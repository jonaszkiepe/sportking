#!/usr/bin/env python3
"""Allegro OAuth for the sportking Inkontor account (device code flow).

  ./scripts/allegro/allegro_auth.py login     # prints a URL + code; you authorize as sklep_Inkontor
  ./scripts/allegro/allegro_auth.py whoami     # read-only check: which account + offer count
  ./scripts/allegro/allegro_auth.py refresh    # refresh the access token (they expire ~12h)

Client credentials come from .env (quotes stripped):
    allegro_client_id, allegro_client_secret
Tokens are saved to .allegro_tokens.json (git-ignored, local only).
Production Allegro by default; set ALLEGRO_SANDBOX=1 to target the sandbox.
"""
import os, sys, json, time, base64, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TOKENS = ROOT / ".allegro_tokens.json"
SANDBOX = os.environ.get("ALLEGRO_SANDBOX") == "1"
OAUTH = "https://allegro.pl.allegrosandbox.pl" if SANDBOX else "https://allegro.pl"
API = "https://api.allegro.pl.allegrosandbox.pl" if SANDBOX else "https://api.allegro.pl"
UA = "sportking-sync/v1.0 (+https://sportking.pl/sportking-app)"

env = {}
for l in open(ROOT / ".env"):
    if "=" in l and not l.startswith("#"):
        k, v = l.rstrip("\n").split("=", 1)
        env[k] = v.strip().strip('"').strip("'")
CID, CSEC = env.get("allegro_client_id"), env.get("allegro_client_secret")


def _basic():
    return "Basic " + base64.b64encode(f"{CID}:{CSEC}".encode()).decode()


def _post(url, data, auth=True):
    hdr = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA}
    if auth:
        hdr["Authorization"] = _basic()
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=hdr)
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {"__error": e.code, "__body": e.read().decode()}


def _save(tok):
    tok["_saved"] = int(time.time())
    TOKENS.write_text(json.dumps(tok, indent=2))


def _load():
    if not TOKENS.exists():
        sys.exit("no tokens yet — run: ./scripts/allegro/allegro_auth.py login")
    return json.loads(TOKENS.read_text())


def login():
    if not CID or not CSEC:
        sys.exit("missing allegro_client_id / allegro_client_secret in .env")
    d = _post(f"{OAUTH}/auth/oauth/device", {"client_id": CID})
    if "__error" in d:
        sys.exit(f"device init failed: {d}")
    print("\n=== Authorize the Inkontor account ===")
    print("1. Open this URL in your browser:")
    print("   ", d.get("verification_uri_complete") or d["verification_uri"])
    print(f"2. Log in as the sklep_Inkontor Allegro account and confirm (code: {d['user_code']}).")
    print("\nWaiting for you to authorize...", flush=True)
    interval, dc = d.get("interval", 5), d["device_code"]
    deadline = time.time() + d.get("expires_in", 600)
    while time.time() < deadline:
        time.sleep(interval)
        t = _post(f"{OAUTH}/auth/oauth/token",
                  {"grant_type": "urn:ietf:params:oauth:grant-type:device_code", "device_code": dc})
        if "access_token" in t:
            _save(t)
            print("Authorized — tokens saved to .allegro_tokens.json")
            return
        body = t.get("__body", "")
        if "authorization_pending" in body:
            continue
        if "slow_down" in body:
            interval += 2
            continue
        sys.exit(f"auth failed: {t}")
    sys.exit("timed out — run login again")


def _bearer_get(path):
    tok = _load()
    req = urllib.request.Request(f"{API}{path}", headers={
        "Authorization": f"Bearer {tok['access_token']}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "User-Agent": UA})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {"__error": e.code, "__body": e.read().decode()[:400]}


def refresh():
    tok = _load()
    if "refresh_token" not in tok:
        sys.exit("no refresh_token — run login")
    t = _post(f"{OAUTH}/auth/oauth/token",
              {"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
    if "access_token" in t:
        _save(t)
        print("access token refreshed")
    else:
        sys.exit(f"refresh failed: {t}")


def whoami():
    r = _bearer_get("/sale/offers?limit=1")
    if r.get("__error"):
        print("auth check FAILED:", r)
    else:
        print(f"auth OK — account has {r.get('totalCount', '?')} offers (read scope working)")


if __name__ == "__main__":
    {"login": login, "refresh": refresh, "whoami": whoami}.get(
        sys.argv[1] if len(sys.argv) > 1 else "login", login)()
