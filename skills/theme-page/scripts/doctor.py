"""Check this machine has what theme-page needs. Usage: python3 doctor.py

Required: Python 3.9+, Chrome/Chromium/Edge (renders slides), ffmpeg + ffprobe (JPGs, MP4s).
Optional: yt-dlp (clip posts from links), macOS 14+ with swiftc (subject cut-outs on covers).
Exits 1 when a required tool is missing.
"""
import platform
import shutil
import sys

import cutout
import kit

INSTALL = {
    "chrome": "install Google Chrome (or set THEME_PAGE_CHROME to a Chrome/Chromium binary)",
    "ffmpeg": "macOS: brew install ffmpeg · Linux: sudo apt install ffmpeg",
    "yt-dlp": "macOS: brew install yt-dlp · anywhere: pipx install yt-dlp",
    "cutout": "macOS 14+ only: xcode-select --install",
}


def rows():
    chrome_ok = shutil.which(kit.CHROME) is not None or __import__("pathlib").Path(kit.CHROME).exists()
    return [
        ("python 3.9+", sys.version_info >= (3, 9), True, platform.python_version()),
        ("chrome", chrome_ok, True, kit.CHROME if chrome_ok else INSTALL["chrome"]),
        ("ffmpeg", bool(shutil.which("ffmpeg") and shutil.which("ffprobe")), True, INSTALL["ffmpeg"]),
        ("yt-dlp", shutil.which("yt-dlp") is not None, False, INSTALL["yt-dlp"]),
        ("subject cut-outs", cutout.available(), False, INSTALL["cutout"]),
    ]


def main():
    missing = False
    for name, ok, required, note in rows():
        mark = "ok " if ok else ("MISSING" if required else "off")
        print(f"{mark:8} {name:18} {'' if ok and name != 'chrome' else note}")
        missing |= required and not ok
    print("\nAll required tools found." if not missing else "\nInstall the MISSING tools, then run this again.")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
