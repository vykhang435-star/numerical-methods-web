from pathlib import Path

imgs = list(Path("public/images").glob("logan_fig_p4_*_beam.png"))
print(f"Total Logan Ch4 beam figures in public/images: {len(imgs)}")
for img in sorted(imgs):
    print(" ", img.name, f"({img.stat().st_size} bytes)")
