import decode_qr_uri as dqr
import generate_otp as gotp
import json
from pyzbar.pyzbar import decode
from PIL import Image

# Load QR code
d = decode(Image.open("qr.bmp"))

URI = d[0].data.decode("utf-8")
# Input user auth data
PASSWORD = input("QRコードパスワードを入力してください > ")
REGISTRATION_CODE = input("登録コードを入力してください > ")
# Decode QR code

data = dqr.decode_qr(URI, PASSWORD)
data = json.loads(data)

SN = data["sn"]
AC = data["ac"]

result = gotp.generate_otp(SN, AC, REGISTRATION_CODE)
print(result)