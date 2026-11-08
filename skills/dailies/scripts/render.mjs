#!/usr/bin/env node
/*
 * Render an HTML composition (templates/composition contract) to video or stills.
 *
 *   node render.mjs comp/index.html --out renders/v1/video.mp4 [--audio mix.wav]
 *   node render.mjs comp/index.html --stills 1,4.5,9 --still-dir review/frames
 *   node render.mjs comp/index.html --serve
 *
 * The page is served from a local HTTP server (so fetch, fonts and video
 * seeking behave like a real site), opened in headless Chromium through
 * playwright-core, stepped frame by frame with window.__dailies.seek(t), and
 * screenshots are piped straight into ffmpeg.
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const HELP = `Usage: node render.mjs <composition.html> [options]

Output (choose one):
  --out <file>          Render video (.mp4 H.264; .mov ProRes 4444 or .webm VP9 when --alpha)
  --stills <t1,t2,...>  Render PNG stills at these times (seconds)
  --serve               Serve the project for live preview and print the URL

Options:
  --still-dir <dir>     Where stills go (default: ./stills)
  --from <s> --to <s>   Render only this time range
  --fps <n>             Override the composition fps (e.g. 15 for drafts)
  --scale <f>           Pixel scale, e.g. 0.5 for a fast half-size draft
  --alpha               Transparent background (overlays for footage)
  --audio <file>        Mux this audio file into the video
  --crf <n>             H.264 quality, lower is better (default 18)
  --png                 Capture frames as PNG instead of high-quality JPEG (slower, lossless)
  --query "<a=b&c=d>"   Extra URL query for the page (e.g. "bg=../review/bg/t2.00.png")
  --root <dir>          Directory to serve (default: the composition folder's parent)
  --browser <name>      chrome | msedge | chromium (default: first that works)
  --port <n>            Port for --serve (default: random)
`;

function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (!k.startsWith("--")) { a._.push(k); continue; }
    const key = k.slice(2);
    const flag = ["alpha", "serve", "png", "help"].includes(key);
    a[key] = flag ? true : argv[++i];
  }
  return a;
}

const args = parseArgs(process.argv.slice(2));
if (args.help || !args._[0]) { console.log(HELP); process.exit(args.help ? 0 : 1); }

const htmlPath = path.resolve(args._[0]);
if (!fs.existsSync(htmlPath)) { console.error(`Not found: ${htmlPath}`); process.exit(1); }
const root = path.resolve(args.root || path.dirname(path.dirname(htmlPath)));
const relHtml = path.relative(root, htmlPath).split(path.sep).join("/");
if (relHtml.startsWith("..")) { console.error("--root must contain the composition"); process.exit(1); }

// ------------------------------------------------------------------ static server
const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".webp": "image/webp", ".gif": "image/gif", ".avif": "image/avif", ".mp4": "video/mp4", ".webm": "video/webm",
  ".mov": "video/quicktime", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4", ".ttf": "font/ttf",
  ".otf": "font/otf", ".woff": "font/woff", ".woff2": "font/woff2", ".txt": "text/plain", ".vtt": "text/vtt",
};

function serve(port = 0) {
  const server = http.createServer((req, res) => {
    const urlPath = decodeURIComponent(new URL(req.url, "http://x").pathname);
    if (urlPath === "/favicon.ico") { res.writeHead(204).end(); return; }
    const file = path.join(root, urlPath);
    if (!file.startsWith(root)) { res.writeHead(403).end(); return; }
    fs.stat(file, (err, st) => {
      if (err || !st.isFile()) { res.writeHead(404).end("not found"); return; }
      const type = MIME[path.extname(file).toLowerCase()] || "application/octet-stream";
      const range = req.headers.range && /bytes=(\d*)-(\d*)/.exec(req.headers.range);
      if (range) {
        // Range support matters: video elements seek by requesting byte ranges.
        const start = range[1] ? parseInt(range[1], 10) : 0;
        const end = range[2] ? parseInt(range[2], 10) : st.size - 1;
        res.writeHead(206, { "Content-Type": type, "Content-Range": `bytes ${start}-${end}/${st.size}`, "Accept-Ranges": "bytes", "Content-Length": end - start + 1, "Cache-Control": "no-store" });
        fs.createReadStream(file, { start, end }).pipe(res);
      } else {
        res.writeHead(200, { "Content-Type": type, "Content-Length": st.size, "Accept-Ranges": "bytes", "Cache-Control": "no-store" });
        fs.createReadStream(file).pipe(res);
      }
    });
  });
  return new Promise((resolve) => server.listen(port, "127.0.0.1", () => resolve(server)));
}

if (args.serve) {
  const server = await serve(args.port ? +args.port : 0);
  const url = `http://127.0.0.1:${server.address().port}/${relHtml}`;
  console.log(`Serving ${root}\nPreview: ${url}\nGuides:  ${url}?guides=1\nPress Ctrl+C to stop.`);
  await new Promise(() => {});
}

// ------------------------------------------------------------------ browser
async function loadPlaywright() {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const tries = [
    () => import("playwright-core"),
    () => createRequire(path.join(here, "..", "package.json"))("playwright-core"),
    () => createRequire(path.join(process.cwd(), "package.json"))("playwright-core"),
    () => import("playwright"),
  ];
  for (const t of tries) {
    try { const m = await t(); return m.chromium ? m : m.default; } catch { /* next */ }
  }
  console.error("playwright-core is not installed. Run scripts/doctor.py; it prints the install command for this setup.");
  process.exit(1);
}

async function launch(pw) {
  const order = args.browser ? [args.browser] : ["chrome", "msedge", "chromium"];
  const launchArgs = ["--force-color-profile=srgb", "--hide-scrollbars", "--autoplay-policy=no-user-gesture-required", "--font-render-hinting=none", "--disable-lcd-text"];
  for (const name of order) {
    try {
      const opts = { headless: true, args: launchArgs };
      if (name !== "chromium") opts.channel = name;
      const b = await pw.chromium.launch(opts);
      return { browser: b, name };
    } catch { /* try next */ }
  }
  console.error("No usable browser. Install Chrome or Edge, or run `npx playwright install chromium`.");
  process.exit(1);
}

function buildUrl(base) {
  const q = new URLSearchParams(args.query || "");
  q.set("render", "1");
  if (args.alpha) q.set("alpha", "1");
  return `${base}?${q.toString()}`;
}

async function openPage(browser, url, viewport, scale) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: scale });
  const page = await context.newPage();
  page.on("pageerror", (e) => console.error(`[page error] ${e.message}`));
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") console.error(`[page ${m.type()}] ${m.text()}`); });
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => window.__dailies && window.__dailies.ready, null, { timeout: 30000 });
  await page.evaluate(() => window.__dailies.ready);
  return { context, page };
}

function ffmpegArgs(meta, fps, outFile, imgCodec) {
  const a = ["-y", "-hide_banner", "-loglevel", "error", "-f", "image2pipe", "-c:v", imgCodec, "-framerate", String(fps), "-i", "-"];
  if (args.audio) {
    a.push("-ss", String(args.from || 0), "-i", path.resolve(args.audio));
  }
  const ext = path.extname(outFile).toLowerCase();
  if (args.alpha && ext === ".webm") {
    a.push("-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-row-mt", "1");
  } else if (args.alpha) {
    a.push("-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0");
  } else {
    // JPEG frames decode as full-range BT.601; convert explicitly to the limited-range
    // BT.709 every player and platform expects, and tag the stream so colors stay put.
    const inRange = imgCodec === "mjpeg" ? ":in_range=full:in_color_matrix=bt601" : "";
    a.push("-vf", `scale=trunc(iw/2)*2:trunc(ih/2)*2${inRange}:out_range=tv:out_color_matrix=bt709,format=yuv420p`,
      "-c:v", "libx264", "-preset", "medium", "-crf", String(args.crf || 18), "-pix_fmt", "yuv420p",
      "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart");
  }
  if (args.audio) a.push("-map", "0:v", "-map", "1:a", "-c:a", ext === ".webm" ? "libopus" : "aac", "-b:a", "192k", "-shortest");
  a.push("-r", String(fps), outFile);
  return a;
}

// ------------------------------------------------------------------ main
const server = await serve();
const base = `http://127.0.0.1:${server.address().port}/${relHtml}`;
const pw = await loadPlaywright();
const { browser, name } = await launch(pw);

let exitCode = 0;
try {
  // first pass: read size/fps/duration
  const probe = await openPage(browser, buildUrl(base), { width: 1280, height: 720 }, 1);
  const meta = await probe.page.evaluate(() => ({ width: __dailies.width, height: __dailies.height, fps: __dailies.fps, duration: __dailies.duration }));
  await probe.context.close();

  const scale = args.scale ? parseFloat(args.scale) : 1;
  const { context, page } = await openPage(browser, buildUrl(base), { width: meta.width, height: meta.height }, scale);
  const usePng = args.png || args.alpha || args.stills;
  const shot = () => page.screenshot({ type: usePng ? "png" : "jpeg", quality: usePng ? undefined : 95, omitBackground: !!args.alpha, animations: "allow", caret: "initial" });

  if (args.stills) {
    const dir = path.resolve(args["still-dir"] || "stills");
    fs.mkdirSync(dir, { recursive: true });
    const times = String(args.stills).split(",").map((s) => parseFloat(s.trim())).filter((n) => !Number.isNaN(n));
    for (const t of times) {
      await page.evaluate((tt) => window.__dailies.seek(tt), t);
      const file = path.join(dir, `t${t.toFixed(2)}.png`);
      fs.writeFileSync(file, await shot());
      console.log(file);
    }
  } else if (args.out) {
    const fps = args.fps ? parseFloat(args.fps) : meta.fps;
    const from = args.from ? parseFloat(args.from) : 0;
    const to = Math.min(args.to ? parseFloat(args.to) : meta.duration, meta.duration);
    const first = Math.round(from * fps), last = Math.round(to * fps);
    const total = last - first;
    const outFile = path.resolve(args.out);
    fs.mkdirSync(path.dirname(outFile), { recursive: true });

    const ff = spawn("ffmpeg", ffmpegArgs(meta, fps, outFile, usePng ? "png" : "mjpeg"), { stdio: ["pipe", "inherit", "inherit"] });
    const ffDone = new Promise((res, rej) => { ff.on("error", rej); ff.on("close", (c) => (c === 0 ? res() : rej(new Error(`ffmpeg exited with ${c}`)))); });
    const write = (buf) => new Promise((res) => (ff.stdin.write(buf) ? res() : ff.stdin.once("drain", res)));

    console.log(`Rendering ${total} frames (${meta.width * scale}x${meta.height * scale} @ ${fps} fps, ${from}s-${to}s) with ${name}`);
    const started = Date.now();
    for (let f = first; f < last; f++) {
      await page.evaluate((tt) => window.__dailies.seek(tt), f / fps);
      await write(await shot());
      const done = f - first + 1;
      if (done % 30 === 0 || done === total) {
        const el = (Date.now() - started) / 1000;
        const eta = (el / done) * (total - done);
        process.stdout.write(`\r  ${done}/${total} frames  ${(done / el).toFixed(1)} fps  eta ${eta.toFixed(0)}s   `);
      }
    }
    ff.stdin.end();
    await ffDone;
    console.log(`\nWrote ${outFile}`);
  } else {
    console.error("Nothing to do: pass --out, --stills or --serve.");
    exitCode = 1;
  }
  await context.close();
} catch (e) {
  console.error(e.stack || String(e));
  exitCode = 1;
} finally {
  await browser.close();
  server.close();
}
process.exit(exitCode);
