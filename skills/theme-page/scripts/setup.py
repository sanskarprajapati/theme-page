"""Create or update theme-page.json for a page.

Usage:
  python3 setup.py --dir <workspace> --niche "AI and tech" --handle @mypage --name "My Page" \
      --account instagram=https://instagram.com/mypage --account x=https://x.com/mypage \
      --palette electric-cyan            # or --accent "#33CCFF" for a custom color
  Optional: --badge <logo file or image URL> --monogram MP
The logo is copied into <workspace>/brand/ so the workspace is self-contained.
Only the flags you pass are changed; everything else in an existing file is kept.
"""
import argparse
import json
import pathlib
import re
import shutil
import sys
import urllib.request

import config


def parse(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=".", help="workspace folder that will hold theme-page.json and carousels/")
    ap.add_argument("--niche")
    ap.add_argument("--handle")
    ap.add_argument("--name")
    ap.add_argument("--account", action="append", default=[], metavar="PLATFORM=URL")
    ap.add_argument("--palette", choices=sorted(config.PALETTES))
    ap.add_argument("--accent", help="custom accent hex, e.g. #33CCFF")
    ap.add_argument("--badge", help="the page's logo (file path or image URL); shown in the badge and on clip posts")
    ap.add_argument("--monogram", help="1-3 letters shown in the badge when there is no logo")
    return ap.parse_args(argv)


def save_logo(src, workspace):
    """Copy or download the logo into <workspace>/brand/ and return its workspace-relative path."""
    brand_dir = workspace / "brand"
    brand_dir.mkdir(parents=True, exist_ok=True)
    if src.startswith("http"):
        ext = pathlib.Path(src.split("?")[0]).suffix.lower() or ".png"
        dest = brand_dir / f"logo{ext if ext in ('.png', '.jpg', '.jpeg', '.webp', '.svg') else '.png'}"
        req = urllib.request.Request(src, headers={"User-Agent": "theme-page-skill"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
    else:
        path = pathlib.Path(src).expanduser().resolve()
        if not path.exists():
            sys.exit(f"logo not found: {path}")
        dest = brand_dir / f"logo{path.suffix.lower()}"
        if path != dest:
            shutil.copyfile(path, dest)
    return str(dest.relative_to(workspace))


def apply(data, args, workspace):
    out = json.loads(json.dumps(data))
    if args.niche:
        out["niche"] = args.niche.strip()
    brand = out.setdefault("brand", {})
    if args.handle:
        brand["handle"] = "@" + args.handle.strip().lstrip("@")
    if args.name:
        brand["name"] = args.name.strip()
    if args.monogram:
        brand["monogram"] = args.monogram.strip()[:3].upper()
    elif args.name and not brand.get("monogram"):
        brand["monogram"] = "".join(w[0] for w in args.name.split()[:2]).upper()
    if args.badge:
        brand["badge"] = save_logo(args.badge, workspace)
    for item in args.account:
        platform, sep, url = item.partition("=")
        if not sep or not url.startswith("http"):
            sys.exit(f"--account needs PLATFORM=URL, got: {item}")
        out.setdefault("accounts", {})[platform.strip().lower()] = url.strip()
    if args.palette:
        out["theme"] = {"palette": args.palette, **config.PALETTES[args.palette]}
    if args.accent:
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", args.accent):
            sys.exit(f"--accent must look like #33CCFF, got: {args.accent}")
        out["theme"] = {"palette": "custom", "accent": args.accent.upper(), "label": "Custom"}
    return out


def main(argv=None):
    args = parse(argv)
    path = pathlib.Path(args.dir).expanduser().resolve() / config.NAME
    data = json.loads(path.read_text()) if path.exists() else {}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(apply(data, args, path.parent), indent=2) + "\n")
    print(f"saved {path}")
    print(json.dumps(config.load(path.parent), indent=2))


if __name__ == "__main__":
    main()
