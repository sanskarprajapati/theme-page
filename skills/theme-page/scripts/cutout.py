"""Background-removed copies of photos and clips, for the subject-in-front-of-logos cover effect.

cut_image() writes an RGBA PNG; cut_video() writes a QuickTime Animation (.mov) clip with alpha covering
exactly [start, start + dur] of the source. Results are cached next to the source in a cut/ folder and
rebuilt only when the source is newer. The Swift tool is compiled once into .bin/.
"""
import pathlib
import platform
import shutil
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / ".bin" / "cutout"


def available():
    """Apple Vision does the matting, so cut-outs need macOS 14+ and swiftc (Xcode command line tools)."""
    if platform.system() != "Darwin" or _macos_major() < 14:
        return False
    return TOOL.exists() or shutil.which("swiftc") is not None


def _macos_major():
    """platform.mac_ver() is empty in some Python builds, so fall back to sw_vers; unknown counts as new."""
    version = platform.mac_ver()[0]
    if not version:
        try:
            version = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True).stdout.strip()
        except OSError:
            version = ""
    return int(version.split(".")[0]) if version.split(".")[0].isdigit() else 99


def _tool():
    src = HERE / "cutout.swift"
    if not TOOL.exists() or TOOL.stat().st_mtime < src.stat().st_mtime:
        TOOL.parent.mkdir(exist_ok=True)
        subprocess.run(["swiftc", "-O", str(src), "-o", str(TOOL)], check=True)
    return str(TOOL)


def _fresh(out, src):
    return out.exists() and out.stat().st_mtime >= src.stat().st_mtime


def cut_image(src, keep_all=False):
    """keep_all=False keeps only the largest subject, dropping bystanders."""
    src = pathlib.Path(src).resolve()
    out = src.parent / "cut" / f"{src.stem}{'-all' if keep_all else ''}.png"
    if not _fresh(out, src):
        out.parent.mkdir(exist_ok=True)
        subprocess.run([_tool(), str(src), str(out), *(["--all"] if keep_all else [])], check=True)
    return out


def cut_video(src, start, dur, fps=30, height=1440, keep_all=False):
    src = pathlib.Path(src).resolve()
    out = src.parent / "cut" / f"{src.stem}-{start:g}-{dur:g}{'-all' if keep_all else ''}.mov"
    if _fresh(out, src):
        return out
    out.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        frames, masked = pathlib.Path(td) / "f", pathlib.Path(td) / "m"
        frames.mkdir()
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start}", "-t", f"{dur}", "-i", str(src),
                        "-vf", f"fps={fps},scale=-2:{height}", str(frames / "%05d.png")], check=True)
        subprocess.run([_tool(), str(frames), str(masked), *(["--all"] if keep_all else [])], check=True)
        tmp = pathlib.Path(td) / "out.mov"
        subprocess.run(["ffmpeg", "-v", "error", "-framerate", str(fps), "-i", str(masked / "%05d.png"),
                        "-c:v", "qtrle", "-pix_fmt", "argb", str(tmp)], check=True)
        shutil.move(tmp, out)
    return out
