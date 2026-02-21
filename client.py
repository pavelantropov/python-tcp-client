#!/usr/bin/env python3

import socket


def tcp_client():
    s = None
    try:
        print("TCP client started")
        s, port = connect_to_server()
        buffer = ""

        while True:
            msg = input("[CLIENT] Enter message: ")
            if not msg:
                continue

            s.sendall((msg + "\n").encode("utf-8"))

            while True:
                data = s.recv(1024)
                if not data:
                    print("[CLIENT] Server closed connection")
                    return

                buffer += data.decode("utf-8")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        print(f"[SERVER] {line}")

                if len(data) < 1024:
                    break

    except ConnectionRefusedError:
        print(f"[CLIENT] Error: Server is not running on port {port}")
    except socket.timeout:
        print("[CLIENT] Error: Connection timeout")
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
    finally:
        if s:
            s.close()
        print("[CLIENT] Disconnected from server")


def connect_to_server() -> tuple[socket.socket, int]:
    address = input("Enter address to connect to: ")
    port = int(input("Enter port to use: "))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    s.connect((address, port))
    print("[CLIENT] Connected to server")
    return s, port


if __name__ == "__main__":
    tcp_client()
