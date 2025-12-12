import socket
import struct

HOST = "127.0.0.1"
PORT = 5432

# Minimal Postgres StartupMessage (protocol 3.0)
def startup_message(user="axigen_user", database="axigen_db"):
    params = (
        b"user\x00" + user.encode() + b"\x00" +
        b"database\x00" + database.encode() + b"\x00" +
        b"\x00"
    )
    length = 4 + 4 + len(params)
    return struct.pack("!I", length) + struct.pack("!I", 196608) + params  # 196608 = 3<<16

s = socket.socket()
s.settimeout(5)
print("[SOCKET] connecting...")
s.connect((HOST, PORT))
print("[SOCKET] connected, sending startup packet...")
s.sendall(startup_message())

print("[SOCKET] waiting for response...")
data = s.recv(64)
print("[SOCKET] first bytes:", data)
s.close()
