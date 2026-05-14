import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import json
from rapidfuzz import fuzz

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

visited = set()
pause_flag = False
stop_flag = False

def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def safe_request(url):
    try:
        return requests.get(url, timeout=6, verify=False)
    except:
        return None

def fuzzy_ai_detection(text):
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

def detect_ai_widgets(scripts):
    hits = []
    for s in scripts:
        src = s.get("src", "") or ""
        body = s.text or ""
        for sig in CHATBOT_SIGNATURES:
            if fuzz.partial_ratio(sig.lower(), src.lower()) > 80:
                hits.append(sig)
        if fuzzy_ai_detection(src) or fuzzy_ai_detection(body):
            hits.append("AI-Heuristic")
    return list(set(hits))


def crawl(url, depth, results_box, tree, parent_node, found_box):
    global pause_flag, stop_flag

    if stop_flag:
        return

    while pause_flag and not stop_flag:
        time.sleep(0.1)

    if depth == 0 or url in visited:
        return

    visited.add(url)
    r = safe_request(url)
    if not r:
        results_box.insert(tk.END, f"[ERROR] {url}\n", "error")
        return

    soup = BeautifulSoup(r.text, "html.parser")
    scripts = soup.find_all("script")

    detections = detect_ai_widgets(scripts)
    if detections:
        msg = f"[FOUND] {url}\n  - {', '.join(detections)}\n"
        results_box.insert(tk.END, msg, "found")
        found_box.insert(tk.END, msg, "found")
    else:
        msg = f"[OK] {url} — no detections\n"
        results_box.insert(tk.END, msg, "ok")

    node = tree.insert(parent_node, "end", text=url)

    links = soup.find_all("a", href=True)
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


def threaded_scan(url_entry, depth_entry, results_box, tree, found_box):
    def run():
        global stop_flag, pause_flag
        stop_flag = False
        pause_flag = False

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

        results_box.insert(tk.END, f"Starting scan: {url} (depth {depth})\n")
        root = tree.insert("", "end", text=url)
        crawl(url, depth, results_box, tree, root, found_box)
        results_box.insert(tk.END, "\nScan complete.\n")

    threading.Thread(target=run, daemon=True).start()


def run_gui():
    global pause_flag, stop_flag

    win = tk.Tk()
    win.title("AI/Chatbot Scanner - Enhanced")

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

    tk.Label(win, text="URL:").grid(row=1, column=0)
    url_entry = tk.Entry(win, width=50)
    url_entry.grid(row=1, column=1)

    tk.Label(win, text="Depth:").grid(row=2, column=0)
    depth_entry = tk.Entry(win, width=5)
    depth_entry.insert(0, "2")
    depth_entry.grid(row=2, column=1, sticky="w")

    start_btn = tk.Button(
        win,
        text="Start Scan",
        command=lambda: threaded_scan(url_entry, depth_entry, results_box, tree, found_box)
    )
    start_btn.grid(row=3, column=0)

    pause_btn = tk.Button(win, text="Pause", command=lambda: toggle_pause())
    pause_btn.grid(row=3, column=1)

    stop_btn = tk.Button(win, text="Stop", command=lambda: do_stop())
    stop_btn.grid(row=3, column=2)

    def toggle_pause():
        global pause_flag
        pause_flag = not pause_flag

    def do_stop():
        global stop_flag
        stop_flag = True

    win.mainloop()


if __name__ == "__main__":
    run_gui()
