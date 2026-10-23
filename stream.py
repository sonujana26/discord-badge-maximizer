#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import math
import os
import random
import select
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence

# paths
ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "session.json"
GAMES_FILE = ROOT.parent / "data" / "games.json"

# endpoints
ME_URL = "https://discord.com/api/v9/users/@me?with_analytics_token=true"
USERS_URL = "https://discord.com/api/v9/users"
SCIENCE_URL = "https://discord.com/api/v9/science"
PROPERTIES_URL = "https://cordapi.dolfi.es/api/v2/properties/windows"
GAMES_CDN_URL = "https://cdn.discordapp.com/detectables/games.json"
GATEWAY_URL = "gateway.discord.gg"

# telemetry settings
BATCH_SIZE = 50
BATCH_DELAY = 0.3
AUTH_MAX_AGE = 12 * 3600
DEBUG = False

# client identity matching discord desktop
CLIENT_VERSION = "1.0.9253"
CLIENT_BUILD_NUMBER = 594031
NATIVE_BUILD_NUMBER = 88414
OS_VERSION = "10.0.26200"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) discord/1.0.9253 Chrome/148.0.7778.280 "
    "Electron/42.7.1 Safari/537.36"
)

# streaming badge milestones (hours)
STREAM_TIERS = [
    (1, "Newcomer", 1),
    (2, "Fledgling", 5),
    (3, "Breakout", 20),
    (4, "Standout", 75),
    (5, "Trendsetter", 150),
    (6, "Headliner", 300),
    (7, "Star", 500),
    (8, "Sensation", 1000),
    (9, "Visionary", 2000),
    (10, "Phenomenon", 5000),
]

# popular games to randomly assign stream context
POPULAR_STREAM_GAMES = [
    ("356828650048323584", "VALORANT", "VALORANT-Win64-Shipping.exe"),
    ("438122941374070784", "Minecraft", "javaw.exe"),
    ("731306170669531147", "Grand Theft Auto V", "GTA5.exe"),
    ("731306170669531148", "Counter-Strike 2", "cs2.exe"),
    ("356869127241990144", "League of Legends", "LeagueClient.exe"),
    ("444089524797898752", "Fortnite", "FortniteClient-Win64-Shipping.exe"),
    ("731306170669531149", "Apex Legends", "r5apex.exe"),
    ("731306170669531150", "Overwatch 2", "Overwatch.exe"),
    ("731306170669531151", "Rocket League", "RocketLeague.exe"),
    ("731306170669531152", "Roblox", "RobloxPlayerBeta.exe"),
]


def _user_id_from_token(token: str) -> str:
    try:
        first = token.split(".", 1)[0]
        pad = "=" * (-len(first) % 4)
        return base64.b64decode(first + pad).decode("utf-8")
    except Exception:
        return ""


class Console:
    """colored terminal output with timestamped entries."""

    RED = "\x1b[91m"
    ORANGE = "\x1b[38;5;208m"
    GREEN = "\x1b[92m"
    YELLOW = "\x1b[93m"
    CYAN = "\x1b[96m"
    WHITE = "\x1b[97m"
    GREY = "\x1b[90m"
    MAGENTA = "\x1b[95m"
    RESET = "\x1b[0m"
    RULE = "─" * 48

    def __init__(self) -> None:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        if sys.platform == "win32":
            self._enable_ansi()

    @staticmethod
    def _enable_ansi() -> None:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)

    def _stamp(self) -> str:
        return f"{self.GREY}{time.strftime('%H:%M:%S')}{self.RESET}"

    def _line(self, glyph: str, target: str, detail: str, color: str) -> None:
        print(f"  {self._stamp()} {glyph} {self.WHITE}{target}{self.RESET} {self.GREY}·{self.RESET} {color}{detail}{self.RESET}")

    def ok(self, target: str, detail: str) -> None:
        self._line(f"{self.GREEN}✓{self.RESET}", target, detail, self.GREEN)

    def sent(self, target: str, detail: str) -> None:
        self._line(f"{self.CYAN}↑{self.RESET}", target, detail, self.CYAN)

    def live(self, target: str, detail: str) -> None:
        self._line(f"{self.MAGENTA}●{self.RESET}", target, detail, self.MAGENTA)

    def warn(self, target: str, detail: str) -> None:
        self._line(f"{self.YELLOW}!{self.RESET}", target, detail, self.YELLOW)

    def err(self, target: str, detail: str) -> None:
        self._line(f"{self.RED}✗{self.RESET}", target, detail, self.RED)

    def info(self, detail: str) -> None:
        print(f"  {self._stamp()} {self.GREY}·{self.RESET} {self.WHITE}{detail}{self.RESET}")

    def rule(self) -> None:
        print(f"  {self.GREY}{self.RULE}{self.RESET}")

    def clear(self) -> None:
        print("\x1b[2J\x1b[3J\x1b[H", end="")

    def banner(self) -> None:
        self.clear()
        print()
        print(f"  {self.CYAN}stream maximizer{self.RESET} {self.GREY}·{self.RESET} {self.WHITE}discord stream time badge{self.RESET}")
        print(f"    {self.GREY}advanced multi-vector telemetry & live stream engine{self.RESET}")
        print()


@dataclass
class State:
    """persistent auth state: token, cookie, analytics_token, stream stats."""

    token: str = ""
    cookie: str = ""
    fingerprint: str = ""
    analytics_token: str = ""
    fetched_at: int = 0
    total_stream_hours_claimed: float = 0.0
    total_stream_sessions: int = 0
    last_guild_id: str = ""
    last_channel_id: str = ""

    @classmethod
    def load(cls) -> "State":
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                known_keys = set(cls().__dict__.keys())
                filtered = {k: v for k, v in data.items() if k in known_keys}
                return cls(**filtered)
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        # preserve existing keys from session.json (like games list, stats)
        existing = {}
        if STATE_FILE.exists():
            try:
                existing = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing.update(asdict(self))
        STATE_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    @property
    def is_stale(self) -> bool:
        return not self.analytics_token or (time.time() - self.fetched_at) > AUTH_MAX_AGE

    @property
    def has_cookie(self) -> bool:
        return bool(self.cookie.strip())

    @property
    def has_token(self) -> bool:
        return bool(self.token.strip())


def _local_props() -> dict:
    return {
        "os": "Windows",
        "browser": "Discord Client",
        "release_channel": "stable",
        "client_version": CLIENT_VERSION,
        "os_version": OS_VERSION,
        "os_arch": "x64",
        "app_arch": "x64",
        "system_locale": "en-US",
        "has_client_mods": False,
        "browser_user_agent": USER_AGENT,
        "browser_version": "42.7.1",
        "os_sdk_version": "26200",
        "client_build_number": CLIENT_BUILD_NUMBER,
        "native_build_number": NATIVE_BUILD_NUMBER,
        "client_event_source": None,
        "client_app_state": "focused",
    }


def build_super_props(launch_signature: str, heartbeat_session: str) -> tuple[str, dict]:
    try:
        req = urllib.request.Request(
            PROPERTIES_URL,
            method="POST",
            data=b"{}",
            headers={"content-type": "application/json", "user-agent": USER_AGENT},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            props = json.loads(resp.read().decode("utf-8"))["properties"]
    except Exception:
        props = _local_props()
    props["client_launch_id"] = str(uuid.uuid4())
    props["launch_signature"] = launch_signature
    props["client_heartbeat_session_id"] = heartbeat_session
    raw = json.dumps(props, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii"), props


def _read_analytics_token(auth_token: str, super_props: str) -> str:
    req = urllib.request.Request(
        ME_URL,
        headers={
            "authorization": auth_token,
            "user-agent": USER_AGENT,
            "x-super-properties": super_props,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"token rejected (HTTP {exc.code})") from exc
    token = data.get("analytics_token")
    if not token:
        raise RuntimeError("no analytics_token returned by discord")
    return token


def ensure_token(state: State, super_props: str) -> None:
    if not state.is_stale:
        return
    state.analytics_token = _read_analytics_token(state.token, super_props)
    state.fetched_at = int(time.time())
    state.save()


@dataclass(frozen=True)
class Session:
    """ephemeral client identity per execution."""

    heartbeat_session: str
    launch_signature: str
    super_props: str
    props_dict: dict

    @classmethod
    def new(cls) -> "Session":
        hb = str(uuid.uuid4())
        sig = str(uuid.uuid4())
        b64_props, raw_props = build_super_props(sig, hb)
        return cls(hb, sig, b64_props, raw_props)


class ScienceClient:
    """constructs and posts telemetry packets to /api/v9/science."""

    def __init__(self, state: State, session: Session) -> None:
        self.state = state
        self.session = session
        self._seq = 0

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def build_stream_events(
        self,
        duration_ms: int,
        guild_id: str = "",
        channel_id: str = "",
        viewer_count: int = 2,
        stream_type: str = "screen",
        game_info: tuple[str, str, str] | None = None,
        end_ts: int | None = None,
    ) -> list[dict]:
        """
        crafts a comprehensive stream session sequence:
        1. video_stream_started (backdated to start of stream)
        2. running_game_heartbeat (with voice/media session metadata)
        3. video_stream_heartbeat (mid-session duration snapshot)
        4. video_stream_ended (terminal event with duration, viewer metrics)
        5. screenshare_finished (desktop telemetry counterpart)
        6. voice_connection_ended (underlying voice session summary)
        """
        now = int(time.time() * 1000) if end_ts is None else end_ts
        start_ts = max(0, now - duration_ms)
        media_sid = str(uuid.uuid4())
        rtc_id = str(uuid.uuid4())
        user_id = _user_id_from_token(self.state.token) or str(random.randint(10**17, 10**18))

        if not guild_id:
            guild_id = self.state.last_guild_id or str(random.randint(10**18, 10**19))
        if not channel_id:
            channel_id = self.state.last_channel_id or str(random.randint(10**18, 10**19))

        stream_key = f"guild:{guild_id}:{channel_id}:{user_id}"
        duration_sec = int(duration_ms / 1000)

        events: list[dict] = []

        # 1. video_stream_started
        events.append({
            "type": "video_stream_started",
            "properties": {
                "client_track_timestamp": start_ts,
                "client_heartbeat_session_id": self.session.heartbeat_session,
                "event_sequence_number": self._next_seq(),
                "channel_id": channel_id,
                "guild_id": guild_id,
                "media_session_id": media_sid,
                "rtc_connection_id": rtc_id,
                "stream_key": stream_key,
                "context": "guild",
                "stream_type": stream_type,
                "is_owner": True,
                "has_audio": True,
                "video_codec": "H264",
                "video_resolution": "1080p",
                "video_fps": 60,
                "audio_codec": "opus",
                "rendered_locale": "en-US",
                "launch_signature": self.session.launch_signature,
                "client_app_state": "focused",
                "client_send_timestamp": start_ts,
            },
        })

        # 2. game heartbeat linked with voice and stream
        game_id, game_name, game_exe = game_info or random.choice(POPULAR_STREAM_GAMES)
        events.append({
            "type": "running_game_heartbeat",
            "properties": {
                "client_track_timestamp": now,
                "client_heartbeat_session_id": self.session.heartbeat_session,
                "event_sequence_number": self._next_seq(),
                "game_id": game_id,
                "game_name": game_name,
                "game_metadata": None,
                "game_executable": game_exe,
                "game_detection_enabled": True,
                "initial_heartbeat": False,
                "final_heartbeat": True,
                "game_session_id": str(uuid.uuid4()),
                "duration_tracked_ms": duration_ms,
                "rtc_connection_id": rtc_id,
                "media_session_id": media_sid,
                "voice_channel_id": channel_id,
                "voice_channel_guild_id": guild_id,
                "voice_channel_type": 2,  # GUILD_VOICE
                "voice_channel_bitrate": 64000,
                "launch_signature": self.session.launch_signature,
                "client_app_state": "focused",
                "client_send_timestamp": now,
            },
        })

        # 3. video_stream_heartbeat
        events.append({
            "type": "video_stream_heartbeat",
            "properties": {
                "client_track_timestamp": now,
                "client_heartbeat_session_id": self.session.heartbeat_session,
                "event_sequence_number": self._next_seq(),
                "channel_id": channel_id,
                "guild_id": guild_id,
                "media_session_id": media_sid,
                "rtc_connection_id": rtc_id,
                "stream_key": stream_key,
                "duration_tracked_ms": duration_ms,
                "duration": duration_sec,
                "viewer_count": viewer_count,
                "max_viewer_count": viewer_count + 1,
                "stream_type": stream_type,
                "launch_signature": self.session.launch_signature,
                "client_app_state": "focused",
                "client_send_timestamp": now,
            },
        })

        # 4. video_stream_ended
        events.append({
            "type": "video_stream_ended",
            "properties": {
                "client_track_timestamp": now,
                "client_heartbeat_session_id": self.session.heartbeat_session,
                "event_sequence_number": self._next_seq(),
                "channel_id": channel_id,
                "guild_id": guild_id,
                "media_session_id": media_sid,
                "rtc_connection_id": rtc_id,
                "stream_key": stream_key,
                "duration": duration_sec,
                "duration_ms": duration_ms,
                "duration_tracked_ms": duration_ms,
                "viewer_count": viewer_count,
                "max_viewers": viewer_count + 1,
                "average_viewers": float(viewer_count),
                "stream_type": stream_type,
                "disconnect_reason": "user_ended",
                "launch_signature": self.session.launch_signature,
                "client_app_state": "focused",
                "client_send_timestamp": now,
            },
        })

        # 5. screenshare_finished
        events.append({
            "type": "screenshare_finished",
            "properties": {
                "client_track_timestamp": now,
                "client_heartbeat_session_id": self.session.heartbeat_session,
                "event_sequence_number": self._next_seq(),
                "channel_id": channel_id,
                "guild_id": guild_id,
                "media_session_id": media_sid,
                "rtc_connection_id": rtc_id,
                "duration": duration_sec,
                "duration_ms": duration_ms,
                "viewer_count": viewer_count,
                "launch_signature": self.session.launch_signature,
                "client_app_state": "focused",
                "client_send_timestamp": now,
            },
        })

        # 6. voice_connection_ended
        events.append({
            "type": "voice_connection_ended",
            "properties": {
                "client_track_timestamp": now,
                "client_heartbeat_session_id": self.session.heartbeat_session,
                "event_sequence_number": self._next_seq(),
                "channel_id": channel_id,
                "guild_id": guild_id,
                "media_session_id": media_sid,
                "rtc_connection_id": rtc_id,
                "duration": duration_sec,
                "duration_ms": duration_ms,
                "disconnect_reason": "user_disconnect",
                "launch_signature": self.session.launch_signature,
                "client_app_state": "focused",
                "client_send_timestamp": now,
            },
        })

        return events

    def post(self, events: Sequence[dict]) -> int:
        """posts a batch to /api/v9/science. returns HTTP status code (204 = success)."""
        payload = {"token": self.state.analytics_token, "events": list(events)}
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "accept": "*/*",
            "accept-language": "en-US",
            "authorization": self.state.token,
            "content-type": "application/json",
            "cookie": self.state.cookie,
            "origin": "https://discord.com",
            "referer": "https://discord.com/channels/@me",
            "user-agent": USER_AGENT,
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "UTC",
            "x-super-properties": self.session.super_props,
        }
        if DEBUG:
            print("\n" + "=" * 60)
            print(f"POST {SCIENCE_URL} ({len(payload['events'])} events)")
            print("body:", json.dumps(payload, indent=2))
            print("=" * 60)
        req = urllib.request.Request(SCIENCE_URL, data=body, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status
        except urllib.error.HTTPError as exc:
            return exc.code
        except Exception:
            return 0



class MiniWebSocket:
    """pure stdlib websocket client (RFC 6455) for discord gateway communication."""

    def __init__(self, host: str, port: int = 443, path: str = "/") -> None:
        self.host = host
        self.port = port
        self.path = path
        self.sock: ssl.SSLSocket | None = None
        self.closed = True

    def connect(self) -> None:
        raw_sock = socket.create_connection((self.host, self.port), timeout=15)
        ctx = ssl.create_default_context()
        self.sock = ctx.wrap_socket(raw_sock, server_hostname=self.host)
        sec_key = base64.b64encode(os.urandom(16)).decode("ascii")

        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {sec_key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"User-Agent: {USER_AGENT}\r\n\r\n"
        )
        self.sock.sendall(req.encode("utf-8"))

        # read handshake response
        header_data = b""
        while b"\r\n\r\n" not in header_data:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("failed handshake with gateway")
            header_data += chunk

        first_line = header_data.split(b"\r\n")[0].decode("utf-8", "ignore")
        if "101" not in first_line:
            raise ConnectionError(f"gateway handshake rejected: {first_line}")
        self.closed = False

    def send(self, data: str) -> None:
        if self.closed or not self.sock:
            raise ConnectionError("socket closed")
        payload = data.encode("utf-8")
        length = len(payload)
        mask_key = os.urandom(4)

        header = bytearray([0x81])  # FIN + text frame opcode
        if length <= 125:
            header.append(0x80 | length)
        elif length <= 65535:
            header.append(0x80 | 126)
            header.extend(length.to_bytes(2, "big"))
        else:
            header.append(0x80 | 127)
            header.extend(length.to_bytes(8, "big"))

        header.extend(mask_key)
        masked = bytearray(payload[i] ^ mask_key[i % 4] for i in range(length))
        self.sock.sendall(header + masked)

    def recv(self, timeout: float = 5.0) -> dict | None:
        if self.closed or not self.sock:
            return None
        r, _, _ = select.select([self.sock], [], [], timeout)
        if not r:
            return None

        # read frame header
        head = self.sock.recv(2)
        if not head or len(head) < 2:
            return None
        opcode = head[0] & 0x0F
        if opcode == 0x8:  # close frame
            self.close()
            return None
        if opcode == 0x9:  # ping -> send pong
            # respond to ping
            return {"op": "ping"}

        length = head[1] & 0x7F
        if length == 126:
            ext = self.sock.recv(2)
            length = int.from_bytes(ext, "big")
        elif length == 127:
            ext = self.sock.recv(8)
            length = int.from_bytes(ext, "big")

        payload = b""
        while len(payload) < length:
            chunk = self.sock.recv(length - len(payload))
            if not chunk:
                break
            payload += chunk

        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return None

    def close(self) -> None:
        self.closed = True
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass


class GatewayStreamEngine:
    """
    connects to discord gateway, joins voice channel, and triggers Opcode 18 STREAM_CREATE
    allows legitimate live streaming in a voice channel headlessly without a running game or GPU
    """

    def __init__(self, state: State, session: Session, console: Console) -> None:
        self.state = state
        self.session = session
        self.console = console
        self.ws: MiniWebSocket | None = None
        self.running = False
        self.heartbeat_interval = 41.25
        self.sequence: int | None = None
        self.stream_key = ""
        self.session_id = ""
        self.start_time = 0.0

    def start_stream(self, guild_id: str, channel_id: str) -> None:
        C = self.console
        C.info("connecting to discord gateway (wss://gateway.discord.gg)...")
        self.ws = MiniWebSocket(GATEWAY_URL, path="/?v=9&encoding=json")
        try:
            self.ws.connect()
        except Exception as exc:
            C.err("gateway", f"connection failed: {exc}")
            C.rule()
            input(f"  {C.ORANGE}›{C.RESET} press enter to return to menu")
            return

        C.ok("gateway", "connected")
        self.running = True
        self.start_time = time.time()

        t = threading.Thread(target=self._loop, args=(guild_id, channel_id), daemon=True)
        t.start()

        print()
        C.live("stream", f"broadcasting Go Live in channel {C.ORANGE}{channel_id}{C.RESET}")
        C.info(f"{C.GREEN}active!{C.WHITE} discord shows your account as {C.MAGENTA}LIVE{C.RESET}")
        C.rule()
        input(f"  {C.ORANGE}›{C.RESET} press enter at any time to stop streaming: ")

        self.running = False
        if self.ws:
            try:
                if self.stream_key:
                    self.ws.send(json.dumps({"op": 19, "d": {"stream_key": self.stream_key}}))
                self.ws.send(json.dumps({"op": 4, "d": {"guild_id": guild_id, "channel_id": None, "self_mute": False, "self_deaf": False, "self_video": False}}))
            except Exception:
                pass
            self.ws.close()

        elapsed = time.time() - self.start_time
        hours = elapsed / 3600.0
        self.state.total_stream_hours_claimed += hours
        self.state.save()
        C.ok("stream", f"ended · {elapsed:.0f}s ({hours:.2f}h) streamed live")
        C.rule()
        input(f"  {C.ORANGE}›{C.RESET} press enter to return to menu")

    def _loop(self, guild_id: str, channel_id: str) -> None:
        last_hb = time.time()
        while self.running:
            try:
                now = time.time()
                if now - last_hb > self.heartbeat_interval:
                    self.ws.send(json.dumps({"op": 1, "d": self.sequence}))
                    last_hb = now

                msg = self.ws.recv(timeout=1.0)
                if not msg:
                    continue

                op = msg.get("op")
                seq = msg.get("s")
                t = msg.get("t")
                d = msg.get("d")

                if seq is not None:
                    self.sequence = seq

                if op == 10:
                    self.heartbeat_interval = d.get("heartbeat_interval", 41250) / 1000.0
                    last_hb = time.time()
                    ident = {
                        "op": 2,
                        "d": {
                            "token": self.state.token,
                            "capabilities": 16381,
                            "properties": self.session.props_dict,
                            "presence": {
                                "status": "online",
                                "since": 0,
                                "activities": [],
                                "afk": False,
                            },
                        },
                    }
                    self.ws.send(json.dumps(ident))

                elif op == 0 and t == "READY":
                    self.session_id = d.get("session_id", "")
                    self.console.ok("auth", f"gateway authenticated ({d.get('user', {}).get('username')})")

                    voice_state = {
                        "op": 4,
                        "d": {
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "self_mute": False,
                            "self_deaf": False,
                            "self_video": False,
                        },
                    }
                    self.ws.send(json.dumps(voice_state))

                    stream_create = {
                        "op": 18,
                        "d": {
                            "type": "guild",
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "preferred_region": None,
                        },
                    }
                    self.ws.send(json.dumps(stream_create))

                elif op == 0 and t == "STREAM_CREATE":
                    self.stream_key = d.get("stream_key", "")
                    self.console.ok("stream", f"stream created! stream_key: {self.stream_key}")

                elif op == 1:
                    self.ws.send(json.dumps({"op": 1, "d": self.sequence}))
                    last_hb = time.time()

            except Exception:
                if not self.running:
                    break


def inspect_profile(state: State, session: Session, console: Console) -> None:
    C = console
    if not state.has_token:
        C.err("auth", "no token saved")
        C.rule()
        input(f"  {C.ORANGE}›{C.RESET} press enter to continue")
        return

    C.info("fetching profile data from discord...")
    uid = _user_id_from_token(state.token)
    if not uid:
        try:
            req_me = urllib.request.Request(
                ME_URL,
                headers={
                    "authorization": state.token,
                    "user-agent": USER_AGENT,
                    "x-super-properties": session.super_props,
                },
            )
            with urllib.request.urlopen(req_me, timeout=10) as resp:
                uid = json.loads(resp.read().decode("utf-8")).get("id", "")
        except Exception:
            pass

    if not uid:
        C.err("profile", "unable to resolve user id from token")
        C.rule()
        input(f"  {C.ORANGE}›{C.RESET} press enter to continue")
        return

    url = f"{USERS_URL}/{uid}/profile?with_mutual_guilds=false&with_mutual_friends_count=false"
    req = urllib.request.Request(
        url,
        headers={
            "authorization": state.token,
            "user-agent": USER_AGENT,
            "x-super-properties": session.super_props,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        user = data.get("user", {})
        badges = data.get("badges", [])
        C.rule()
        username = user.get("username", "Unknown")
        global_name = user.get("global_name")
        display = f"{global_name} (@{username})" if global_name else f"@{username}"
        C.ok("account", f"{display} · ID: {uid}")

        if badges:
            C.info(f"badges ({len(badges)}):")
            for b in badges:
                bid = b.get("id", "badge")
                desc = b.get("description", "")
                C.info(f"  {C.CYAN}•{C.WHITE} {C.ORANGE}{bid}{C.WHITE}: {desc}")
        else:
            C.info("no public badges equipped on profile")
    except Exception as exc:
        C.err("profile", f"failed to load: {exc}")

    C.rule()
    input(f"  {C.ORANGE}›{C.RESET} press enter to continue")


# main stream maximizer application
class StreamMaximizerApp:
    def __init__(self) -> None:
        self.console = Console()
        self.state = State.load()
        self.session: Session | None = None
        self.client: ScienceClient | None = None

    def start(self) -> None:
        C = self.console
        C.banner()
        time.sleep(0.3)

        # 1. token check
        if not self.state.has_token:
            self._prompt_token()
        else:
            C.ok("auth", "token loaded from state")
        if not self.state.has_token:
            C.err("token", "required to run")
            return

        # 2. cookie check
        if not self.state.has_cookie:
            self._prompt_cookie()
        else:
            C.ok("auth", "cf_clearance cookie loaded")
        if not self.state.has_cookie:
            C.err("cookie", "required to run")
            return

        # 3. initialize session and analytics token
        C.info("validating session...")
        self._new_session()
        try:
            ensure_token(self.state, self.session.super_props)
            C.ok("auth", "ready · analytics token cached")
        except Exception as exc:
            C.err("auth", str(exc))
            return

        time.sleep(0.5)
        self.menu()

    def _new_session(self) -> None:
        self.session = Session.new()
        self.client = ScienceClient(self.state, self.session)

    def _prompt_token(self) -> None:
        self.console.info("paste your discord account token")
        entered = input(f"  {self.console.GREY}token:{self.console.RESET} ").strip()
        if entered:
            self.state.token = entered
            self.state.save()
            self.console.ok("token", "saved")

    def _prompt_cookie(self) -> None:
        self.console.info("paste your cf_clearance cookie header")
        entered = input(f"  {self.console.GREY}cookie:{self.console.RESET} ").strip()
        if entered:
            self.state.cookie = entered
            self.state.save()
            self.console.ok("cookie", "saved")

    def _refresh(self) -> None:
        C = self.console
        C.info("paste updated token (or leave empty to keep current):")
        tok = input(f"  {C.GREY}token:{C.RESET} ").strip()
        if tok:
            self.state.token = tok
            C.ok("token", "updated")

        C.info("paste fresh cf_clearance cookie (or leave empty to keep current):")
        ck = input(f"  {C.GREY}cookie:{C.RESET} ").strip()
        if ck:
            self.state.cookie = ck
            C.ok("cookie", "updated")

        C.info("refreshing analytics token...")
        try:
            self.state.fetched_at = 0
            ensure_token(self.state, self.session.super_props)
            self._new_session()
            self.state.save()
            C.ok("auth", "refreshed successfully")
        except Exception as exc:
            C.err("auth", str(exc))
        time.sleep(1)

    # Mode 1: Instant Science Telemetry Forge
    def claim_stream_hours(self) -> None:
        """forges and posts stream session events directly to /api/v9/science."""
        C = self.console
        C.rule()
        C.info(f"{C.CYAN}Instant Telemetry Spoof{C.WHITE} - Forge N hours streamed directly to Discord Science")
        C.rule()

        # Display streaming tiers
        print("  Streaming Badge Tiers:")
        for tier, name, req in STREAM_TIERS:
            print(f"    Tier {tier:2d} · {C.ORANGE}{name:12s}{C.RESET} {req:5d} hours")
        print()

        raw_hours = input(f"  {C.GREY}target hours to claim? [e.g. 5000]:{C.RESET} ").strip()
        try:
            hours = float(raw_hours) if raw_hours else 5000.0
        except ValueError:
            C.err("input", "invalid hours")
            return

        # Target guild/channel (optional; synthetic defaults used if blank)
        raw_guild = input(f"  {C.GREY}target guild id (optional, enter to randomize):{C.RESET} ").strip()
        raw_chan = input(f"  {C.GREY}target voice channel id (optional, enter to randomize):{C.RESET} ").strip()

        if raw_guild:
            self.state.last_guild_id = raw_guild
        if raw_chan:
            self.state.last_channel_id = raw_chan
        self.state.save()

        # Prompt for session duration size (large chunks vs realistic multi-session)
        print()
        C.info("choose injection strategy:")
        print(f"    {C.ORANGE}1{C.RESET} · Single High-Impact Session (One giant stream session of {hours:,.0f}h)")
        print(f"    {C.ORANGE}2{C.RESET} · Realistic Session Batches (Chunked into 10h stream sessions)")
        strat = input(f"  {C.ORANGE}›{C.RESET} select strategy [1]: ").strip() or "1"

        sessions_to_send: list[list[dict]] = []

        if strat == "1":
            # 1 massive session
            duration_ms = int(hours * 3600 * 1000)
            events = self.client.build_stream_events(
                duration_ms=duration_ms,
                guild_id=raw_guild,
                channel_id=raw_chan,
                viewer_count=2,
            )
            sessions_to_send.append(events)
        else:
            # Chunked into 10-hour sessions
            chunk_hours = 10.0
            num_chunks = math.ceil(hours / chunk_hours)
            now = int(time.time() * 1000)
            for i in range(num_chunks):
                chunk_h = min(chunk_hours, hours - (i * chunk_hours))
                duration_ms = int(chunk_h * 3600 * 1000)
                # backdate each session by i * 12 hours
                session_end = now - (i * 12 * 3600 * 1000)
                events = self.client.build_stream_events(
                    duration_ms=duration_ms,
                    guild_id=raw_guild,
                    channel_id=raw_chan,
                    viewer_count=random.randint(2, 5),
                    end_ts=session_end,
                )
                sessions_to_send.append(events)

        total_batches = len(sessions_to_send)
        C.info(f"dispatching {C.ORANGE}{total_batches}{C.WHITE} stream session(s) totalling {C.ORANGE}{hours:,.0f} hours{C.WHITE}...")
        C.rule()

        claimed_ok = 0
        for idx, session_events in enumerate(sessions_to_send, 1):
            status = self.client.post(session_events)
            if status == 204:
                claimed_ok += 1
                C.sent(f"session {idx}/{total_batches}", f"HTTP 204 Accepted ({len(session_events)} events)")
            elif status in (401, 403):
                C.err(f"session {idx}", f"HTTP {status} auth rejected · refresh auth (option 4)")
                break
            else:
                C.warn(f"session {idx}", f"HTTP {status}")
            time.sleep(BATCH_DELAY)

        print()
        if claimed_ok == total_batches:
            C.ok("complete", f"successfully claimed {hours:,.0f} streamed hours across {claimed_ok} session(s)!")
            self.state.total_stream_hours_claimed += hours
            self.state.total_stream_sessions += claimed_ok
            self.state.save()
        else:
            C.warn("incomplete", f"{claimed_ok}/{total_batches} sessions sent successfully")

        C.info(f"{C.GREY}note: discord badge progression updates every 24-48h on analytics sync.{C.RESET}")
        C.rule()
        input(f"  {C.ORANGE}›{C.RESET} press enter to return to menu")

    # Mode 2: Multi-Session Realistic Historical Stream Generator
    def generate_historical_stream_history(self) -> None:
        """generates a realistic multi-week history of streams with natural durations."""
        C = self.console
        C.rule()
        C.info(f"{C.CYAN}Realistic Historical Stream History Builder{C.WHITE}")
        C.rule()
        C.info("generates historical stream sessions spanning the past 30-90 days,")
        C.info("with randomized lengths (2h to 6h), varying viewer counts (1-8), and game titles.")
        print()

        raw_hours = input(f"  {C.GREY}cumulative hours to generate? [500]:{C.RESET} ").strip()
        try:
            target_hours = float(raw_hours) if raw_hours else 500.0
        except ValueError:
            C.err("input", "invalid hours")
            return

        accumulated = 0.0
        sessions: list[list[dict]] = []
        now = int(time.time() * 1000)

        current_end = now
        while accumulated < target_hours:
            dur_h = round(random.uniform(2.0, 5.5), 2)
            if accumulated + dur_h > target_hours:
                dur_h = round(target_hours - accumulated, 2)
            duration_ms = int(dur_h * 3600 * 1000)
            viewers = random.randint(2, 7)
            game = random.choice(POPULAR_STREAM_GAMES)

            ev = self.client.build_stream_events(
                duration_ms=duration_ms,
                guild_id=self.state.last_guild_id,
                channel_id=self.state.last_channel_id,
                viewer_count=viewers,
                game_info=game,
                end_ts=current_end,
            )
            sessions.append(ev)
            accumulated += dur_h
            # step back 1 to 2 days for next session
            current_end -= int(random.uniform(20, 36) * 3600 * 1000)

        C.info(f"generated {C.ORANGE}{len(sessions)}{C.WHITE} distinct stream sessions ({accumulated:,.1f}h total).")
        C.rule()

        sent_ok = 0
        for i, s in enumerate(sessions, 1):
            status = self.client.post(s)
            if status == 204:
                sent_ok += 1
                C.sent(f"stream {i}/{len(sessions)}", f"HTTP 204 Accepted")
            else:
                C.warn(f"stream {i}", f"HTTP {status}")
            time.sleep(BATCH_DELAY)

        print()
        C.ok("complete", f"dispatched {sent_ok}/{len(sessions)} historical streams ({accumulated:,.1f}h)")
        self.state.total_stream_hours_claimed += accumulated
        self.state.total_stream_sessions += sent_ok
        self.state.save()
        C.rule()
        input(f"  {C.ORANGE}›{C.RESET} press enter to return to menu")

    # Mode 3: Headless Gateway Live Streamer (Real AFK Stream)
    def run_gateway_live_streamer(self) -> None:
        """joins real voice channel and sets live Go Live state."""
        C = self.console
        C.rule()
        C.info(f"{C.MAGENTA}Headless Gateway Live Streamer{C.WHITE} (Zero CPU/GPU Go Live)")
        C.rule()
        C.info("this connects your account to discord gateway and broadcasts an active")
        C.info("Go Live stream directly in a voice channel without running any games or GPU.")
        print()

        guild_id = input(f"  {C.GREY}server (guild) id:{C.RESET} ").strip() or self.state.last_guild_id
        channel_id = input(f"  {C.GREY}voice channel id:{C.RESET} ").strip() or self.state.last_channel_id

        if not guild_id or not channel_id:
            C.err("input", "guild id and voice channel id are required for live streaming")
            time.sleep(1.5)
            return

        self.state.last_guild_id = guild_id
        self.state.last_channel_id = channel_id
        self.state.save()

        engine = GatewayStreamEngine(self.state, self.session, self.console)
        engine.start_stream(guild_id, channel_id)

    # menu loop
    def menu(self) -> None:
        C = self.console
        while True:
            C.clear()
            C.banner()
            C.info(f"total stream hours claimed: {C.ORANGE}{self.state.total_stream_hours_claimed:,.1f}h{C.WHITE} ({self.state.total_stream_sessions} sessions)")
            C.rule()
            C.info(f"{C.ORANGE}1{C.RESET} · Claim Stream Hours (Instant Telemetry Forge)")
            C.info(f"{C.ORANGE}2{C.RESET} · Generate Realistic Stream History (Multi-Week Generator)")
            C.info(f"{C.ORANGE}3{C.RESET} · Headless Gateway AFK Streamer (Live Go-Live Broadcast)")
            C.info(f"{C.ORANGE}4{C.RESET} · Inspect Discord Profile & Badges")
            C.info(f"{C.ORANGE}5{C.RESET} · Refresh Auth (Token & Cookie)")
            C.info(f"{C.ORANGE}6{C.RESET} · Exit")
            C.rule()

            choice = input(f"  {C.ORANGE}›{C.RESET} ").strip()
            print()
            if choice == "1":
                self.claim_stream_hours()
            elif choice == "2":
                self.generate_historical_stream_history()
            elif choice == "3":
                self.run_gateway_live_streamer()
            elif choice == "4":
                inspect_profile(self.state, self.session, self.console)
            elif choice == "5":
                self._refresh()
            elif choice in ("6", "exit", "q"):
                break
            else:
                C.warn("input", "invalid option")
                time.sleep(1)


def main() -> None:
    try:
        StreamMaximizerApp().start()
    except KeyboardInterrupt:
        print()
        Console().warn("exit", "operation interrupted by user")


if __name__ == "__main__":
    main()
