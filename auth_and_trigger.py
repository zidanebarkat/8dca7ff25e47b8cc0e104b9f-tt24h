#!/usr/bin/env python3
"""
TikTok 24/7 Stream - One-time setup helper

Run this once to:
1. Authenticate via QR code
2. Save session cookies locally
3. Print base64-encoded cookies for GitHub Actions
4. Optionally trigger the workflow
"""
import base64
import json
import sys
from pathlib import Path

# Add metasec to path
METASEC_PATH = Path(__file__).parent / "metasec"
sys.path.insert(0, str(METASEC_PATH))

from live import make_session, qr_login, gen_device_id


def main():
    import argparse
    parser = argparse.ArgumentParser(description="TikTok auth helper")
    parser.add_argument("--repo", default="zidanebarkat/8dca7ff25e47b8cc0e104b9f-tt24h", help="GitHub repo (owner/name)")
    parser.add_argument("--source", required=True, help="Source URL to stream")
    parser.add_argument("--title", default="Live Stream", help="TikTok stream title")
    parser.add_argument("--topic", default="5", help="Topic ID (5=Gaming)")
    parser.add_argument("--game", default="0", help="Game tag ID")
    parser.add_argument("--github-token", default="", help="GitHub PAT for auto-trigger")
    parser.add_argument("--overlay", default="", help="Overlay text")
    parser.add_argument("--cookies", default="", help="YouTube cookies file (for YouTube sources)")
    args = parser.parse_args()

    print("=" * 60)
    print("  TikTok 24/7 Stream - Auth Setup")
    print("=" * 60)

    # Step 1: QR Login
    print("\n[*] Step 1: Scan QR code with TikTok app")
    device_id = gen_device_id()
    s = make_session()
    cookies = qr_login(s, device_id, poll_timeout=180)
    if not cookies:
        print("[!] QR login failed")
        sys.exit(1)

    # Save cookies locally
    cookies_file = Path(__file__).parent / "session_cookies.json"
    with open(cookies_file, "w") as f:
        json.dump(cookies, f, indent=2)
    print(f"\n[+] Cookies saved to {cookies_file}")

    # Base64 encode for workflow
    cookies_b64 = base64.b64encode(json.dumps(cookies).encode()).decode()
    print(f"\n[+] Base64 cookies (copy this for workflow):")
    print(f"    {cookies_b64}")

    # Save to file for convenience
    b64_file = Path(__file__).parent / "cookies_b64.txt"
    with open(b64_file, "w") as f:
        f.write(cookies_b64)
    print(f"\n[+] Also saved to {b64_file}")

    # YouTube cookies if provided
    yt_b64 = ""
    if args.cookies:
        with open(args.cookies) as f:
            yt_b64 = base64.b64encode(f.read().encode()).decode()

    # Step 2: Trigger workflow
    if args.github_token:
        print("\n[*] Step 2: Triggering workflow...")
        import subprocess
        cmd = [
            "gh", "workflow", "run", "stream.yml",
            "-R", args.repo,
            "-f", f"source_url={args.source}",
            "-f", f"tiktok_session_cookies_b64={cookies_b64}",
            "-f", f"github_token={args.github_token}",
            "-f", f"overlay_text={args.overlay}",
            "-f", f"title={args.title}",
            "-f", f"topic={args.topic}",
            "-f", f"game_tag={args.game}",
            "-f", f"cookies_b64={yt_b64}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[+] Workflow triggered!")
        else:
            print(f"[!] Failed: {result.stderr}")
    else:
        print("\n[*] To trigger manually:")
        print(f"    gh workflow run stream.yml -R {args.repo} \\")
        print(f"      -f source_url={args.source} \\")
        print(f"      -f tiktok_session_cookies_b64=<cookies_b64> \\")
        print(f"      -f github_token=<PAT> \\")
        print(f"      -f title={args.title} \\")
        print(f"      -f topic={args.topic} \\")
        print(f"      -f game_tag={args.game}")

    print("\n" + "=" * 60)
    print("  DONE! The stream will run 24/7 automatically.")
    print("  Session cookies last ~30 days.")
    print("  When they expire, run this script again.")
    print("=" * 60)


if __name__ == "__main__":
    main()
