# client.py

import socket
import threading
import json
import base64
import sys
import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = "127.0.0.1"
PORT = 5555

username = sys.argv[1]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# =====================================
# RSA KEYS
# =====================================

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

# Store all peer public keys
peer_keys = {}

# =====================================
# GROUP ENCRYPTION
# =====================================

def encrypt_group_message(message):

    # ONE AES key for everyone
    aes_key = AESGCM.generate_key(bit_length=128)

    aesgcm = AESGCM(aes_key)

    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(
        nonce,
        message.encode(),
        None
    )

    encrypted_keys = {}

    # Encrypt AES key separately for each user
    for user, pubkey in peer_keys.items():

        encrypted_key = pubkey.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        encrypted_keys[user] = (
            base64.b64encode(encrypted_key).decode()
        )

    # Also encrypt for self
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    encrypted_keys[username] = (
        base64.b64encode(encrypted_key).decode()
    )

    return {
        "type": "group_message",
        "from": username,
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "keys": encrypted_keys
    }


def decrypt_group_message(packet):

    # Get OUR encrypted AES key
    encrypted_key = base64.b64decode(
        packet["keys"][username]
    )

    nonce = base64.b64decode(packet["nonce"])

    ciphertext = base64.b64decode(
        packet["ciphertext"]
    )

    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    aesgcm = AESGCM(aes_key)

    plaintext = aesgcm.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext.decode()

# =====================================
# RECEIVE THREAD
# =====================================

def receive():

    while True:

        try:
            data = client.recv(65536)

            packet = json.loads(data.decode())

            # PUBLIC KEY EXCHANGE
            if packet["type"] == "public_key":

                sender = packet["username"]

                if sender != username:

                    peer_keys[sender] = (
                        serialization.load_pem_public_key(
                            packet["key"].encode()
                        )
                    )

                    print(f"[+] {sender} joined")

            # GROUP MESSAGE
            elif packet["type"] == "group_message":

                # Ignore if no encrypted key for us
                if username not in packet["keys"]:
                    continue

                msg = decrypt_group_message(packet)

                print(f"\n[{packet['from']}] {msg}")

        except Exception as e:
            print("Receive error:", e)
            break

threading.Thread(
    target=receive,
    daemon=True
).start()

# =====================================
# SEND PUBLIC KEY
# =====================================

public_packet = {
    "type": "public_key",
    "username": username,
    "key": public_pem
}

client.sendall(
    json.dumps(public_packet).encode()
)

print(f"Connected as {username}")

# =====================================
# CHAT LOOP
# =====================================

while True:

    msg = input()

    packet = encrypt_group_message(msg)

    client.sendall(
        json.dumps(packet).encode()
    )
