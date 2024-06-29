import socket
import threading
from fastapi import FastAPI

app = FastAPI()

def relay_thread(sock, peer1_addr, peer2_addr):
    while True:
        data, addr = sock.recvfrom(2048)
        if addr == peer1_addr:
            sock.sendto(data, peer2_addr)
        elif addr == peer2_addr:
            sock.sendto(data, peer1_addr)

@app.get("/start_relay_server")
def start_relay_server(port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"Relay server started on port {port}")

    peer1_addr = None
    peer2_addr = None

    def listen():
        nonlocal peer1_addr, peer2_addr
        while True:
            data, addr = sock.recvfrom(2048)
            if peer1_addr is None:
                peer1_addr = addr
                print(f"Peer 1 connected: {peer1_addr}")
            elif peer2_addr is None:
                peer2_addr = addr
                print(f"Peer 2 connected: {peer2_addr}")
                threading.Thread(target=relay_thread, args=(sock, peer1_addr, peer2_addr)).start()
            else:
                sock.sendto(b"Server is busy, try again later", addr)

    threading.Thread(target=listen).start()
    return {"status": "Relay server started", "port": port}
