#!/usr/bin/env python3

import signal
import socket
import sys
import threading

DEFAULT_ADDRESS = "localhost"
DEFAULT_PORT = 8888
DEFAULT_TIMEOUT = 5.0
CONNECTION_TIMEOUT = 2.0
BUFFER_SIZE = 1024
EXIT_COMMANDS = {"quit", "q"}


def main() -> None:
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

    try:
        tcp_client()
    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user")
        sys.exit(0)


def tcp_client():
    s = None
    try:
        print("TCP client started (type quit or q to exit)")

        address, port = get_connection_params()
        s = connect(address, port)
        if not s:
            return

        connection_closed = threading.Event()
        readerThread = threading.Thread(
            target=reader, args=(s, connection_closed), daemon=True
        )
        senderThread = threading.Thread(
            target=sender, args=(s, connection_closed), daemon=True
        )
        readerThread.start()
        senderThread.start()

        readerThread.join()
        senderThread.join()

    except (BrokenPipeError, ConnectionResetError):
        print("[CLIENT] Connection lost")
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
    finally:
        close_socket(s)
        print("[CLIENT] Disconnected from server")


def get_connection_params() -> tuple[str, int]:
    address = (
        input("Enter address to connect to (default=localhost): ").strip()
        or DEFAULT_ADDRESS
    )

    port = input("Enter port to use (default=8888): ").strip()
    port = int(port) if port else DEFAULT_PORT

    return address, port


def connect(address: str, port: int) -> socket.socket | None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.settimeout(CONNECTION_TIMEOUT)
        s.connect((address, port))
        print("[CLIENT] Connected to server")
        s.settimeout(DEFAULT_TIMEOUT)
        return s

    except ConnectionRefusedError:
        print(f"[CLIENT] Error: Server is not running on port {port}")
    except socket.timeout:
        print("[CLIENT] Error: Connection timeout")

    return None


def sender(s: socket.socket, connection_closed: threading.Event) -> None:
    try:
        while not connection_closed.is_set():
            msg = input("[CLIENT] Enter message: ")
            if not msg:
                continue

            if msg.lower() in EXIT_COMMANDS:
                print("[CLIENT] Disconnecting...")
                return

            s.sendall((msg + "\n").encode("utf-8"))

    except socket.timeout:
        print("[CLIENT] Error: Server timeout")
    finally:
        connection_closed.set()


def reader(s: socket.socket, connection_closed: threading.Event) -> None:
    buffer = ""

    try:
        while not connection_closed.is_set():
            try:
                data = s.recv(1024)
            except socket.timeout:
                continue

            if not data:
                print("[CLIENT] Server closed connection")
                break

            buffer += data.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line:
                    print(f"\n[SERVER] {line}")
    finally:
        connection_closed.set()


def close_socket(s: socket.socket | None) -> None:
    if s is None:
        return

    try:
        s.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass

    try:
        s.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()
