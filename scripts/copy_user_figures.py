import shutil
from pathlib import Path

src_hk231 = Path(r"C:/Users/Vy Khang/.gemini/antigravity/brain/05c3c75a-68cc-4c74-b635-9b1abcc723f1/.user_uploaded/media_1795507724849_b6ff111b.png")
dst_hk231 = Path(r"d:/pps/numerical-methods-web/public/images/hk231_fig_1.png")

src_hk241 = Path(r"C:/Users/Vy Khang/.gemini/antigravity/brain/05c3c75a-68cc-4c74-b635-9b1abcc723f1/.user_uploaded/media_1795507319939_508db243.png")
dst_hk241 = Path(r"d:/pps/numerical-methods-web/public/images/hk241_fig_2_beam.png")

shutil.copy2(src_hk231, dst_hk231)
print(f"Copied HK231 Fig 1 ({dst_hk231.stat().st_size} bytes)")

shutil.copy2(src_hk241, dst_hk241)
print(f"Copied HK241 Fig 2 ({dst_hk241.stat().st_size} bytes)")
