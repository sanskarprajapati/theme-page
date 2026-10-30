"""Video slides: any slide containing a .vslot element renders to MP4 instead of JPG.

The page is screenshotted with a transparent background (video slots are see-through holes), Chrome
dumps each slot's on-screen box, and ffmpeg lays the clips into those boxes underneath the overlay.
Round slots (border-radius:50%) are masked to a circle. Clips shorter than the slide loop.
The page is shot twice (without and with only .front elements) so clips can sit between the two:
backdrop clips, back page, inset clips (data-layer=over), cut-out subjects (data-layer=fg), front page.
"""
import json
import pathlib
import re
import subprocess
import tempfile

MAX_SECONDS = 120  # hard cap: no slide video longer than 2 minutes
FPS = 30

# Fits [data-fit] text to its pixel budget, then writes every .vslot box into #vrects for --dump-dom.
PAGE_SCRIPT = """
<script>
document.fonts.ready.then(() => {
  document.querySelectorAll('[data-fit]').forEach(el => {
    let s = parseFloat(getComputedStyle(el).fontSize);
    while (el.offsetHeight > +el.dataset.fit && s > 36) { s -= 2; el.style.fontSize = s + 'px'; }
  });
  const slots = [...document.querySelectorAll('.vslot')].map(el => {
    const r = el.getBoundingClientRect();
    return {x: r.left, y: r.top, w: r.width, h: r.height, ...el.dataset,
            round: getComputedStyle(el).borderRadius.startsWith('50%')};
  });
  const out = document.createElement('pre');
  out.id = 'vrects'; out.style.display = 'none'; out.textContent = JSON.stringify(slots);
  document.body.appendChild(out);
});
</script>"""


def _even(v):
    return max(2, int(round(v / 2)) * 2)


def _probe(src):
    res = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                          "-of", "json", str(src)], check=True, capture_output=True, text=True)
    info = json.loads(res.stdout)
    return float(info["format"]["duration"]), any(s["codec_type"] == "audio" for s in info["streams"])


def _slots(chrome, page):
    dom = subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--virtual-time-budget=6000",
                          "--allow-file-access-from-files", "--dump-dom", page.resolve().as_uri()],
                         check=True, capture_output=True, text=True).stdout
    found = re.search(r'<pre id="vrects"[^>]*>(.*?)</pre>', dom, re.S)
    if not found:
        raise RuntimeError(f"{page.name}: slot boxes not found in DOM dump (fonts or script failed to load)")
    slots = json.loads(found.group(1).replace("&quot;", '"').replace("&amp;", "&"))
    for s in slots:
        src = (page.parent / s["src"]).resolve()
        if not src.exists():
            raise FileNotFoundError(f"{page.name}: video not found: {src}")
        length, has_audio = _probe(src)
        start = float(s.get("start") or 0)
        dur = float(s["dur"]) if s.get("dur") else length - start
        if dur > MAX_SECONDS:
            raise ValueError(f"{page.name}: {src.name} runs {dur:.0f}s; trim it to {MAX_SECONDS}s or less "
                             f"with dur=")
        s.update(src=src, start=start, dur=min(dur, length - start), has_audio=has_audio)
    return slots


def _trim(slot, tmp, i):
    """Cut the clip window first so looping restarts at `start`, not at the top of the file.
    Alpha clips (cutout.cut_video output) are already cut to their window and must keep their alpha."""
    if slot["src"].suffix == ".mov" and slot["start"] == 0:
        return slot["src"]
    out = tmp / f"clip{i}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{slot['start']}", "-t", f"{slot['dur']}",
                    "-i", str(slot["src"]), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                    "-c:a", "aac", str(out)], check=True)
    return out


def _clip_filter(i, s):
    w, h = _even(s["w"]), _even(s["h"])
    px, py = (float(p.strip("%")) / 100 for p in (s.get("pos") or "50% 50%").split())
    z = float(s.get("zoom") or 1)
    chain = (f"[{i}:v]fps={FPS},scale={_even(w * z)}:{_even(h * z)}:force_original_aspect_ratio=increase,"
             f"crop={w}:{h}:(iw-{w})*{px}:(ih-{h})*{py},setsar=1,format=rgba")
    if s["round"]:
        chain += (",geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                  "a='if(lte(hypot(X-W/2,Y-H/2),W/2),255,0)'")
    return chain + f"[v{i}]"


def _overlays(chrome, page, size, tmp):
    """Two transparent screenshots: everything except .front elements, then only the .front ones."""
    html = page.read_text()
    shots = []
    for name, css in (("back", ".front{visibility:hidden!important}"),
                      ("front", "body *{visibility:hidden!important}.front,.front *{visibility:visible!important}")):
        variant = page.with_name(f"{page.stem}-{name}.html")
        variant.write_text(html.replace("</head>", f"<style>{css}</style></head>"))
        png = tmp / f"{name}.png"
        subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--default-background-color=00000000", f"--window-size={size[0]},{size[1]}",
                        "--virtual-time-budget=6000", "--allow-file-access-from-files",
                        f"--screenshot={png}", variant.resolve().as_uri()], check=True, capture_output=True)
        variant.unlink()
        shots.append(png)
    return shots


def render(chrome, page, size, mp4, poster):
    """Render one video slide: transparent overlay PNG + ffmpeg composite -> mp4 and a poster jpg."""
    slots = _slots(chrome, page)
    total = max(s["dur"] for s in slots)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        back, front = _overlays(chrome, page, size, tmp)
        inputs, chains = [], []
        for i, s in enumerate(slots):
            inputs += ["-stream_loop", "-1", "-t", f"{total}", "-i", str(_trim(s, tmp, i))]
            chains.append(_clip_filter(i, s))
        n = len(slots)
        inputs += ["-loop", "1", "-t", f"{total}", "-i", str(back), "-loop", "1", "-t", f"{total}", "-i", str(front)]
        graph = [f"color=c=black:s={size[0]}x{size[1]}:r={FPS}:d={total}[l0]", *chains]
        # Back to front: backdrop clips, the page minus .front, inset clips, cut-out subject clips,
        # then the .front layer (fade, headline, footer, arrows) so text always stays on top.
        by_layer = {name: [("v", i) for i, s in enumerate(slots) if (s.get("layer") or "under") == name]
                    for name in ("under", "over", "fg")}
        layers = [*by_layer["under"], ("png", n), *by_layer["over"], *by_layer["fg"], ("png", n + 1)]
        for k, (kind, i) in enumerate(layers):
            pos = "0:0" if kind == "png" else f"{int(slots[i]['x'])}:{int(slots[i]['y'])}"
            graph.append(f"[l{k}][{i}:v]overlay={pos}[l{k + 1}]" if kind == "png"
                         else f"[l{k}][v{i}]overlay={pos}[l{k + 1}]")
        graph.append(f"[l{len(layers)}]format=yuv420p[out]")
        voice = next((i for i, s in enumerate(slots) if s.get("audio") == "1" and s["has_audio"]), None)
        audio = ["-map", f"{voice}:a", "-c:a", "aac", "-b:a", "160k"] if voice is not None else ["-an"]
        subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(graph),
                        "-map", "[out]", *audio, "-t", f"{total}", "-r", str(FPS), "-c:v", "libx264",
                        "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        str(mp4)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{min(1.0, total / 2)}", "-i", str(mp4),
                    "-frames:v", "1", "-q:v", "3", str(poster)], check=True)
    return total
