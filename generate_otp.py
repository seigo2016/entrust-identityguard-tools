#!/bin/env python3
from hashlib import pbkdf2_hmac
import logging
import subprocess

logging.basicConfig(level=logging.WARNING)
policy=""
def generate_otp(serial, activationCode, registrationCode):
    # Remove dashes from input so we can work with the data
    serial = serial.replace("-", "")
    activation = activationCode.replace("-", "")
    registration = registrationCode.replace("-", "")

    # TODO: Validate all values through the Luhn check digits

    activation = activation[0:-1] # remove last digit -- check digit
    activationbytes = int(activation).to_bytes(7, byteorder='big')
    logging.info("Activation bytes: 0x%s", activationbytes.hex())

    registration = registration[0:-1] # remove last digit -- check digit
    registrationbytes = int(registration).to_bytes(4, byteorder='big')
    logging.info("Registration bytes: 0x%s", registrationbytes.hex())

    # Derive the RNG output from the registration bytes
    # Remaining bits are used for validation, but we can ignore that in our case
    rngbytes = registrationbytes[-2:]

    logging.info("RNG Bytes: 0x%s", rngbytes.hex())

    password = activationbytes + rngbytes

    # The secret may or may not include the policy
    if policy is not None:
        password += policy.encode('utf-8')
        logging.info("Policy: %s", policy.encode('utf-8'))
    else:
        logging.debug("Policy not provided")

    # Derive the secret key
    key = pbkdf2_hmac(
        hash_name='sha256',
        password=password,
        salt=serial.encode("utf-8"),
        iterations=8,
        dklen=16
    )

    print(key.hex())
    print("To generate a code immediately, run:")
    print("oathtool -v --totp=sha256 --digits=6 " + key.hex())
    cmd = ['oathtool', '-v', '--totp=sha256', '--digits=6', key.hex()]
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    fa_string = out.stdout.decode()
    return fa_string