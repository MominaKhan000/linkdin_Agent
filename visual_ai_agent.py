"""
visual_ai_agent.py

Generates a LinkedIn post with an LLM (via Groq) and publishes it
automatically using Playwright.

Login flow:
  - Reuse a saved session (linkedin_storage_state.json) if present and valid.
  - Otherwise log in with credentials from accounts/multi_account.json.
  - Save the session again after a successful login.
  - Pause for manual input only if LinkedIn shows a CAPTCHA / checkpoint.
"""

import sys
import os
import time
import random
import json
import re
import logging
from pathlib import Path
from datetime import datetime

from config.setting import settings

OPENAI_MODEL = settings.OPENAI_MODEL
OPENAI_TEMPERATURE = settings.OPENAI_TEMPERATURE

# ============================================
# LOGGING
# ============================================

LOG_DIR = getattr(settings, "LOG_DIR", Path("log"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("linkedin_agent")
logger.setLevel(getattr(logging, str(getattr(settings, "LOG_LEVEL", "INFO")).upper(), logging.INFO))
if not logger.handlers:
    _stream = logging.StreamHandler(sys.stdout)
    _stream.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
    logger.addHandler(_stream)

    _file = logging.FileHandler(LOG_DIR / "linkedin_agent.log", encoding="utf-8")
    _file.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(_file)

# ============================================
# ANSI COLORS
# ============================================

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ============================================
# COMPUTER VISION ANIMATIONS
# ============================================

class VisionAnimation:
    def __init__(self):
        self.is_running = False
        self.frame_count = 0

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def scan_animation(self, duration=2):
        self.is_running = True
        start = time.time()
        width = 50

        while self.is_running and (time.time() - start) < duration:
            self.frame_count += 1
            pos = int((time.time() - start) / duration * width)
            scan_line = '█' * min(pos, width) + '░' * (width - min(pos, width))

            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.write(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║  🧠 NEURAL NETWORK SCANNING                                ║
║  ╔{'═' * 50}╗                                             ║
║  ║{scan_line}║  {self.frame_count}%                        ║
║  ╚{'═' * 50}╝                                             ║
{Colors.RESET}""")
            sys.stdout.flush()
            time.sleep(0.05)
        self.is_running = False

    def neural_network_visualization(self, duration=2):
        self.is_running = True
        start = time.time()
        layers = [10, 20, 30, 20, 10]

        while self.is_running and (time.time() - start) < duration:
            self.frame_count += 1
            visual_layers = []
            for i, size in enumerate(layers):
                neurons = ''.join(['█' if random.random() > 0.4 else '░' for _ in range(size)])
                visual_layers.append(f"  Layer {i+1}: {neurons}")

            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.write(f"""
{Colors.MAGENTA}╔══════════════════════════════════════════════════════════════╗
║  🧬 DEEP NEURAL NETWORK ACTIVATION                         ║
{chr(10).join([f'║  {layer}' for layer in visual_layers])}
║  🔥 Activation: {self.frame_count * 2}%                     ║
{Colors.RESET}""")
            sys.stdout.flush()
            time.sleep(0.1)
        self.is_running = False

    def ai_thinking_animation(self, duration=3):
        self.is_running = True
        start = time.time()
        thinking_states = ["🤔 Analyzing...", "🧠 Processing...", "💡 Generating...", "✨ Refining..."]
        state_index = 0
        last_state_change = time.time()

        while self.is_running and (time.time() - start) < duration:
            self.frame_count += 1
            if time.time() - last_state_change > 0.8:
                state_index = (state_index + 1) % len(thinking_states)
                last_state_change = time.time()

            progress = (time.time() - start) / duration
            bar = '█' * int(progress * 40) + '░' * (40 - int(progress * 40))

            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.write(f"""
{Colors.BLUE}╔══════════════════════════════════════════════════════════════╗
║  🧠 AI PROCESSING                                          ║
║  [{bar}] {int(progress * 100)}%                              ║
║  💭 Status: {thinking_states[state_index]}                  ║
{Colors.RESET}""")
            sys.stdout.flush()
            time.sleep(0.08)
        self.is_running = False

    def vision_system_demo(self, duration=2):
        self.is_running = True
        start = time.time()
        stages = ["📷 Capturing...", "🔍 Detecting...", "🧩 Matching...", "🎯 Recognizing..."]

        while self.is_running and (time.time() - start) < duration:
            self.frame_count += 1
            stage_index = min(int((time.time() - start) / duration * len(stages)), len(stages) - 1)

            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.write(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║  👁️  COMPUTER VISION PROCESSING                            ║
║  📊 Stage: {stages[stage_index]}                           ║
║  🕐 Frame: {self.frame_count}                               ║
{Colors.RESET}""")
            sys.stdout.flush()
            time.sleep(0.1)
        self.is_running = False

# ============================================
# POST GENERATOR
# ============================================

def generate_post_with_openai(project_details, tone="professional"):
    """Generate post using Groq API"""

    print(f"\n{Colors.YELLOW}🧠 Generating post with {OPENAI_MODEL}...{Colors.RESET}")

    prompt = f"""
You are a LinkedIn marketing expert. Create a professional LinkedIn post.

PROJECT DETAILS:
{project_details}

TONE: {tone}

Return ONLY JSON:
{{
    "hook": "Opening line",
    "body": "Main content (80-120 words)",
    "cta": "Call to action",
    "hashtags": ["#tag1", "#tag2", "#tag3"],
    "full_post": "Complete post"
}}
"""

    try:
        from groq import Groq
        client = Groq(api_key=settings.OPENAI_API_KEY)  # Reuses the same env var

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=500
        )

        content = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None

    except Exception as e:
        logger.error(f"Error generating post: {e}")
        print(f"{Colors.RED}❌ Error generating post: {e}{Colors.RESET}")
        return None

# ============================================
# SAVE POST TO FILES
# ============================================

def save_post_to_files(post_data, project_details, tone):
    """Save post to files"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    posts_dir = Path("posts")
    posts_dir.mkdir(exist_ok=True)

    json_file = posts_dir / f"post_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "project": project_details,
            "tone": tone,
            "model": OPENAI_MODEL,
            "post": post_data
        }, f, indent=2, ensure_ascii=False)
    print(f"{Colors.GREEN}💾 Saved JSON: {json_file}{Colors.RESET}")

    txt_file = posts_dir / f"post_{timestamp}.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("LINKEDIN AI AGENT - GENERATED POST\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tone: {tone}\n")
        f.write(f"Model: {OPENAI_MODEL}\n\n")
        f.write(post_data.get("full_post", ""))
        f.write("\n\n" + "-" * 60 + "\n")
        f.write(f"Hashtags: {', '.join(post_data.get('hashtags', []))}\n")
    print(f"{Colors.GREEN}💾 Saved Text: {txt_file}{Colors.RESET}")

# ============================================
# CREDENTIALS
# ============================================

def load_linkedin_credentials():
    """
    Load LinkedIn credentials from accounts/multi_account.json
    """

    cred_file = Path("accounts") / "multi_account.json"

    print(f"Looking for credentials: {cred_file.resolve()}")

    if not cred_file.exists():
        raise FileNotFoundError(
            f"Credentials file not found:\n{cred_file.resolve()}"
        )

    with open(cred_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support multiple formats

    if "accounts" in data:
        account = data["accounts"][0]

    elif "email" in data:
        account = data

    else:
        raise ValueError("Invalid credential file format.")

    email = account.get("email")
    password = account.get("password")

    if not email:
        raise ValueError("Email missing in credential file.")

    if not password:
        raise ValueError("Password missing in credential file.")

    print(f"Loaded account: {email}")

    return {
        "email": email,
        "password": password
    }

# ============================================
# LINKEDIN AUTOMATION HELPERS
# ============================================

STORAGE_STATE_PATH = Path("linkedin_storage_state.json")
FAILURE_SCREENSHOT_PATH = Path("failure.png")

LOGIN_URL = "https://www.linkedin.com/login"
FEED_URL = "https://www.linkedin.com/feed/"


def load_session(browser):
    """Create a browser context from a saved storage state, if one exists."""
    if not STORAGE_STATE_PATH.exists():
        return browser.new_context()

    try:
        with open(STORAGE_STATE_PATH, "r") as f:
            storage_state = json.load(f)
        context = browser.new_context(storage_state=storage_state)
        logger.info("Loaded saved LinkedIn session")
        print(f"{Colors.GREEN}✅ Loaded saved session!{Colors.RESET}")
        return context
    except Exception as e:
        logger.warning(f"Could not load saved session, starting fresh: {e}")
        return browser.new_context()


def save_session(context):
    """Persist the current browser context's storage state to disk."""
    try:
        storage_state = context.storage_state()
        with open(STORAGE_STATE_PATH, "w") as f:
            json.dump(storage_state, f)
        logger.info("Session saved")
        print(f"{Colors.GREEN}✅ Session saved!{Colors.RESET}")
    except Exception as e:
        logger.error(f"Could not save session: {e}")
        print(f"{Colors.RED}❌ Could not save session: {e}{Colors.RESET}")


def is_on_feed(page):
    return "feed" in page.url and "login" not in page.url


def needs_login(page):
    url = page.url
    return "login" in url or "checkpoint" in url or "challenge" in url


def handle_verification_checkpoint(page):
    """LinkedIn is asking for CAPTCHA / 2FA / device verification. This is the
    one point where manual intervention is unavoidable."""
    logger.warning("LinkedIn verification checkpoint detected")
    print(f"\n{Colors.YELLOW}⚠️ Verification checkpoint detected (CAPTCHA/2FA).{Colors.RESET}")
    print(f"{Colors.CYAN}📌 Complete the verification in the browser window.{Colors.RESET}")
    input(f"{Colors.GREEN}👉 Press ENTER once verification is complete...{Colors.RESET}")


def wait_for_feed_ready(page, timeout=20000):
    """Wait until the feed page has actually rendered, using a concrete
    element instead of network-idle (LinkedIn's feed never truly goes
    idle because of background chat/notification polling). Tries several
    strategies since LinkedIn's markup for this button changes over time."""
    _resolve_locator(page, [
        lambda: page.get_by_role("button", name="Start a post"),
        lambda: page.get_by_text("Start a post", exact=False),
        lambda: page.locator("button[aria-label='Start a post']"),
        lambda: page.locator("div.share-box-feed-entry__trigger"),
        lambda: page.locator("[data-control-name='share_via_linkedin']"),
    ], timeout=timeout, description="feed 'Start a post' entry point")


def _resolve_locator(page, strategies, timeout=20000, description="element"):
    """Try several ways of finding an element and return the first one that
    actually becomes visible. LinkedIn periodically changes its login page
    markup, so relying on a single CSS selector is fragile - this tries
    accessible-label lookups first (most stable) and falls back to CSS.

    `strategies` is a list of zero-arg callables, each returning a Locator.
    """
    deadline = time.time() + timeout / 1000
    last_error = None

    while time.time() < deadline:
        for make_locator in strategies:
            try:
                candidate = make_locator().first
                if candidate.count() > 0 and candidate.is_visible():
                    return candidate
            except Exception as e:
                last_error = e
        page.wait_for_timeout(300)

    raise RuntimeError(f"Could not locate {description} using any known strategy. Last error: {last_error}")


def login(page, email, password):
    """Log in to LinkedIn using robust locators. Raises on failure."""
    logger.info("Starting LinkedIn login")
    print(f"{Colors.CYAN}🔐 Logging in to LinkedIn...{Colors.RESET}")

    page.goto(LOGIN_URL, wait_until="domcontentloaded")

    if is_on_feed(page):
        # We still had a valid session - LinkedIn redirected us straight
        # back to the feed instead of showing a login form.
        logger.info("Already authenticated; login form was not needed")
        print(f"{Colors.GREEN}✅ Already logged in!{Colors.RESET}")
        return

    if needs_login(page) and ("checkpoint" in page.url or "challenge" in page.url):
        handle_verification_checkpoint(page)
        page.goto(FEED_URL, wait_until="domcontentloaded")
        if is_on_feed(page):
            return
        page.goto(LOGIN_URL, wait_until="domcontentloaded")

    # LinkedIn has redesigned this page more than once. Try the accessible
    # label first (most stable against markup changes), then fall back to
    # the older/newer attribute names.
    email_box = _resolve_locator(page, [
        lambda: page.get_by_label("Email or phone"),
        lambda: page.get_by_label("Email", exact=False),
        lambda: page.locator("input[name='session_key']"),
        lambda: page.locator("#username"),
        lambda: page.locator("input[autocomplete='username']"),
    ], description="email field")
    email_box.fill(email)

    password_box = _resolve_locator(page, [
        lambda: page.get_by_label("Password", exact=False),
        lambda: page.locator("input[name='session_password']"),
        lambda: page.locator("#password"),
        lambda: page.locator("input[autocomplete='current-password']"),
    ], description="password field")
    password_box.fill(password)

    if not email_box.input_value():
        raise RuntimeError("Email field is empty after fill()")
    if not password_box.input_value():
        raise RuntimeError("Password field is empty after fill()")

    logger.info("Credentials filled, submitting login form")

    submit_button = _resolve_locator(page, [
        lambda: page.get_by_role("button", name="Sign in"),
        lambda: page.locator("button[type='submit']"),
    ], description="sign in button")
    submit_button.click()

    page.wait_for_load_state("domcontentloaded")

    if "checkpoint" in page.url or "challenge" in page.url:
        handle_verification_checkpoint(page)
        page.goto(FEED_URL, wait_until="domcontentloaded")

    if not is_on_feed(page):
        # Give LinkedIn one more chance to redirect to the feed.
        page.wait_for_url("**/feed/**", timeout=30000)

    if not is_on_feed(page):
        raise RuntimeError(f"Login did not reach the feed (current url: {page.url})")

    logger.info("Login successful")
    print(f"{Colors.GREEN}✅ Login successful!{Colors.RESET}")


def ensure_logged_in(page, email, password):
    """Make sure `page` is authenticated and sitting on the feed."""
    page.goto(FEED_URL, wait_until="domcontentloaded")

    if is_on_feed(page):
        try:
            wait_for_feed_ready(page)
            print(f"{Colors.GREEN}✅ Already logged in!{Colors.RESET}")
            return
        except Exception:
            # We're on the feed URL but it didn't render as expected
            # (e.g. session is stale) - fall through to a fresh login.
            logger.warning("On feed URL but feed did not render; re-authenticating")

    login(page, email, password)
    wait_for_feed_ready(page)


def open_post_editor(page):
    """Click 'Start a post' and wait for the post editor to be ready."""
    logger.info("Opening post composer")
    print(f"{Colors.CYAN}📝 Opening post composer...{Colors.RESET}")

    start_button = _resolve_locator(page, [
        lambda: page.get_by_role("button", name="Start a post"),
        lambda: page.get_by_text("Start a post", exact=False),
        lambda: page.locator("button[aria-label='Start a post']"),
        lambda: page.locator("div.share-box-feed-entry__trigger"),
    ], description="'Start a post' button")
    start_button.click()

    editor = _resolve_locator(
    page,
    [
        lambda: page.locator("div[role='textbox']"),
        lambda: page.locator("div[contenteditable='true']"),
        lambda: page.locator(".ql-editor"),
        lambda: page.locator("[aria-label*='Text editor']"),
        lambda: page.locator("[data-placeholder]"),
    ],
    timeout=30000,
    description="LinkedIn post editor"
    )
    editor.wait_for(state="visible", timeout=15000)

    logger.info("Post editor ready")
    print(f"{Colors.GREEN}✅ Editor ready{Colors.RESET}")
    return editor


def publish_post(page, editor, post_content):
    logger.info("Filling post content")
    print(f"{Colors.CYAN}✍️ Writing post content...{Colors.RESET}")

    editor.click()
    editor.fill(post_content)

    page.wait_for_timeout(1500)

    if not editor.inner_text().strip():
        raise RuntimeError("Post editor is empty after fill()")

    # Find ONLY the visible Post button
    post_button = page.get_by_role("button", name="Post").last

    post_button.wait_for(
        state="visible",
        timeout=30000
    )

    post_button.scroll_into_view_if_needed()

    page.wait_for_timeout(1000)

    post_button.click(force=True)

    page.wait_for_timeout(5000)

    logger.info("Post published")
    print(f"{Colors.GREEN}✅ Post published!{Colors.RESET}")

def get_published_post_url(page):
    """Best-effort lookup of the URL for the post that was just published."""
    try:
        post_link = page.locator("a[href*='/feed/update/']").first
        if post_link.count() > 0:
            href = post_link.get_attribute("href")
            if href:
                return f"https://www.linkedin.com{href}" if href.startswith("/") else href
    except Exception as e:
        logger.warning(f"Could not resolve published post URL: {e}")
    return None


def record_published_post(post_content, post_url):
    try:
        posts_dir = Path("posts")
        posts_dir.mkdir(exist_ok=True)
        post_file = posts_dir / "published_posts.json"
        existing = []
        if post_file.exists():
            with open(post_file, "r") as f:
                existing = json.load(f)
        existing.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": post_content[:200] + "...",
            "url": post_url,
        })
        with open(post_file, "w") as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not record published post: {e}")

# ============================================
# LINKEDIN PUBLISHER (single implementation)
# ============================================

def publish_to_linkedin(post_content):
    """Log in (reusing a saved session when possible) and publish `post_content`
    to LinkedIn. Returns True on success, False on failure."""

    print(f"\n{Colors.YELLOW}📤 Auto-publishing to LinkedIn...{Colors.RESET}")
    print(f"{Colors.CYAN}🌐 Opening browser...{Colors.RESET}\n")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed")
        print(f"{Colors.RED}❌ Playwright not installed.{Colors.RESET}")
        print(f"{Colors.YELLOW}📌 Run: python -m playwright install{Colors.RESET}")
        return False

    try:
        creds = load_linkedin_credentials()
    except Exception as e:
        logger.error(f"Could not load credentials: {e}")
        print(f"{Colors.RED}❌ Could not load credentials: {e}{Colors.RESET}")
        return False

    if not creds:
        return False

    email = creds.get("email")
    password = creds.get("password")

    if not email or not password:
        logger.error("Email or password missing from credentials")
        print(f"{Colors.RED}❌ Email or password missing{Colors.RESET}")
        return False

    print(f"{Colors.GREEN}👤 Account: {email}{Colors.RESET}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=settings.LINKEDIN_HEADLESS, slow_mo=200, channel="chrome")
        except Exception:
            browser = p.chromium.launch(headless=settings.LINKEDIN_HEADLESS, slow_mo=200)
        context = load_session(browser)
        page = context.new_page()

        try:
            ensure_logged_in(page, email, password)
            save_session(context)

            editor = open_post_editor(page)
            publish_post(page, editor, post_content)

            post_url = get_published_post_url(page)
            if post_url:
                print(f"\n{Colors.CYAN}🌐 Showing your post...{Colors.RESET}")
                page.goto(post_url, wait_until="domcontentloaded")
                record_published_post(post_content, post_url)
                print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║  🎉 POST PUBLISHED SUCCESSFULLY!                                    ║
║  🔗 URL: {post_url}
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
                """)
            else:
                print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║  🎉 POST PUBLISHED SUCCESSFULLY!                                    ║
║  📝 Check your LinkedIn feed to see the post.                    ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
                """)

            return True

        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
            try:
                page.screenshot(path=str(FAILURE_SCREENSHOT_PATH))
                logger.info(f"Saved failure screenshot to {FAILURE_SCREENSHOT_PATH}")
                print(f"{Colors.YELLOW}📸 Saved failure screenshot: {FAILURE_SCREENSHOT_PATH}{Colors.RESET}")
            except Exception as shot_err:
                logger.error(f"Could not save failure screenshot: {shot_err}")
            return False

        finally:
            browser.close()

# ============================================
# MAIN
# ============================================

def run_visual_agent():
    vision = VisionAnimation()
    vision.clear_screen()

    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🤖  LINKEDIN AI AGENT - COMPUTER VISION MODE               ║
║                                                                  ║
║     👁️  Real-time Neural Processing & Pattern Recognition       ║
║     🧠  Model: {OPENAI_MODEL}                     ║
║     🚀  100% AUTOMATIC - Everything happens automatically!     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """)

    print(f"{Colors.YELLOW}📝 Enter project/topic details:{Colors.RESET}")
    print("   (Type your content, press Enter twice when done)\n")

    lines = []
    while True:
        line = input("   ")
        if line:
            lines.append(line)
        else:
            break

    project_details = "\n".join(lines) if lines else "LinkedIn AI Marketing Agent - Automated Content Generation Platform"
    if not lines:
        print(f"\n{Colors.YELLOW}Using default topic...{Colors.RESET}")

    print("\n🎨 Select tone:")
    print("   1. Professional")
    print("   2. Motivational")
    print("   3. Educational")
    print("   4. Casual")

    tone_map = {"1": "professional", "2": "motivational", "3": "educational", "4": "casual"}
    tone = tone_map.get(input("\nChoice (1-4): ").strip(), "professional")

    print(f"\n{Colors.BOLD}🔍 PHASE 1: NEURAL SCANNING{Colors.RESET}")
    vision.scan_animation(2)
    print(f"\n{Colors.GREEN}✅ Scan complete!{Colors.RESET}")
    time.sleep(0.5)

    print(f"\n{Colors.BOLD}🧠 PHASE 2: NEURAL PROCESSING{Colors.RESET}")
    vision.neural_network_visualization(2)
    print(f"\n{Colors.GREEN}✅ Processing complete!{Colors.RESET}")
    time.sleep(0.5)

    print(f"\n{Colors.BOLD}💭 PHASE 3: AI GENERATION{Colors.RESET}")
    vision.ai_thinking_animation(3)
    print(f"\n{Colors.GREEN}✅ Generation complete!{Colors.RESET}")
    time.sleep(0.5)

    print(f"\n{Colors.BOLD}🧠 Generating final output...{Colors.RESET}")
    post_data = generate_post_with_openai(project_details, tone)

    if not post_data:
        print(f"\n{Colors.RED}❌ Failed to generate post{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}✅ Post generated successfully!{Colors.RESET}")

    print(f"\n{Colors.BOLD}👁️  PHASE 4: COMPUTER VISION FINALIZATION{Colors.RESET}")
    vision.vision_system_demo(2)
    print(f"\n{Colors.GREEN}✅ Finalization complete!{Colors.RESET}")

    post_text = post_data.get("full_post", "")
    words = len(post_text.split())

    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║  📊 POST STATISTICS                                                ║
║  📝 Words: {words:>8}                                              ║
║  🏷️  Hashtags: {len(post_data.get('hashtags', [])):>8}                      ║
║  🧠 Model: {OPENAI_MODEL}                           ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """)

    save_post_to_files(post_data, project_details, tone)

    print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║  📝 GENERATED POST                                                   ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """)
    print(post_text)
    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}Hashtags: {', '.join(post_data.get('hashtags', []))}{Colors.RESET}")
    print(f"{Colors.YELLOW}CTA: {post_data.get('cta', 'N/A')}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")

    print(f"\n{Colors.GREEN}🚀 Auto-publishing in 3 seconds...{Colors.RESET}")
    print(f"{Colors.CYAN}🤖 Everything will happen automatically!{Colors.RESET}")
    time.sleep(3)

    success = publish_to_linkedin(post_text)

    if success:
        print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║  🎉 POST PUBLISHED SUCCESSFULLY!                                    ║
║  🤖 100% AUTOMATIC! No manual clicks needed!                    ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """)
    else:
        print(f"""
{Colors.RED}╔══════════════════════════════════════════════════════════════╗
║  ❌ POST PUBLISHING FAILED                                          ║
║  📌 Run: python -m playwright install                              ║
║  📌 Make sure accounts/multi_account.json has your credentials   ║
║  📌 Check failure.png for a screenshot of what went wrong        ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """)

    print(f"\n{Colors.GREEN}✅ Done!{Colors.RESET}")

if __name__ == "__main__":
    try:
        run_visual_agent()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏹️  Interrupted by user{Colors.RESET}")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()