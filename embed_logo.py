# این اسکریپت رو یه بار اجرا کن
# فایل لوگو رو کنار این اسکریپت بذار با اسم: logo.png
# بعد: python embed_logo.py

import base64
import os

logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
frame_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plant_frame.py")

if not os.path.exists(logo_path):
    print("ERROR: logo.png پیدا نشد")
    print("لوگو رو با اسم logo.png کنار این فایل بذار")
    exit()

with open(logo_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

with open(frame_path, "r", encoding="utf-8") as f:
    content = f.read()

if 'LOGO_BASE64 = ""' not in content:
    print("ERROR: خط LOGO_BASE64 پیدا نشد توی plant_frame.py")
    exit()

content = content.replace('LOGO_BASE64 = ""', f'LOGO_BASE64 = "{b64}"')

with open(frame_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ لوگو embed شد")
print("حالا plant_frame.py رو اجرا کن")
