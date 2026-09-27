# ==================== FAST MASTER CONTROLLER ====================
# Fixes: Multi-key level lookup (raw UID + account_id + nickname)

import os
import sys
import json
import time
import signal
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Optional

# ==================== CONFIG ====================
ACCOUNTS_FILE = "accounts.json"
COMPLETED_DIR = "completed_accounts"
COMPLETED_FILE = os.path.join(COMPLETED_DIR, "completed.json")

CS_SCRIPT = "cs.py"
MAIN_SCRIPT = "Main.py"

LEVEL_FOR_MAIN = 3
LEVEL_FOR_COMPLETE = 21

POLL_INTERVAL = 0.5
CS_TIMEOUT_SECONDS = 1800          # safety: 30 min
MAIN_TIMEOUT_SECONDS = 14400       # safety: 4 hr

CS_LEVEL_FILE = "cs_levels.json"
TOKEN_CACHE_FILE = "token_cache.json"

# ==================== COLORS ====================
USE_COLOR = sys.platform != "win32" or os.environ.get("WT_SESSION") or os.environ.get("ANSICON")

class C:
    GREEN = '\033[92m' if USE_COLOR else ''
    RED = '\033[91m' if USE_COLOR else ''
    YELLOW = '\033[93m' if USE_COLOR else ''
    CYAN = '\033[96m' if USE_COLOR else ''
    MAGENTA = '\033[95m' if USE_COLOR else ''
    WHITE = '\033[97m' if USE_COLOR else ''
    END = '\033[0m' if USE_COLOR else ''

def log(msg, color=C.WHITE):
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"{color}[{ts}] {msg}{C.END}", flush=True)
    except Exception:
        print(f"[{ts}] {msg}", flush=True)

def log_success(m): log(f"[OK] {m}", C.GREEN)
def log_error(m):   log(f"[ERR] {m}", C.RED)
def log_warn(m):    log(f"[WARN] {m}", C.YELLOW)
def log_info(m):    log(f"[INFO] {m}", C.CYAN)
def log_phase(m):   log(f"[PHASE] {m}", C.MAGENTA)


# ==================== FILE HELPERS ====================
def ensure_dirs():
    os.makedirs(COMPLETED_DIR, exist_ok=True)

def load_accounts() -> List[Dict]:
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        log_error(f"accounts.json load failed: {e}")
        return []

def save_accounts(accounts: List[Dict]):
    try:
        tmp = ACCOUNTS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2, ensure_ascii=False)
        os.replace(tmp, ACCOUNTS_FILE)
    except Exception as e:
        log_error(f"accounts.json save failed: {e}")

def load_completed() -> List[Dict]:
    if not os.path.exists(COMPLETED_FILE):
        return []
    try:
        with open(COMPLETED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_completed(completed: List[Dict]):
    try:
        tmp = COMPLETED_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(completed, f, indent=2, ensure_ascii=False)
        os.replace(tmp, COMPLETED_FILE)
    except Exception as e:
        log_error(f"completed.json save failed: {e}")


# ==================== LEVEL LOOKUP (MULTI-KEY) ====================
def _read_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)
    except Exception:
        return {}

def read_level_from_cs(uid: str) -> Optional[int]:
    """Read from cs_levels.json using any matching key."""
    data = _read_json(CS_LEVEL_FILE)
    if not data:
        return None
    uid_str = str(uid)
    # Try direct match
    if uid_str in data:
        try:
            return int(data[uid_str].get("level", 0))
        except Exception:
            pass
    # Scan all entries for matching uid
    for k, v in data.items():
        if str(k) == uid_str:
            try:
                return int(v.get("level", 0))
            except Exception:
                pass
    return None

def read_level_from_token_cache(uid: str) -> Optional[int]:
    """Read from token_cache.json using any matching key."""
    data = _read_json(TOKEN_CACHE_FILE)
    if not data:
        return None
    uid_str = str(uid)
    # Direct match on various key forms
    for key in (uid_str, f"tok_{uid_str}", f"tok_{uid_str[:20]}"):
        if key in data:
            try:
                lvl = data[key].get("level")
                if lvl is not None:
                    return int(lvl)
            except Exception:
                pass
    # Fallback: scan all entries where auth_uid or account_id matches
    for k, v in data.items():
        if not isinstance(v, dict):
            continue
        try:
            if str(v.get("auth_uid", "")) == uid_str:
                lvl = v.get("level")
                if lvl is not None:
                    return int(lvl)
            if str(v.get("account_id", "")) == uid_str:
                lvl = v.get("level")
                if lvl is not None:
                    return int(lvl)
        except Exception:
            continue
    return None

def read_level_from_all_sources(uid: str) -> Optional[int]:
    """Try ALL sources: raw UID, any account_id mapping, etc."""
    candidates = []
    # 1. cs_levels.json
    a = read_level_from_cs(uid)
    if a is not None:
        candidates.append(a)
    # 2. token_cache.json
    b = read_level_from_token_cache(uid)
    if b is not None:
        candidates.append(b)
    # 3. Check cs_levels.json for ANY key that maps to this uid via token_cache
    token_data = _read_json(TOKEN_CACHE_FILE)
    for k, v in token_data.items():
        if not isinstance(v, dict):
            continue
        if str(v.get("auth_uid", "")) == str(uid):
            # Found account mapping → look up account_id in cs_levels
            acc_id = str(v.get("account_id", ""))
            if acc_id:
                c = read_level_from_cs(acc_id)
                if c is not None:
                    candidates.append(c)
        if str(v.get("account_id", "")) == str(uid):
            auth_uid = str(v.get("auth_uid", ""))
            if auth_uid:
                c = read_level_from_cs(auth_uid)
                if c is not None:
                    candidates.append(c)

    return max(candidates) if candidates else None


# ==================== ACCOUNT WORKER ====================
class AccountWorker:
    def __init__(self, uid: str, password: str, nickname: str = ""):
        self.uid = str(uid).strip()
        self.password = str(password).strip()
        self.nickname = nickname or f"Player_{self.uid}"
        self.process: Optional[subprocess.Popen] = None
        self.phase = "idle"
        self.cs_start_time = 0.0
        self.main_start_time = 0.0
        self.running = True
        self.last_level = 0
        self._output_thread: Optional[threading.Thread] = None

    def _start_process(self, script: str) -> bool:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        cmd = [sys.executable, "-u", script, self.uid, self.password]
        log_info(f"[{self.uid}] START: {' '.join(cmd)}")
        try:
            popen_kwargs = dict(
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                bufsize=0
            )
            if sys.platform == "win32":
                popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                popen_kwargs["start_new_session"] = True

            self.process = subprocess.Popen(cmd, **popen_kwargs)

            def _reader():
                try:
                    for raw in iter(self.process.stdout.readline, b''):
                        if not raw:
                            break
                        try:
                            sys.stdout.write(f"[{self.uid}] {raw.decode(errors='replace')}")
                            sys.stdout.flush()
                        except Exception:
                            pass
                except Exception:
                    pass

            self._output_thread = threading.Thread(target=_reader, daemon=True)
            self._output_thread.start()
            return True
        except Exception as e:
            log_error(f"[{self.uid}] START failed ({script}): {e}")
            self.process = None
            return False

    def _stop_process(self, timeout: float = 6.0):
        if not self.process:
            return
        log_warn(f"[{self.uid}] STOP process...")
        try:
            if sys.platform == "win32":
                self.process.terminate()
            else:
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                except Exception:
                    self.process.terminate()
        except Exception:
            pass

        try:
            self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            log_warn(f"[{self.uid}] FORCE kill")
            try:
                if sys.platform == "win32":
                    self.process.kill()
                else:
                    try:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    except Exception:
                        self.process.kill()
            except Exception:
                pass
        finally:
            self.process = None

    def _is_alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def start_cs(self):
        log_phase(f"[{self.uid}] Phase 1: cs.py (Level 2 → 3)")
        if self._start_process(CS_SCRIPT):
            self.phase = "cs"
            self.cs_start_time = time.time()
        else:
            self.phase = "failed"

    def start_main(self):
        log_phase(f"[{self.uid}] Phase 2: Main.py (Level 3 → 21)")
        if self._start_process(MAIN_SCRIPT):
            self.phase = "main"
            self.main_start_time = time.time()
        else:
            self.phase = "failed"

    def complete(self) -> Dict:
        return {
            "uid": self.uid,
            "password": self.password,
            "nickname": self.nickname,
            "level": self.last_level,
            "completed_at": datetime.now().isoformat(timespec="seconds")
        }

    def tick(self):
        if not self.running or self.phase in ("done", "failed"):
            return

        if self.phase == "cs":
            # ⭐ Multi-key lookup — এখানেই আসল ফিক্স
            lvl = read_level_from_all_sources(self.uid)
            if lvl is not None:
                self.last_level = max(self.last_level, lvl)
                if lvl >= LEVEL_FOR_MAIN:
                    log_success(f"[{self.uid}] Level {lvl} detected → Main.py তে সুইচ")
                    self._stop_process()
                    self.start_main()
                    return

            if (time.time() - self.cs_start_time) >= CS_TIMEOUT_SECONDS:
                log_warn(f"[{self.uid}] CS timeout ({CS_TIMEOUT_SECONDS}s) → Main.py")
                self._stop_process()
                self.start_main()
                return

            if not self._is_alive():
                # cs.py মরে গেছে → level চেক করে decide
                self._stop_process()
                lvl = read_level_from_all_sources(self.uid)
                if lvl is not None and lvl >= LEVEL_FOR_MAIN:
                    log_success(f"[{self.uid}] cs.py exited, Level {lvl} ≥ 3 → Main.py")
                    self.start_main()
                elif lvl is not None and lvl > self.last_level:
                    log_success(f"[{self.uid}] cs.py exited, Level {lvl} (was {self.last_level}) → Main.py")
                    self.start_main()
                else:
                    # Level এখনো 3 হয়নি → cs.py আবার
                    # ⭐ Safety: 3 বার পর পর দ্রুত exit হলে Main.py তে যাই
                    if (time.time() - self.cs_start_time) < 3.0:
                        # খুব দ্রুত exit হয়েছে → সম্ভবত level 3+ ছিল কিন্তু read করতে পারিনি
                        log_warn(f"[{self.uid}] cs.py too fast exit → Main.py তে যাই (safety)")
                        self.start_main()
                    else:
                        log_info(f"[{self.uid}] Level এখনো {lvl} < 3 → cs.py আবার")
                        self.start_cs()
                return

        elif self.phase == "main":
            lvl = read_level_from_all_sources(self.uid)
            if lvl is not None:
                self.last_level = max(self.last_level, lvl)
                if lvl >= LEVEL_FOR_COMPLETE:
                    log_success(f"[{self.uid}] 🎉 Level {lvl} → সম্পন্ন!")
                    self._stop_process()
                    self.phase = "done"
                    self.running = False
                    return

            if (time.time() - self.main_start_time) >= MAIN_TIMEOUT_SECONDS:
                log_warn(f"[{self.uid}] Main timeout → restart")
                self._stop_process()
                self.start_main()
                return

            if not self._is_alive():
                log_warn(f"[{self.uid}] Main.py বন্ধ → আবার চালু")
                self._stop_process()
                self.start_main()
                return

    def stop(self):
        self.running = False
        self._stop_process()


# ==================== MASTER ====================
class Master:
    def __init__(self):
        self.workers: Dict[str, AccountWorker] = {}
        self.completed_uids: set = set()
        self.stop_flag = False
        self._accounts_mtime = 0.0

    def _load_completed_uids(self):
        completed = load_completed()
        self.completed_uids = {str(c["uid"]) for c in completed}
        log_info(f"পূর্বে সম্পন্ন অ্যাকাউন্ট: {len(self.completed_uids)}")

    def _get_accounts_mtime(self) -> float:
        try:
            return os.path.getmtime(ACCOUNTS_FILE) if os.path.exists(ACCOUNTS_FILE) else 0.0
        except Exception:
            return 0.0

    def _spawn_workers(self):
        accounts = load_accounts()
        existing_uids = set()

        for acc in accounts:
            uid = str(acc.get("uid", "")).strip()
            pwd = str(acc.get("password", "")).strip()
            nick = acc.get("nickname", "")

            if not uid or not pwd:
                continue

            existing_uids.add(uid)

            if uid in self.completed_uids:
                continue

            if uid in self.workers:
                continue

            current_lvl = read_level_from_all_sources(uid)
            w = AccountWorker(uid, pwd, nick)
            self.workers[uid] = w

            if current_lvl is not None and current_lvl >= LEVEL_FOR_MAIN:
                log_info(f"[{uid}] Level {current_lvl} → সরাসরি Main.py")
                w.start_main()
            else:
                log_info(f"[{uid}] Level {current_lvl or '<3'} → cs.py")
                w.start_cs()

        for uid in list(self.workers.keys()):
            if uid not in existing_uids and uid not in self.completed_uids:
                log_info(f"[{uid}] accounts.json থেকে মুছে ফেলা → ওয়ার্কার বন্ধ")
                self.workers[uid].stop()
                del self.workers[uid]

    def _remove_completed_from_accounts(self, uid: str):
        accounts = load_accounts()
        new_accounts = [a for a in accounts if str(a.get("uid")) != str(uid)]
        if len(new_accounts) != len(accounts):
            save_accounts(new_accounts)
            log_info(f"[{uid}] accounts.json থেকে রিমুভ")

    def _save_completed(self, record: Dict):
        completed = load_completed()
        completed = [c for c in completed if str(c["uid"]) != str(record["uid"])]
        completed.append(record)
        save_completed(completed)
        self.completed_uids.add(str(record["uid"]))
        log_success(f"[{record['uid']}] completed.json এ সেভ (Level {record['level']})")

    def tick(self):
        mtime = self._get_accounts_mtime()
        if mtime != self._accounts_mtime:
            self._accounts_mtime = mtime
            self._spawn_workers()

        for uid, w in list(self.workers.items()):
            w.tick()

            if w.phase == "done":
                record = w.complete()
                self._save_completed(record)
                self._remove_completed_from_accounts(uid)
                del self.workers[uid]
                log_success(f"[{uid}] চূড়ান্তভাবে শেষ ও রিমুভ")
            elif w.phase == "failed":
                log_error(f"[{uid}] ওয়ার্কার ব্যর্থ → রিমুভ")
                del self.workers[uid]

        return True

    def stop_all(self):
        log_warn("সব ওয়ার্কার বন্ধ করা হচ্ছে...")
        for w in self.workers.values():
            w.stop()
        self.workers.clear()


# ==================== SIGNAL ====================
_master_instance: Optional[Master] = None

def _signal_handler(signum, frame):
    log_warn(f"\nসিগন্যাল {signum} → শাটডাউন")
    if _master_instance:
        _master_instance.stop_all()
    sys.exit(0)


# ==================== MAIN ====================
def main():
    global _master_instance
    ensure_dirs()

    print("=" * 60)
    print("   FAST Master Controller - Level-Based Auto Switch")
    print("=" * 60)
    log_info(f"Poll interval: {POLL_INTERVAL}s")
    log_info(f"Level for Main: {LEVEL_FOR_MAIN}")
    log_info(f"Level for Complete: {LEVEL_FOR_COMPLETE}")
    log_info(f"CS timeout: {CS_TIMEOUT_SECONDS}s")
    log_info(f"Main timeout: {MAIN_TIMEOUT_SECONDS}s")
    log_info(f"Multi-key level lookup: ENABLED")
    print("=" * 60)

    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _signal_handler)

    master = Master()
    _master_instance = master

    master._load_completed_uids()
    master._accounts_mtime = master._get_accounts_mtime()
    master._spawn_workers()

    if not master.workers:
        log_warn("কোনো অ্যাকাউন্ট নেই। accounts.json এ UID/Password দিন।")

    try:
        while True:
            master.tick()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log_warn("\nব্যবহারকারী থামিয়েছে")
    finally:
        master.stop_all()
        log_success("সব প্রসেস বন্ধ।")


if __name__ == "__main__":
    main()