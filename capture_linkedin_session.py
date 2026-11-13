"""
capture_linkedin_session.py

Run this ONCE (and again any time LinkedIn logs you out / the checkpoint
comes back). It opens a real browser window, you log in to LinkedIn by
hand — exactly like you normally would, including any 2FA/CAPTCHA — and
then it saves that authenticated session to linkedin_storage_state.json.

From then on, visual_ai_agent.py will detect that saved session, skip the
automated login form entirely, and go straight to posting. No more fighting
LinkedIn's login markup or bot-detection checkpoints on every run.

Usage:
    python capture_linkedin_session.py
"""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

STORAGE_STATE_PATH = Path("linkedin_storage_state.json")
LOGIN_URL = "https://www.linkedin.com/login"
FEED_URL = "https://www.linkedin.com/feed/"


def main():
    with sync_playwright() as p:
        # Prefer the real, installed Chrome over the bundled Chromium if
        # it's available - it carries a more typical browser fingerprint,
        # which combined with a human doing the actual typing makes this
        # look like an ordinary login rather than an automated one.
        try:
            browser = p.chromium.launch(headless=False, channel="chrome")
        except Exception:
            browser = p.chromium.launch(headless=False)

        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL, wait_until="domcontentloaded")

        print("\nA browser window has opened.")
        print("Log in to LinkedIn manually - email, password, and any")
        print("verification code or CAPTCHA LinkedIn asks for.")
        input("\nOnce you're looking at your LinkedIn feed, press ENTER here...")

        page.goto(FEED_URL, wait_until="domcontentloaded")

        if "feed" not in page.url:
            print(f"\nHmm, this doesn't look like the feed (current URL: {page.url}).")
            input("Finish logging in in the browser, then press ENTER again...")

        storage_state = context.storage_state()
        with open(STORAGE_STATE_PATH, "w") as f:
            json.dump(storage_state, f)

        print(f"\n✅ Session saved to {STORAGE_STATE_PATH.resolve()}")
        print("You can now run visual_ai_agent.py and it will skip the login form.")

        browser.close()


if __name__ == "__main__":
    main()