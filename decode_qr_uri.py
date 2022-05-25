#!/bin/env python3
import urllib.parse
import hmac
import hashlib
from hashlib import pbkdf2_hmac
import base64
import logging
from Crypto.Cipher import AES

def decode_qr(URI, PASSWORD):
    # Parse URL
    o = urllib.parse.urlparse(URI)

    # Validate scheme
    if o.scheme != 'igmobileotp':
        logging.warning("Only the scheme igmobileotp is currently supported")

    logging.info("Scheme: %s", o.scheme)

    # Parse query string
    query = urllib.parse.parse_qs(o.query)

    # Validate action
    try:
        if query['action'][0] != 'secactivate':
            logging.warning("Only the secactivate action is currently supported")
        logging.info("Action: %s", query['action'][0])
    except:
        logging.warning("No action was found in the URI. Are you sure this is from a valid QR code?")

    # Validate some encrypted data actually exists
    enc = False
    try:
        enc = query['enc'][0]
    except:
        raise Exception('An "enc" parameter is a required part of the URI')

    # Decode the enc parameter from base64
    try:
        enc = base64.b64decode(enc, validate=True)
    except:
        raise Exception('Could not decode base64 from enc paramater')

    # Get the salt from enc
    kdfSalt = enc[0:8]

    logging.debug("KDF Salt: 0x%s", kdfSalt.hex())

    # Run PBKDF2 to obtain our AES key
    key = pbkdf2_hmac(
        hash_name='sha256',
        password=PASSWORD.encode('utf-8'),
        salt=kdfSalt,
        iterations=1000,
        dklen=64
    )

    logging.debug("KDF Output: 0x%s", key.hex())

    # Validate whether our key is correct using the provided MAC
    # The MAC'd payload does not include the MAC itself
    macedPayload = o.query[0:o.query.rfind('&')] # mac is last param, so can remove it this way

    hmacKey = key[16:48]
    logging.debug("HMAC Key: 0x%s", hmacKey.hex())

    hmacer = hmac.new(hmacKey, digestmod=hashlib.sha256)
    hmacer.update(macedPayload.encode('utf-8'))
    hmacDigest = hmacer.digest()

    logging.info('HMAC Digest: 0x%s', hmacDigest.hex())

    try:
        mac = query['mac'][0]
        if base64.b64decode(mac) != hmacDigest[0:12]:
            logging.warning("Falied to validate HMAC. Are you use this passcode is correct?")
    except:
        logging.warning("No MAC was provided in URI. Cannot verify if key is correct")

    # Remove the KDF salt from the encrypted data
    encdata = enc[8:]

    # Get our parameters required for decryption
    iv = key[48:]
    aesKey = key[0:16]

    logging.debug("IV: 0x%s", iv.hex())
    logging.debug("AES Key: 0x%s", aesKey.hex())

    # custom unpad, as pycrytodome does not support pkcs5
    unpad = lambda s: s[0:-(s[-1])]

    cipher = AES.new(aesKey, mode=AES.MODE_CBC, iv=iv)
    decrypted_data = unpad(cipher.decrypt(encdata))

    # print(decrypted_data.decode("utf-8"))

    return decrypted_data.decode("utf-8")