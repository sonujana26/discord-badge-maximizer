#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator, Sequence

WORKSPACE_DIR = Path(__file__).resolve().parent
STATE_STORAGE_PATH = WORKSPACE_DIR / "session.json"
DATABASE_STORAGE_PATH = WORKSPACE_DIR.parent / "data" / "games.json"

REST_IDENTITY_URL = "https://discord.com/api/v9/users/@me?with_analytics_token=true"
DISCORD_USERS_API = "https://discord.com/api/v9/users"
TELEMETRY_INGEST_URL = "https://discord.com/api/v9/science"
UPSTREAM_METRICS_URL = "https://cordapi.dolfi.es/api/v2/properties/windows"
DISCORD_CATALOG_URL = "https://cdn.discordapp.com/detectables/games.json"

DISPATCH_BATCH_LIMIT = 50
NETWORK_COOLDOWN_SEC = 0.3
TOKEN_EXPIRY_THRESHOLD_SEC = 12 * 3600

DESKTOP_CLIENT_VERSION = "1.0.9253"
DESKTOP_BUILD_IDENTIFIER = 594031
PLATFORM_BUILD_IDENTIFIER = 88414
PLATFORM_OS_REVISION = "10.0.26200"
USER_AGENT_IDENTIFIER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) discord/1.0.9253 Chrome/148.0.7778.280 "
    "Electron/42.7.1 Safari/537.36"
)

# PE32+ Authenticode and MachineGuid metadata extraction script for Discord executable validation
_POWERSHELL_PE_ANALYZER = r'''
param(
  [int]$ProcessId = 0,
  [string]$Path,
  [Parameter(Mandatory = $true)][string]$UserId
)

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class CertPubKeyHash {
  const uint X509_ASN_ENCODING = 0x00000001;
  const uint PKCS_7_ASN_ENCODING = 0x00010000;
  const uint CALG_SHA_256 = 0x0000800C;

  [StructLayout(LayoutKind.Sequential)] struct Blob { public uint cbData; public IntPtr pbData; }
  [StructLayout(LayoutKind.Sequential)] struct AlgId { public IntPtr pszObjId; public Blob Parameters; }
  [StructLayout(LayoutKind.Sequential)] struct BitBlob { public uint cbData; public IntPtr pbData; public uint cUnusedBits; }
  [StructLayout(LayoutKind.Sequential)] struct PubKeyInfo { public AlgId Algorithm; public BitBlob PublicKey; }
  [StructLayout(LayoutKind.Sequential)] struct FileTime { public uint Low; public uint High; }
  [StructLayout(LayoutKind.Sequential)]
  struct CertInfo {
    public uint Version; public Blob SerialNumber; public AlgId SignatureAlgorithm; public Blob Issuer;
    public FileTime NotBefore; public FileTime NotAfter; public Blob Subject;
    public PubKeyInfo SubjectPublicKeyInfo; public BitBlob IssuerUniqueId; public BitBlob SubjectUniqueId;
    public uint ExtensionCount; public IntPtr Extensions;
  }
  [StructLayout(LayoutKind.Sequential)]
  struct CertContext {
    public uint EncodingType; public IntPtr Encoded; public uint EncodedSize;
    public IntPtr CertInfo; public IntPtr Store;
  }

  [DllImport("crypt32.dll", SetLastError = true)]
  static extern bool CryptHashPublicKeyInfo(
    IntPtr provider, uint algid, uint flags, uint encoding, ref PubKeyInfo info, byte[] hash, ref uint hashSize);

  public static byte[] Hash(IntPtr certContext) {
    var ctx = Marshal.PtrToStructure<CertContext>(certContext);
    var info = Marshal.PtrToStructure<CertInfo>(ctx.CertInfo);
    var hash = new byte[32];
    uint hashSize = 32;
    if (!CryptHashPublicKeyInfo(IntPtr.Zero, CALG_SHA_256, 0, X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, ref info.SubjectPublicKeyInfo, hash, ref hashSize) || hashSize != 32)
      throw new InvalidOperationException("CryptHashPublicKeyInfo failed");
    return hash;
  }
}
"@

if (!$Path) {
  if (!$ProcessId) { throw "Pass -Path <exe> or -ProcessId <pid>." }
  $Path = (Get-Process -Id $ProcessId).Path
}
if (!$Path) { throw "Could not resolve executable path." }

$fs = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
try {
  $fileSize = [UInt64]$fs.Length
  $readSize = [int][Math]::Min($fs.Length, 0x10000)
  $buf = [byte[]]::new($readSize)
  $read = $fs.Read($buf, 0, $readSize)
  if ($read -lt 0x40) { throw "File prefix is too small." }
  if ($read -ne $readSize) { [Array]::Resize([ref]$buf, $read) }
} finally {
  $fs.Dispose()
}

if ([BitConverter]::ToUInt16($buf, 0) -ne 0x5A4D) { throw "Not an MZ executable." }
$pe = [BitConverter]::ToInt32($buf, 0x3C)
if ($pe -lt 0 -or [BitConverter]::ToUInt32($buf, $pe) -ne 0x4550) { throw "Not a PE executable." }

$fh = $pe + 4
$sections = [BitConverter]::ToUInt16($buf, $fh + 2)
$timestamp = [BitConverter]::ToUInt32($buf, $fh + 4)
$optSize = [BitConverter]::ToUInt16($buf, $fh + 16)
$opt = $fh + 20
$isPe32Plus = [BitConverter]::ToUInt16($buf, $opt) -eq 0x20B
if (!$isPe32Plus) { throw "Discord only fingerprints PE32+." }
$sizeOfImage = [BitConverter]::ToUInt32($buf, $opt + 56)

$sectionTable = $opt + $optSize
$sha256 = [Security.Cryptography.SHA256]::Create()
$headerHash = $sha256.ComputeHash([byte[]]$buf[0..($sectionTable - 1)])
$sectionHash = $sha256.ComputeHash([byte[]]$buf[$sectionTable..($sectionTable + $sections * 40 - 1)])

$machineGuid = (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Cryptography" -Name MachineGuid).MachineGuid
$machineUserHash = $sha256.ComputeHash([Text.Encoding]::UTF8.GetBytes($machineGuid + $UserId))

$sig = Get-AuthenticodeSignature -LiteralPath $Path
$signed = $sig.Status -eq "Valid" -and $sig.SignerCertificate
if ($signed) {
  $name = $sig.SignerCertificate.GetNameInfo([Security.Cryptography.X509Certificates.X509NameType]::SimpleName, $false)
  $certHash = $sha256.ComputeHash([Text.Encoding]::UTF8.GetBytes($name) + [CertPubKeyHash]::Hash($sig.SignerCertificate.Handle))
} else {
  $certHash = [byte[]]::new(32)
}

$flags = 0
if ($signed) { $flags += 1 }
if ($isPe32Plus) { $flags += 2 }

$out = [byte[]](@(1, [byte]$flags) +
  [BitConverter]::GetBytes($fileSize) +
  [BitConverter]::GetBytes($timestamp) +
  [BitConverter]::GetBytes($sizeOfImage) +
  $headerHash + $machineUserHash + $sectionHash + $certHash)

$key = $sha256.ComputeHash([Text.Encoding]::UTF8.GetBytes($UserId + "https://discord.com/careers"))
for ($i = 1; $i -lt $out.Length; $i++) {
  $out[$i] = $out[$i] -bxor $key[($i - 1) -band 31]
}

[Convert]::ToBase64String($out)
'''


def extract_account_snowflake(auth_token: str) -> str:
    try:
        prefix = auth_token.split(".", 1)[0]
        padding = "=" * (-len(prefix) % 4)
        return base64.b64decode(prefix + padding).decode("utf-8")
    except Exception:
        return ""


def build_binary_signature(account_id: str, file_path: str = "", active_pid: int = 0) -> str:
    if os.name != "nt":
        raise RuntimeError("Fingerprint generation requires a Windows runtime.")
    temp_script = Path(tempfile.gettempdir()) / f"sig_gen_{uuid.uuid4().hex}.ps1"
    temp_script.write_text(_POWERSHELL_PE_ANALYZER, encoding="utf-8")
    try:
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(temp_script), "-UserId", account_id
        ]
        cmd += (["-ProcessId", str(active_pid)] if active_pid else ["-Path", file_path])
        execution = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    finally:
        try:
            temp_script.unlink()
        except OSError:
            pass
    if execution.returncode != 0:
        err_msg = (execution.stderr or execution.stdout or "").strip().splitlines()
        raise RuntimeError(err_msg[-1] if err_msg else "PowerShell fingerprint generation failed.")
    lines = [line.strip() for line in execution.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("Fingerprint generator yielded empty output.")
    return lines[-1]


class TerminalInterface:
    COLOR_ALERT = "\x1b[91m"
    COLOR_PRIMARY = "\x1b[38;5;208m"
    COLOR_SUCCESS = "\x1b[92m"
    COLOR_NOTICE = "\x1b[93m"
    COLOR_TEXT = "\x1b[97m"
    COLOR_MUTED = "\x1b[90m"
    COLOR_RESET = "\x1b[0m"
    DIVIDER = "─" * 46

    def __init__(self) -> None:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        if sys.platform == "win32":
            self._activate_vt_processing()

    @staticmethod
    def _activate_vt_processing() -> None:
        import ctypes
        kernel = ctypes.windll.kernel32
        stdout_handle = kernel.GetStdHandle(-11)
        flags = ctypes.c_uint32()
        if kernel.GetConsoleMode(stdout_handle, ctypes.byref(flags)):
            kernel.SetConsoleMode(stdout_handle, flags.value | 0x0004)

    def _render_timestamp(self) -> str:
        return f"{self.COLOR_MUTED}{time.strftime('%H:%M:%S')}{self.COLOR_RESET}"

    def write_status(self, symbol: str, target: str, message: str, color: str) -> None:
        print(f"  {self._render_timestamp()} {symbol} {self.COLOR_TEXT}{target}{self.COLOR_RESET} "
              f"{self.COLOR_MUTED}·{self.COLOR_RESET} {color}{message}{self.COLOR_RESET}")

    def success(self, target: str, message: str) -> None:
        self.write_status(f"{self.COLOR_SUCCESS}✓{self.COLOR_RESET}", target, message, self.COLOR_SUCCESS)

    def dispatched(self, target: str, message: str) -> None:
        self.write_status(f"{self.COLOR_MUTED}·{self.COLOR_RESET} {self.COLOR_SUCCESS}posted{self.COLOR_RESET}", target, message, self.COLOR_SUCCESS)

    def warning(self, target: str, message: str) -> None:
        self.write_status(f"{self.COLOR_NOTICE}!{self.COLOR_RESET}", target, message, self.COLOR_NOTICE)

    def failure(self, target: str, message: str) -> None:
        self.write_status(f"{self.COLOR_ALERT}✗{self.COLOR_RESET}", target, message, self.COLOR_ALERT)

    def log(self, message: str) -> None:
        print(f"  {self._render_timestamp()} {self.COLOR_MUTED}·{self.COLOR_RESET} {self.COLOR_TEXT}{message}{self.COLOR_RESET}")

    def separator(self) -> None:
        print(f"  {self.COLOR_MUTED}{self.DIVIDER}{self.COLOR_RESET}")

    def clear_viewport(self) -> None:
        print("\x1b[2J\x1b[3J\x1b[H", end="")

    def display_header(self) -> None:
        self.clear_viewport()
        print()
        print(f"  {self.COLOR_PRIMARY}DISCORD BADGE MAXIMIZER{self.COLOR_RESET} {self.COLOR_MUTED}·{self.COLOR_RESET} {self.COLOR_TEXT}Playtime & Game Variety{self.COLOR_RESET}")
        print(f"    {self.COLOR_MUTED}Direct Telemetry Ingestion Engine{self.COLOR_RESET}")
        print()


@dataclass
class AccountSessionState:
    token: str = ""
    cookie: str = ""
    fingerprint: str = ""
    analytics_token: str = ""
    fetched_at: int = 0
    used_games: list[str] = field(default_factory=list)
    total_games_claimed: int = 0
    total_hours_claimed: float = 0.0

    @classmethod
    def restore(cls) -> "AccountSessionState":
        if STATE_STORAGE_PATH.exists():
            try:
                raw_data = json.loads(STATE_STORAGE_PATH.read_text(encoding="utf-8"))
                known_keys = set(cls().__dict__.keys())
                instance = cls(**{k: v for k, v in raw_data.items() if k in known_keys and k != "used_games"})
                instance.used_games = raw_data.get("used_games", [])
                return instance
            except Exception:
                pass
        return cls()

    def persist(self) -> None:
        existing = {}
        if STATE_STORAGE_PATH.exists():
            try:
                existing = json.loads(STATE_STORAGE_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing.update(asdict(self))
        STATE_STORAGE_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    @property
    def requires_refresh(self) -> bool:
        return not self.analytics_token or (time.time() - self.fetched_at) > TOKEN_EXPIRY_THRESHOLD_SEC

    @property
    def has_credentials(self) -> bool:
        return bool(self.token.strip()) and bool(self.cookie.strip())


def generate_fallback_properties() -> dict:
    return {
        "os": "Windows",
        "browser": "Discord Client",
        "release_channel": "stable",
        "client_version": DESKTOP_CLIENT_VERSION,
        "os_version": PLATFORM_OS_REVISION,
        "os_arch": "x64",
        "app_arch": "x64",
        "system_locale": "en-US",
        "has_client_mods": False,
        "browser_user_agent": USER_AGENT_IDENTIFIER,
        "browser_version": "42.7.1",
        "os_sdk_version": "26200",
        "client_build_number": DESKTOP_BUILD_NUMBER,
        "native_build_number": PLATFORM_BUILD_IDENTIFIER,
        "client_event_source": None,
        "client_app_state": "focused",
    }


def assemble_super_properties(signature_id: str, session_id: str) -> str:
    try:
        network_req = urllib.request.Request(
            UPSTREAM_METRICS_URL,
            method="POST",
            data=b"{}",
            headers={"content-type": "application/json", "user-agent": USER_AGENT_IDENTIFIER}
        )
        with urllib.request.urlopen(network_req, timeout=10) as net_resp:
            properties_payload = json.loads(net_resp.read().decode("utf-8"))["properties"]
    except Exception:
        properties_payload = generate_fallback_properties()

    properties_payload["client_launch_id"] = str(uuid.uuid4())
    properties_payload["launch_signature"] = signature_id
    properties_payload["client_heartbeat_session_id"] = session_id
    serialized = json.dumps(properties_payload, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(serialized).decode("ascii")


def request_analytics_credential(auth_token: str, super_properties_b64: str) -> str:
    network_req = urllib.request.Request(
        REST_IDENTITY_URL,
        headers={
            "authorization": auth_token,
            "user-agent": USER_AGENT_IDENTIFIER,
            "x-super-properties": super_properties_b64,
        }
    )
    try:
        with urllib.request.urlopen(network_req, timeout=15) as net_resp:
            parsed = json.loads(net_resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Authentication rejected by endpoint (HTTP {exc.code})") from exc

    credential = parsed.get("analytics_token")
    if not credential:
        raise RuntimeError("Upstream response omitted analytics_token field.")
    return credential


def synchronize_credentials(state: AccountSessionState, super_props_b64: str) -> None:
    if not state.requires_refresh:
        return
    state.analytics_token = request_analytics_credential(state.token, super_props_b64)
    state.fetched_at = int(time.time())
    state.persist()


@dataclass(frozen=True)
class RuntimeClientContext:
    heartbeat_session_id: str
    launch_signature_id: str
    encoded_properties: str

    @classmethod
    def initialize(cls) -> "RuntimeClientContext":
        hb_session = str(uuid.uuid4())
        launch_sig = str(uuid.uuid4())
        return cls(hb_session, launch_sig, assemble_super_properties(launch_sig, hb_session))


@dataclass(frozen=True)
class DetectableTitle:
    title_id: str
    display_name: str
    binary_name: str


def identify_windows_binary(game_record: dict) -> str:
    for target in game_record.get("executables", []):
        if target.get("os") == "win32" and target.get("name"):
            return target["name"]
    return "game.exe"


def fetch_remote_catalog() -> str:
    req = urllib.request.Request(DISCORD_CATALOG_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8")
    try:
        DATABASE_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        DATABASE_STORAGE_PATH.write_text(content, encoding="utf-8")
    except OSError:
        pass
    return content


def parse_catalog_entries(raw_json: str) -> list[DetectableTitle]:
    payload = json.loads(raw_json)
    catalog: list[DetectableTitle] = []
    registered_ids: set[str] = set()

    for item in payload:
        record_id = str(item.get("id", ""))
        if not record_id.isdigit() or record_id in registered_ids:
            continue
        if not any(entry.get("os") == "win32" and entry.get("name") for entry in item.get("executables", [])):
            continue
        registered_ids.add(record_id)
        catalog.append(DetectableTitle(record_id, item.get("name", "Unknown Game"), identify_windows_binary(item)))

    return catalog


def load_game_catalog() -> list[DetectableTitle]:
    cached_content = ""
    if DATABASE_STORAGE_PATH.exists():
        cached_content = DATABASE_STORAGE_PATH.read_text(encoding="utf-8").strip()
    if cached_content:
        try:
            titles = parse_catalog_entries(cached_content)
            if titles:
                return titles
        except (json.JSONDecodeError, ValueError):
            pass
    try:
        return parse_catalog_entries(fetch_remote_catalog())
    except Exception:
        return []


class TelemetryEventFabricator:
    def __init__(self, state: AccountSessionState, context: RuntimeClientContext) -> None:
        self.state = state
        self.context = context
        self._sequence_index = 0

    def _increment_sequence(self) -> int:
        self._sequence_index += 1
        return self._sequence_index

    def construct_launch_payload(self, title: DetectableTitle) -> dict:
        timestamp_now = int(time.time() * 1000)
        attributes = {
            "client_track_timestamp": timestamp_now,
            "client_heartbeat_session_id": self.context.heartbeat_session_id,
            "event_sequence_number": self._increment_sequence(),
            "game": title.display_name,
            "game_id": title.title_id,
            "verified": True,
            "elevated": False,
            "is_launcher": False,
            "game_platform": "desktop",
            "detection_method": "verified_game",
            "is_overlay_enabled": False,
            "is_overlay_game_enabled": True,
            "is_overlay_game_source": "OOP_DEFAULT_DATABASE",
            "fullscreen_type": "UNKNOWN",
            "hardware_display_count": 1,
            "overlay_method": "Disabled",
            "activity_status_enabled": True,
            "activity_status_shared_guilds": [],
            "current_user_status": "online",
            "game_detection_enabled": True,
            "executable_path": title.binary_name,
            "voice_channel_id": None,
            "voice_channel_type": None,
            "voice_channel_bitrate": None,
            "voice_channel_guild_id": None,
            "hidden_by_distributor": False,
            "game_metadata": None,
            "executable_fingerprint": self.state.fingerprint,
            "client_performance_cpu": None,
            "client_performance_memory": None,
            "cpu_core_count": None,
            "accessibility_features": 0,
            "rendered_locale": "en-US",
            "launch_signature": self.context.launch_signature_id,
            "client_rtc_state": None,
            "client_app_state": "focused",
            "client_send_timestamp": timestamp_now,
        }
        if not self.state.fingerprint:
            attributes.pop("executable_fingerprint", None)
        return {"type": "launch_game", "properties": attributes}

    def construct_heartbeat_payload(
        self,
        title: DetectableTitle,
        duration_ms: int,
        session_token: str,
        is_initial: bool,
        is_final: bool,
        event_time_ms: int | None = None
    ) -> dict:
        tracked_time = int(time.time() * 1000) if event_time_ms is None else event_time_ms
        return {
            "type": "running_game_heartbeat",
            "properties": {
                "client_track_timestamp": tracked_time,
                "client_heartbeat_session_id": self.context.heartbeat_session_id,
                "event_sequence_number": self._increment_sequence(),
                "game_id": title.title_id,
                "game_name": title.display_name,
                "game_metadata": None,
                "game_executable": title.binary_name,
                "game_detection_enabled": True,
                "initial_heartbeat": is_initial,
                "final_heartbeat": is_final,
                "game_session_id": session_token,
                "duration_tracked_ms": duration_ms,
                "rtc_connection_id": None,
                "media_session_id": None,
                "launch_signature": self.context.launch_signature_id,
                "client_app_state": "focused",
                "client_send_timestamp": tracked_time,
            },
        }

    def assemble_complete_session(self, title: DetectableTitle, duration_ms: int) -> list[dict]:
        session_id = str(uuid.uuid4())
        current_time = int(time.time() * 1000)
        origin_time = current_time - duration_ms
        if origin_time < 0:
            origin_time = current_time

        return [
            self.construct_heartbeat_payload(title, 0, session_id, is_initial=True, is_final=False, event_time_ms=origin_time),
            self.construct_launch_payload(title),
            self.construct_heartbeat_payload(title, duration_ms, session_id, is_initial=False, is_final=True, event_time_ms=current_time),
        ]

    def post_telemetry_batch(self, events: Sequence[dict]) -> int:
        envelope = {"token": self.state.analytics_token, "events": list(events)}
        encoded_body = json.dumps(envelope).encode("utf-8")
        network_headers = {
            "accept": "*/*",
            "accept-language": "en-US",
            "authorization": self.state.token,
            "content-type": "application/json",
            "cookie": self.state.cookie,
            "origin": "https://discord.com",
            "referer": "https://discord.com/channels/@me",
            "user-agent": USER_AGENT_IDENTIFIER,
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "UTC",
            "x-super-properties": self.context.encoded_properties,
        }

        request_handle = urllib.request.Request(TELEMETRY_INGEST_URL, data=encoded_body, method="POST", headers=network_headers)
        try:
            with urllib.request.urlopen(request_handle, timeout=15) as response:
                return response.status
        except urllib.error.HTTPError as error:
            return error.code
        except Exception:
            return 0


def segment_collection(items: Sequence[DetectableTitle], chunk_size: int) -> Iterator[Sequence[DetectableTitle]]:
    for idx in range(0, len(items), chunk_size):
        yield items[idx:idx + chunk_size]


class IngestionPipeline:
    def __init__(self, fabricator: TelemetryEventFabricator, terminal: TerminalInterface) -> None:
        self.fabricator = fabricator
        self.terminal = terminal

    def execute_stream(self, titles: Sequence[DetectableTitle], session_builder) -> int:
        total_records = len(titles)
        processed_successfully = 0

        for batch_index, partition in enumerate(segment_collection(titles, DISPATCH_BATCH_LIMIT), start=1):
            accumulated_events = []
            for target in partition:
                accumulated_events.extend(session_builder(target))

            http_status = self.fabricator.post_telemetry_batch(accumulated_events)
            if http_status == 204:
                processed_successfully += len(partition)
                self.terminal.dispatched(f"batch {batch_index}", f"{processed_successfully}/{total_records} titles accepted")
            elif http_status in (401, 403):
                self.terminal.failure(
                    f"batch {batch_index}",
                    f"[{http_status}] Authentication failed. Refresh token/cookie via Option 3."
                )
                return processed_successfully
            else:
                self.terminal.warning(f"batch {batch_index}", f"HTTP {http_status}")

            time.sleep(NETWORK_COOLDOWN_SEC)

        return processed_successfully


class ApplicationController:
    def __init__(self) -> None:
        self.terminal = TerminalInterface()
        self.state = AccountSessionState.restore()
        self.runtime_context: RuntimeClientContext | None = None
        self.fabricator: TelemetryEventFabricator | None = None
        self.catalog: list[DetectableTitle] = []

    def start(self) -> None:
        self.terminal.display_header()
        time.sleep(0.3)

        if not self.state.token:
            self._prompt_account_token()
        else:
            self.terminal.success("auth", "User token loaded from state")

        if not self.state.token:
            self.terminal.failure("token", "Account token is required.")
            return

        if not self.state.cookie:
            self.terminal.display_header()
            self._prompt_clearance_cookie()
        else:
            self.terminal.success("auth", "Clearance cookie loaded from state")

        if not self.state.cookie:
            self.terminal.failure("cookie", "cf_clearance cookie is required.")
            return

        self.terminal.log("loading detectable games catalog...")
        self.catalog = load_game_catalog()
        if not self.catalog:
            self.terminal.failure("catalog", "Unable to retrieve detectable games catalog.")
            return
        self.terminal.success("catalog", f"{len(self.catalog)} verified titles loaded")

        if not self.state.fingerprint:
            self.terminal.warning("fingerprint", "Executable fingerprint not set (optional for hours, recommended for variety).")

        self.terminal.log("synchronizing analytics credentials...")
        self._renew_session()
        try:
            synchronize_credentials(self.state, self.runtime_context.encoded_properties)
        except Exception as exc:
            self.terminal.failure("auth", str(exc))
            return
        self.terminal.success("auth", "Ingestion pipeline initialized")

        time.sleep(0.5)
        self.render_main_menu()

    def _renew_session(self) -> None:
        self.runtime_context = RuntimeClientContext.initialize()
        self.fabricator = TelemetryEventFabricator(self.state, self.runtime_context)

    def _prompt_account_token(self) -> None:
        self.terminal.log("Paste your Discord account authorization token:")
        val = input(f"  {self.terminal.COLOR_MUTED}token:{self.terminal.COLOR_RESET} ").strip()
        if val:
            self.state.token = val
            self.state.persist()
            self.terminal.success("token", "Saved to local state")

    def _prompt_clearance_cookie(self) -> None:
        self.terminal.log("Paste your cf_clearance cookie header value:")
        val = input(f"  {self.terminal.COLOR_MUTED}cookie:{self.terminal.COLOR_RESET} ").strip()
        if val:
            self.state.cookie = val
            self.state.persist()
            self.terminal.success("cookie", "Saved to local state")

    def _reconfigure_credentials(self) -> None:
        T = self.terminal
        T.log("Update cookie header? [y/n]")
        ans = input(f"  {T.COLOR_MUTED}›{T.COLOR_RESET} ").strip().lower()
        if ans in ("y", "yes"):
            T.log("Paste fresh cookie header:")
            new_ck = input(f"  {T.COLOR_MUTED}cookie:{T.COLOR_RESET} ").strip()
            if new_ck:
                self.state.cookie = new_ck
                T.success("cookie", "Updated")

        T.log("Refreshing analytics token from Discord...")
        try:
            self.state.fetched_at = 0
            synchronize_credentials(self.state, self.runtime_context.encoded_properties)
        except Exception as exc:
            T.failure("auth", str(exc))
            return
        self._renew_session()
        self.state.persist()
        T.success("auth", "Credentials refreshed successfully")
        time.sleep(1)

    def _ensure_runtime_readiness(self) -> bool:
        if not self.state.cookie:
            self.terminal.failure("cookie", "Missing cookie. Use Option 3 to configure.")
            return False
        if self.state.requires_refresh:
            try:
                synchronize_credentials(self.state, self.runtime_context.encoded_properties)
            except Exception as exc:
                self.terminal.failure("auth", str(exc))
                return False
            self._renew_session()
        return bool(self.state.analytics_token)

    def trigger_playtime_ingestion(self) -> None:
        if not self._ensure_runtime_readiness():
            return
        T = self.terminal
        print()
        T.log(f"{len(self.catalog)} detectable games available.")

        raw_count = input(f"  {T.COLOR_MUTED}Target games count [all]:{T.COLOR_RESET} ").strip()
        try:
            target_count = int(raw_count) if raw_count else len(self.catalog)
        except ValueError:
            T.failure("input", "Invalid game count specified.")
            return
        target_count = min(target_count, len(self.catalog))

        raw_hours = input(f"  {T.COLOR_MUTED}Hours per game [1]:{T.COLOR_RESET} ").strip()
        try:
            target_hours = float(raw_hours) if raw_hours else 1.0
        except ValueError:
            T.failure("input", "Invalid hours specified.")
            return

        selected_titles = self._filter_title_selection(target_count)
        if not selected_titles:
            T.failure("catalog", "No titles selected.")
            return

        duration_ms = int(target_hours * 3600 * 1000)
        total_aggregate = len(selected_titles) * target_hours
        print()
        T.log(f"Submitting {T.COLOR_PRIMARY}{target_hours:g}h{T.COLOR_TEXT} across {T.COLOR_PRIMARY}{len(selected_titles)}{T.COLOR_TEXT} titles ({total_aggregate:,.0f}h total)")
        T.separator()

        engine = IngestionPipeline(self.fabricator, self.terminal)
        accepted = engine.execute_stream(
            selected_titles,
            lambda title: self.fabricator.assemble_complete_session(title, duration_ms)
        )

        print()
        T.success("completed", f"{accepted}/{len(selected_titles)} titles processed ({accepted * target_hours:,.0f}h total)")
        self.state.total_games_claimed += accepted
        self.state.total_hours_claimed += accepted * target_hours
        self.state.persist()

        T.log(f"{T.COLOR_MUTED}note: discord badge progression updates every 24-48h on analytics sync.{T.COLOR_RESET}")
        T.separator()
        input(f"  {T.COLOR_PRIMARY}›{T.COLOR_RESET} Press enter to return to menu")

    def _filter_title_selection(self, desired_amount: int) -> list[DetectableTitle]:
        existing_pool = {item.title_id for item in self.catalog}
        unprocessed = [item.title_id for item in self.catalog if item.title_id not in self.state.used_games]
        processed = [gid for gid in self.state.used_games if gid in existing_pool]

        if len(unprocessed) >= desired_amount:
            chosen = unprocessed[:desired_amount]
        else:
            chosen = unprocessed
            if processed:
                needed = desired_amount - len(chosen)
                rotated = processed[needed:] + processed[:needed]
                chosen.extend(rotated[:needed])

        self.state.used_games = [gid for gid in self.state.used_games if gid not in chosen] + chosen
        registry = {item.title_id: item for item in self.catalog}
        return [registry[gid] for gid in chosen if gid in registry]

    def configure_executable_fingerprint(self) -> None:
        T = self.terminal
        account_id = extract_account_snowflake(self.state.token)
        if not account_id:
            T.failure("fingerprint", "Valid token required to derive user identity.")
            time.sleep(1)
            return
        if os.name != "nt":
            T.failure("fingerprint", "Fingerprint generation requires Windows OS.")
            time.sleep(1)
            return

        T.log("Generate executable fingerprint bound to account and machine.")
        T.log(f"Account Snowflake: {T.COLOR_PRIMARY}{account_id}{T.COLOR_RESET}")
        T.log("Provide an executable (.exe) path or active game Process ID (PID):")
        raw_input = input(f"  {T.COLOR_MUTED}path or PID:{T.COLOR_RESET} ").strip().strip('"')
        if not raw_input:
            T.log("Operation cancelled.")
            time.sleep(1)
            return

        target_pid = int(raw_input) if raw_input.isdigit() else 0
        target_path = "" if target_pid else raw_input
        if target_path and not Path(target_path).exists():
            T.failure("fingerprint", f"File path does not exist: {target_path}")
            time.sleep(1.5)
            return

        T.log("Generating signature via PowerShell PE analyzer...")
        try:
            signature = build_binary_signature(account_id, file_path=target_path, active_pid=target_pid)
        except Exception as exc:
            T.failure("fingerprint", str(exc))
            time.sleep(2)
            return

        self.state.fingerprint = signature
        self.state.persist()
        T.success("fingerprint", f"Assigned ({len(signature)} chars) · saved to state")
        time.sleep(1.5)

    def inspect_profile(self) -> None:
        T = self.terminal
        if not self.state.token:
            T.failure("auth", "No user token configured.")
            T.separator()
            input(f"  {T.COLOR_PRIMARY}›{T.COLOR_RESET} Press enter to continue")
            return

        T.log("Retrieving profile data from Discord...")
        uid = extract_account_snowflake(self.state.token)
        encoded_props = self.runtime_context.encoded_properties if self.runtime_context else ""
        if not uid:
            try:
                probe_request = urllib.request.Request(
                    REST_IDENTITY_URL,
                    headers={
                        "authorization": self.state.token,
                        "user-agent": USER_AGENT_IDENTIFIER,
                        "x-super-properties": encoded_props,
                    },
                )
                with urllib.request.urlopen(probe_request, timeout=10) as resp:
                    uid = json.loads(resp.read().decode("utf-8")).get("id", "")
            except Exception:
                pass

        if not uid:
            T.failure("profile", "Unable to resolve account identity snowflake.")
            T.separator()
            input(f"  {T.COLOR_PRIMARY}›{T.COLOR_RESET} Press enter to continue")
            return

        target_url = f"{DISCORD_USERS_API}/{uid}/profile?with_mutual_guilds=false&with_mutual_friends_count=false"
        request = urllib.request.Request(
            target_url,
            headers={
                "authorization": self.state.token,
                "user-agent": USER_AGENT_IDENTIFIER,
                "x-super-properties": encoded_props,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as resp:
                profile_payload = json.loads(resp.read().decode("utf-8"))

            user_obj = profile_payload.get("user", {})
            badges_list = profile_payload.get("badges", [])
            T.separator()
            user_handle = user_obj.get("username", "Unknown")
            global_name = user_obj.get("global_name")
            display_name = f"{global_name} (@{user_handle})" if global_name else f"@{user_handle}"
            T.success("account", f"{display_name} · ID: {uid}")

            if badges_list:
                T.log(f"Profile Badges ({len(badges_list)}):")
                for badge in badges_list:
                    bid = badge.get("id", "badge")
                    desc = badge.get("description", "")
                    T.log(f"  {T.COLOR_PRIMARY}•{T.COLOR_RESET} {T.COLOR_TEXT}{bid}{T.COLOR_RESET}: {desc}")
            else:
                T.log("No public badges equipped on profile.")
        except Exception as exc:
            T.failure("profile", f"Failed to retrieve profile: {exc}")

        T.separator()
        input(f"  {T.COLOR_PRIMARY}›{T.COLOR_RESET} Press enter to continue")

    def render_main_menu(self) -> None:
        T = self.terminal
        while True:
            T.clear_viewport()
            T.display_header()
            T.log(f"Detectable Titles: {T.COLOR_PRIMARY}{len(self.catalog)}{T.COLOR_TEXT}")
            T.log(f"Cumulative Logged: {T.COLOR_PRIMARY}{self.state.total_games_claimed}{T.COLOR_TEXT} titles · {T.COLOR_PRIMARY}{self.state.total_hours_claimed:,.0f}h{T.COLOR_TEXT} playtime")
            T.separator()
            T.log(f"{T.COLOR_PRIMARY}1{T.COLOR_RESET} · Claim Games (Game Time & Game Variety)")
            T.log(f"{T.COLOR_PRIMARY}2{T.COLOR_RESET} · Inspect Discord Profile & Badges")
            T.log(f"{T.COLOR_PRIMARY}3{T.COLOR_RESET} · Refresh Credentials & Cookie")
            T.log(f"{T.COLOR_PRIMARY}4{T.COLOR_RESET} · Configure Executable Fingerprint")
            T.log(f"{T.COLOR_PRIMARY}5{T.COLOR_RESET} · Exit")
            T.separator()

            selection = input(f"  {T.COLOR_PRIMARY}›{T.COLOR_RESET} ").strip()
            print()
            if selection == "1":
                self.trigger_playtime_ingestion()
            elif selection == "2":
                self.inspect_profile()
            elif selection == "3":
                self._reconfigure_credentials()
            elif selection == "4":
                self.configure_executable_fingerprint()
            elif selection in ("5", "q", "exit", ""):
                break
            else:
                T.warning("input", "Invalid selection.")
                time.sleep(0.5)


def execute_entrypoint() -> None:
    try:
        ApplicationController().start()
    except KeyboardInterrupt:
        print()
        TerminalInterface().warning("exit", "Execution halted by user.")


if __name__ == "__main__":
    execute_entrypoint()
