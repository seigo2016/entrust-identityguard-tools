import decode_qr_uri as dqr
import generate_otp as gotp
import json
from pyzbar.pyzbar import decode
from PIL import Image

# Load QR code
d = decode(Image.open("code.dib"))
URI = d[0].data.decode("utf-8")

# Input user auth data
PASSWORD = input("Enter your password. \n(The password given with the QR code. Example: 54998317)\n>")
REGISTRATION_CODE = input("Enter your registration code.\n(The user provides this to the activation service. Example: 12211-49352)\n>")

# Decode QR code
data = dqr.decode_qr(URI, PASSWORD)
data = json.loads(data)
SN = data["sn"]
AC = data["ac"]

result = gotp.generate_otp(SN, AC, REGISTRATION_CODE)
print(result)