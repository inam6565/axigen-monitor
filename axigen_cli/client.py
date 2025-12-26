# axigen_cli/client.py

import socket
from typing import List


class AxigenCLIError(Exception):
    """Generic Axigen CLI error."""


class AxigenCLIClient:
    def __init__(self, host: str, port: int = 7000, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None

    # ---------- connection / login ----------

    def connect(self) -> None:
        """Open TCP connection to Axigen CLI."""
        self._sock = socket.create_connection((self.host, self.port), self.timeout)
        self._sock.settimeout(self.timeout)
        # read banner / welcome text (we don't really need it)
        _ = self._recv_all()

    def close(self) -> None:
        if self._sock:
            try:
                self.send_line("QUIT")
            except Exception:
                pass
            try:
                self._sock.close()
            finally:
                self._sock = None

    def login(self, username: str, password: str) -> None:
        """
        Login to Axigen CLI.

        Typical sequence (when using telnet) is:
            USER <user>
            <server asks for password>
            <you type password>

        We emulate that here.
        """
        if not self._sock:
            raise AxigenCLIError("Not connected")

        # Send username
        self.send_line(f"USER {username}")
        resp = self._recv_all()

        # Axigen usually prompts for password after USER; we just send it
        self.send_line(password)
        resp += self._recv_all()

        if "invalid" in resp.lower() or "failed" in resp.lower():
            raise AxigenCLIError(f"Login failed: {resp.strip()}")

    # ---------- command helpers ----------

    def send_line(self, line: str) -> None:
        if not self._sock:
            raise AxigenCLIError("Not connected")
        data = (line + "\r\n").encode("utf-8", errors="ignore")
        self._sock.sendall(data)

    def run_command(self, command: str) -> str:
        """
        Send a single CLI command and return raw response as text.
        We read until no more data arrives within 'timeout'.
        """
        self.send_line(command)
        return self._recv_all()

    def _recv_all(self) -> str:
        """
        Read data until there's a timeout or the server stops sending.
        For simple one-shot commands like LIST domains this is usually enough.
        """
        if not self._sock:
            raise AxigenCLIError("Not connected")

        chunks: List[bytes] = []
        while True:
            try:
                chunk = self._sock.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            chunks.append(chunk)
            # heuristic: if we got less than buffer size, likely end of response
            if len(chunk) < 4096:
                break
        
        return b"".join(chunks).decode("utf-8", errors="ignore")

    # context manager support
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
