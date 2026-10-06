"""Build the web-sized media in public/media from the original project folders.

Run from the site root:  python scripts/prep-media.py
Needs Pillow and ffmpeg. Safe to re-run; it only writes into public/media.
"""
import shutil
import subprocess
from pathlib import Path

from PIL import Image

DOWNLOADS = Path.home() / "Downloads"
REPO = DOWNLOADS / "cafe-racer-concept"
PORTFOLIO = DOWNLOADS / "Portfolio_Images"
FRAMES = DOWNLOADS / "final_frames"
NAVI = DOWNLOADS / "NAVI"
OUT = Path(__file__).resolve().parent.parent / "public" / "media"


def webp(src: Path, dst: Path, width: int, quality: int = 82) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=6)
    print(f"{dst.relative_to(OUT)}  {im.width}x{im.height}  {dst.stat().st_size // 1024} KB")


def hero_loop() -> None:
    """Explode sequence from the raw farm frames, played forward then reversed so it loops cleanly."""
    first, count = 478, 140
    dst = OUT / "hero-loop.mp4"
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y",
            "-framerate", "24", "-start_number", str(first),
            "-i", str(FRAMES / "frame_%05d.png"), "-frames:v", str(count),
            "-filter_complex",
            "[0:v]scale=1600:-2,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]",
            "-map", "[v]", "-c:v", "libx264", "-preset", "slow", "-crf", "27",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(dst),
        ],
        check=True,
    )
    print(f"hero-loop.mp4  {dst.stat().st_size // 1024} KB")
    webp(FRAMES / f"frame_{first:05d}.png", OUT / "hero-poster.webp", 1600)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hero_loop()

    film = REPO / "media" / "film"
    shutil.copyfile(film / "cafe-racer-concept-1080p.mp4", OUT / "cafe-racer-film.mp4")
    for name in ("hero", "exploded", "night", "finish-green", "finish-black"):
        webp(film / f"{name}.jpg", OUT / "cafe" / f"{name}.webp", 1600)

    renders = REPO / "media" / "renders"
    for name in ("engine", "engineexploded", "clutchhubexploded", "crankshaftside",
                 "shockabsorberexploded", "rearwheelside"):
        webp(renders / f"{name}.jpg", OUT / "cafe" / f"{name}.webp", 1200)

    for png in PORTFOLIO.glob("p*/*.png"):
        group = "wing" if "Aerodynamics" in png.parent.name else "cafe"
        webp(png, OUT / group / f"{png.stem}.webp", 1600, quality=88)

    webp(NAVI / "angleperspectiveview2.png", OUT / "navi" / "navi.webp", 1200)
    webp(NAVI / "handle.png", OUT / "navi" / "handle.webp", 1200)

    # Landscape detail crop of the handle for the work index thumbnail.
    handle = Image.open(NAVI / "handle.png").convert("RGB")
    w, h = handle.size
    crop = handle.crop((0, round(h * 0.16), w, round(h * 0.16) + round(w * 10 / 16)))
    crop = crop.resize((1200, 750), Image.LANCZOS)
    crop.save(OUT / "navi" / "handle-thumb.webp", "WEBP", quality=82, method=6)


if __name__ == "__main__":
    main()
