# server.py

import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5555

clients = []
public_keys = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"[SERVER] Listening on {HOST}:{PORT}")


def broadcast(data, sender=None):
    dead = []

    for client in clients:
        if client != sender:
            try:
                client.sendall(data)
            except:
                dead.append(client)

    for d in dead:
        if d in clients:
            clients.remove(d)


def handle_client(client):
    username = None

    while True:
        try:
            data = client.recv(8192)

            if not data:
                break

            packet = json.loads(data.decode())

            # Handle public key exchange
            if packet["type"] == "public_key":
                username = packet["username"]

                # Save public key
                public_keys[username] = packet

                # Send all existing public keys to new client
                for user, key_packet in public_keys.items():
                    if user != username:
                        client.sendall(json.dumps(key_packet).encode())

                # Broadcast new user's key to everyone else
                broadcast(data, client)

                print(f"[KEY] Stored key for {username}")

            else:
                # Relay encrypted messages
                broadcast(data, client)

        except Exception as e:
            print("Error:", e)
            break

    if client in clients:
        clients.remove(client)

    if username and username in public_keys:
        del public_keys[username]

    client.close()


while True:
    client, addr = server.accept()

    print(f"[NEW CONNECTION] {addr}")

    clients.append(client)

    thread = threading.Thread(
        target=handle_client,
        args=(client,)
    )

    thread.start()
