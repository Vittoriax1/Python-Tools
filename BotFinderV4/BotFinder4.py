import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import json
from rapidfuzz import fuzz

# Try to import Playwright (optional)
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

requests.packages.urllib3.disable_warnings()

CHATBOT_SIGNATURES = [
    "widget.botpress.cloud", "botpress.com",
    "dialogflow", "google.cloud.dialogflow",
    "cdn.botframework.com", "webchat.botframework.com",
    "livechatinc.com", "tawk.to", "intercom.io",
    "api.intercom.io", "static.zdassets.com",
    "zdassets.com", "drift.com", "js.driftt.com",
    "salesforceliveagent.com", "boldchat.com",
    "freshchat.com", "snapengage.com", "olark.com",
    "userlike.com", "chatbot.com", "chatscript",
    "hubspot.net/livechat", "crisp.chat", "crisp.im",
    "landbot.io", "chatwoot.com", "helpshift.com",
    "zoho.com/salesiq", "snatchbot.me"
]

AI_KEYWORDS = [
    "model", "endpoint", "generate", "chat", "inference",
    "neural", "ai", "token", "stream", "completion",
    "assistant", "prompt", "websocket", "llm"
]

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
}

visited = set()
pause_flag = False
stop_flag = False
js_mode = False  # toggled from GUI

LEARNED_SIGNATURES = set()  # auto-learned candidate chatbot domains


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def safe_request(url):
    try:
        return requests.get(url, timeout=10, verify=False, headers=BROWSER_HEADERS)
    except:
        return None


def fuzzy_ai_detection(text):
    text = text or ""
    for keyword in AI_KEYWORDS:
        if fuzz.partial_ratio(keyword.lower(), text.lower()) > 80:
            return True
    if "{" in text and "}" in text:
        try:
            data = json.loads(text.strip())
            if isinstance(data, dict):
                return True
        except:
            pass
    return False


def detect_ai_widgets(scripts, network_urls=None):
    global LEARNED_SIGNATURES

    hits = []
    network_urls = network_urls or []

    # Script src + body
    for s in scripts:
        src = s.get("src", "") or ""
        body = s.text or ""
        for sig in CHATBOT_SIGNATURES:
            if fuzz.partial_ratio(sig.lower(), src.lower()) > 80:
                hits.append(sig)
        if fuzzy_ai_detection(src) or fuzzy_ai_detection(body):
            hits.append("AI-Heuristic")

    # Network URLs (requests, responses, websockets)
    for url in network_urls:
        matched_any = False
        for sig in CHATBOT_SIGNATURES:
            if fuzz.partial_ratio(sig.lower(), url.lower()) > 80:
                hits.append(f"NET:{sig}")
                matched_any = True

        # Heuristic on network URL
        if fuzzy_ai_detection(url):
            hits.append("NET-AI-Heuristic")
            matched_any = True

        # Auto-learn candidate chatbot domains
        if matched_any:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain and all(sig not in domain for sig in CHATBOT_SIGNATURES):
                LEARNED_SIGNATURES.add(domain)

    return list(set(hits))


def fetch_with_playwright(url):
    """Return (html, network_urls) using a headless browser."""
    if not PLAYWRIGHT_AVAILABLE:
        return None, []

    html = ""
    network_urls = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def on_request(request):
                network_urls.append(request.url)

            def on_response(response):
                try:
                    network_urls.append(response.url)
                except:
                    pass

            def on_websocket(ws):
                try:
                    network_urls.append(ws.url)
                except:
                    pass

            page.on("request", on_request)
            page.on("response", on_response)
            page.on("websocket", on_websocket)

            page.goto(url, wait_until="networkidle", timeout=25000)
            html = page.content()
            browser.close()
    except:
        return None, []

    return html, network_urls


def crawl(url, depth, results_box, tree, parent_node, found_box):
    global pause_flag, stop_flag, js_mode

    if stop_flag:
        return

    while pause_flag and not stop_flag:
        time.sleep(0.1)

    if depth == 0 or url in visited:
        return

    visited.add(url)

    # --- Always log that we are scanning this page ---
    results_box.insert(tk.END, f"[SCAN] {url}\n", "crawl")
    results_box.see(tk.END)

    # --- First pass: HTML via requests ---
    r = safe_request(url)
    if not r:
        results_box.insert(tk.END, f"[ERROR] {url}\n", "error")
        return

    soup_html = BeautifulSoup(r.text, "html.parser")
    scripts_html = soup_html.find_all("script")

    scripts_all = list(scripts_html)
    network_urls = []

    # --- Second pass: JS/Network via Playwright (if enabled) ---
    if js_mode and PLAYWRIGHT_AVAILABLE:
        results_box.insert(tk.END, f"[JS] Enhanced scan with headless browser: {url}\n", "crawl")
        results_box.see(tk.END)
        html_js, network_urls = fetch_with_playwright(url)
        if html_js:
            soup_js = BeautifulSoup(html_js, "html.parser")
            scripts_js = soup_js.find_all("script")
            scripts_all.extend(scripts_js)

    # --- Detection using combined data ---
    detections = detect_ai_widgets(scripts_all, network_urls)

    if detections:
        msg = f"[FOUND] {url}\n  - {', '.join(detections)}\n"
        results_box.insert(tk.END, msg, "found")
        found_box.insert(tk.END, msg, "found")
    else:
        msg = f"[OK] {url} — no detections\n"
        results_box.insert(tk.END, msg, "ok")

    node = tree.insert(parent_node, "end", text=url)

    # Crawl links (HTML DOM is enough to discover URLs)
    links = soup_html.find_all("a", href=True)
    domain = urlparse(url).netloc

    for link in links:
        if stop_flag:
            return
        while pause_flag and not stop_flag:
            time.sleep(0.1)

        new = urljoin(url, link['href'])
        parsed = urlparse(new)

        if parsed.netloc == domain and new not in visited:
            results_box.insert(tk.END, f"[crawl] → {new}\n", "crawl")
            results_box.see(tk.END)
            crawl(new, depth - 1, results_box, tree, node, found_box)


def threaded_scan(url_entry, depth_entry, results_box, tree, found_box, js_var):
    def run():
        global stop_flag, pause_flag, js_mode, LEARNED_SIGNATURES
        stop_flag = False
        pause_flag = False
        js_mode = bool(js_var.get()) and PLAYWRIGHT_AVAILABLE
        LEARNED_SIGNATURES.clear()

        url = normalize_url(url_entry.get().strip())
        try:
            depth = int(depth_entry.get().strip())
        except:
            depth = 1

        visited.clear()
        results_box.delete(1.0, tk.END)
        found_box.delete(1.0, tk.END)

        for i in tree.get_children():
            tree.delete(i)

        mode_label = "HTML + JS/Network" if js_mode else "HTML-only"
        if js_var.get() and not PLAYWRIGHT_AVAILABLE:
            results_box.insert(
                tk.END,
                "JS mode requested but Playwright is not installed. Running HTML-only.\n",
                "error"
            )

        results_box.insert(tk.END, f"Starting scan: {url} (depth {depth}) — Mode: {mode_label}\n")
        root = tree.insert("", "end", text=url)
        crawl(url, depth, results_box, tree, root, found_box)
        results_box.insert(tk.END, "\nScan complete.\n")

        if LEARNED_SIGNATURES:
            results_box.insert(
                tk.END,
                "\n[LEARNED] Candidate chatbot/AI-related domains observed:\n",
                "crawl"
            )
            for dom in sorted(LEARNED_SIGNATURES):
                results_box.insert(tk.END, f"  - {dom}\n", "crawl")

    threading.Thread(target=run, daemon=True).start()


def run_gui():
    global pause_flag, stop_flag

    win = tk.Tk()
    win.title("AI/Chatbot Scanner - Hybrid Enhanced")

    nb = ttk.Notebook(win)
    log_frame = ttk.Frame(nb)
    tree_frame = ttk.Frame(nb)
    found_frame = ttk.Frame(nb)

    nb.add(log_frame, text="Log")
    nb.add(tree_frame, text="Crawl Tree")
    nb.add(found_frame, text="Found Only")
    nb.grid(row=0, column=0, columnspan=3, sticky="nsew")

    results_box = scrolledtext.ScrolledText(log_frame, width=100, height=30)
    results_box.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame)
    tree.pack(fill="both", expand=True)

    found_box = scrolledtext.ScrolledText(found_frame, width=100, height=30)
    found_box.pack(fill="both", expand=True)

    # Color tags
    for box in (results_box,):
        box.tag_config("found", foreground="red")
        box.tag_config("ok", foreground="green")
        box.tag_config("crawl", foreground="blue")
        box.tag_config("error", foreground="orange")

    found_box.tag_config("found", foreground="red")

    tk.Label(win, text="URL:").grid(row=1, column=0, sticky="e")
    url_entry = tk.Entry(win, width=50)
    url_entry.grid(row=1, column=1, sticky="w")

    tk.Label(win, text="Depth:").grid(row=2, column=0, sticky="e")
    depth_entry = tk.Entry(win, width=5)
    depth_entry.insert(0, "8")
    depth_entry.grid(row=2, column=1, sticky="w")

    js_var = tk.BooleanVar(value=False)
    js_checkbox_label = "Enable JS/Network mode (Playwright)"
    if not PLAYWRIGHT_AVAILABLE:
        js_checkbox_label += " [Playwright not installed]"
    js_checkbox = tk.Checkbutton(win, text=js_checkbox_label, variable=js_var)
    js_checkbox.grid(row=3, column=0, columnspan=2, sticky="w")

    start_btn = tk.Button(
        win,
        text="Start Scan",
        command=lambda: threaded_scan(
            url_entry, depth_entry, results_box, tree, found_box, js_var
        )
    )
    start_btn.grid(row=4, column=0)

    pause_btn = tk.Button(win, text="Pause", command=lambda: toggle_pause())
    pause_btn.grid(row=4, column=1)

    stop_btn = tk.Button(win, text="Stop", command=lambda: do_stop())
    stop_btn.grid(row=4, column=2)

    def toggle_pause():
        global pause_flag
        pause_flag = not pause_flag

    def do_stop():
        global stop_flag
        stop_flag = True

    win.mainloop()


if __name__ == "__main__":
    run_gui()
