import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from rapidfuzz import fuzz
import re
import ssl
import socket

# Optional SOCKS support for TLS over Tor
try:
    import socks
    HAVE_SOCKS = True
except ImportError:
    HAVE_SOCKS = False

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
    "zoho.com/salesiq", "snatchbot.me", "tidio.co", "tidiochat.com",
    "smartsupp.com", "smartsuppcdn.com",
    "helpcrunch.com", "widget.helpcrunch.com",
    "kommunicate.io", "widget.kommunicate.io",
    "mobilemonkey.com", "bot.mobilemonkey.com",
    "manychat.com", "api.manychat.com",
    "giosg.com", "widget.giosg.com",
    "acquire.io", "widget.acquire.io",
    "heyday.ai", "heyday.ai/chat",
    "ada.support", "api.ada.support",
    "kustomerapp.com", "chat.kustomerapp.com",
    "gladly.com", "chat.gladly.com",
    "frontapp.com", "chat.frontapp.com",
    "birdeye.com", "birdeye.chat",
    "liveperson.net", "lpsnmedia.net",
    "livehelpnow.net",
    "purechat.com", "pcdn.co",
    "clickdesk.com",
    "zopim.com", "v2.zopim.com",
    "livezilla.net",
    "rocket.chat", "chat.rocket.chat",
    "messenger.com", "facebook.com/plugins/chat",
    "whatsapp.com/send", "wa.me",
    "telegram.org/js/telegram-widget.js",
    "line.me/R/ti/p",
    "wechat.com", "weixin.qq.com",
    "replain.cc",
    "flowxo.com",
    "botstar.com",
    "pandorabots.com",
    "liveagent.com", "liveagent.chat",
    "chatra.io", "static.chatra.io",
    "jivochat.com", "code.jivosite.com",
    "zendesk.com/chat", "zdassets.com/ekr/snippet.js",
    "freshworks.com/live-chat",
    "tiledesk.com",
    "whoson.com",
    "bold360.com",
    "genesys.com/cloud/chat",
    "verloop.io",
    "yellow.ai",
    "haptik.ai",
    "nlpcloud.io"
]

AI_ENDPOINT_SIGNATURES = [
    "api.openai.com", "openai.com",
    "anthropic.com", "api.anthropic.com",
    "cohere.ai", "api.cohere.ai",
    "huggingface.co", "inference.huggingface.co",
    "azure.com/openai", "openai.azure.com",
    "replicate.com", "api.replicate.com",
    "groq.com", "api.groq.com", "mistral.ai", "api.mistral.ai",
    "googleapis.com/ai", "generativelanguage.googleapis.com",
    "vertexai.googleapis.com",
    "gemini.google.com",
    "ai.google.dev",
    "bedrock.aws", "runtime.sagemaker.amazonaws.com",
    "runtime.a2i.aws",
    "perplexity.ai", "api.perplexity.ai",
    "stability.ai", "api.stability.ai",
    "runpod.io", "api.runpod.ai",
    "modal.com", "api.modal.com",
    "together.ai", "api.together.xyz",
    "fireworks.ai", "api.fireworks.ai",
    "sambanova.ai", "api.sambanova.ai",
    "nomic.ai", "api.nomic.ai",
    "voyageai.com", "api.voyageai.com",
    "deepgram.com", "api.deepgram.com",
    "assemblyai.com", "api.assemblyai.com",
    "elevenlabs.io", "api.elevenlabs.io",
    "speechmatics.com", "api.speechmatics.com",
    "rev.ai", "api.rev.ai",
    "ai21.com", "api.ai21.com",
    "aleph-alpha.com", "api.aleph-alpha.com",
    "coqui.ai", "api.coqui.ai",
    "openrouter.ai", "api.openrouter.ai",
    "inferrd.ai",
    "clarifai.com", "api.clarifai.com",
    "databricks.com/serving-endpoints",
    "baseten.co", "api.baseten.co",
    "forefront.ai", "api.forefront.ai",
    "textcortex.com", "api.textcortex.com",
    "writer.com", "api.writer.com",
    "hyperspace.ai",
    "ai.cloudflare.com",
    "nlpcloud.io", "api.nlpcloud.io",
    "cohere.com", "cohere.ai",
    "openchat.team",
    "lmsys.org", "api.lmsys.org",
    "huggingface.co/spaces",
    "replicate.delivery"
]

AI_KEYWORDS = [
    "llm", "completion", "completions",
    "chatcompletion", "chat-completion",
    "generate", "generation",
    "inference", "infer", "predict",
    "embedding", "embeddings",
    "tokenize", "detokenize",
    "assistant", "prompt", "system_prompt",
    "model_id", "model_name",
    "stream", "streaming",
    "ai_api", "ai_endpoint",
    "chatbot", "botengine",
    "nlp", "transformer"
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

# Tor proxy for Tor Browser on Kali (SOCKS5 127.0.0.1:9150)
TOR_PROXY = {
    "http": "socks5h://127.0.0.1:9150",
    "https": "socks5h://127.0.0.1:9150"
}

visited = set()
pause_flag = False
stop_flag = False
js_mode = False
debug_mode = False
hide_low_conf = False
tor_mode = False  # manual Tor toggle

LEARNED_SIGNATURES = set()

# Forced paths (hidden but common)
FORCED_PATHS = [
    "/wp-login.php",
    "/wp-admin/",
    "/wp-admin/admin-ajax.php",
    "/login/",
    "/admin/",
    "/user/login",
    "/dashboard/",
    "/cms/",
    "/backend/",
]

# Bruteforce common files
BRUTE_PATHS = [
    "/robots.txt",
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/readme.html",
    "/license.txt",
    "/wp-config.php",
    "/.env",
    "/.git/config",
    "/.well-known/security.txt",
]

# Directory probing
DIR_PROBE_PATHS = [
    "/wp-content/",
    "/wp-content/plugins/",
    "/wp-content/themes/",
    "/wp-includes/",
    "/wp-json/",
    "/.well-known/",
]

# Directory fuzzing wordlist
DIR_FUZZ_WORDS = [
    "admin", "backup", "old", "test", "dev", "staging",
    "api", "private", "config", "uploads", "files", "logs"
]

# Global file registry
files_found = {
    "html": set(),
    "js": set(),
    "css": set(),
    "img": set(),
    "json": set(),
    "api": set(),
    "ws": set(),
    "font": set(),
    "other": set()
}

# For flat list: (url, ftype, source_page)
files_flat = []

# Subdomain recon
subdomains_found = set()

# Tech stack fingerprinting + WAF/HTTP
tech_fingerprints = {
    "server": set(),
    "x_powered_by": set(),
    "frameworks": set(),
    "cms": set(),
    "js_libs": set(),
    "waf": set(),
    "http": set()
}

# Parameter discovery
parameters_found = {}  # param -> set(urls)

# JS endpoints (medium extraction)
js_endpoints = set()  # (endpoint, source_js)

# Forms
forms_found = []  # (page, action, method, inputs_str)

# TLS / SSL
discovered_domains = set()  # domains seen anywhere
tls_fingerprints = {}  # domain -> info dict


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def safe_request(url):
    try:
        if tor_mode:
            return requests.get(
                url,
                timeout=10,
                verify=False,
                headers=BROWSER_HEADERS,
                proxies=TOR_PROXY,
                allow_redirects=True
            )
        else:
            return requests.get(
                url,
                timeout=10,
                verify=False,
                headers=BROWSER_HEADERS,
                allow_redirects=True
            )
    except:
        return None


def fuzzy_ai_detection(text):
    text = text or ""
    count = 0
    for keyword in AI_KEYWORDS:
        if fuzz.partial_ratio(keyword.lower(), text.lower()) > 80:
            count += 1
    return count


def score_and_detect(scripts, network_urls=None):
    global LEARNED_SIGNATURES

    network_urls = network_urls or []
    detections = []
    debug_info = []
    score = 0

    for s in scripts:
        src = s.get("src", "") or ""
        body = s.text or ""

        for sig in CHATBOT_SIGNATURES:
            if fuzz.partial_ratio(sig.lower(), src.lower()) > 80:
                detections.append(sig)
                score += 40
                debug_info.append(f"Script src matched vendor: {sig}")

        src_hits = fuzzy_ai_detection(src)
        body_hits = fuzzy_ai_detection(body)
        total_hits = src_hits + body_hits
        if total_hits >= 3:
            score += 25
            detections.append("AI-Heuristic")
            debug_info.append(f"Script AI keyword cluster: {total_hits} hits")
        elif total_hits >= 1:
            score += 5
            debug_info.append(f"Script AI keyword weak hit: {total_hits} hits")

    for url in network_urls:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = (parsed.path or "").lower()

        matched_vendor = False

        for sig in CHATBOT_SIGNATURES:
            if fuzz.partial_ratio(sig.lower(), url.lower()) > 80:
                detections.append(f"NET:{sig}")
                score += 40
                matched_vendor = True
                debug_info.append(f"Network matched vendor: {sig}")
                break

        if not matched_vendor:
            for sig in AI_ENDPOINT_SIGNATURES:
                if sig in domain or sig in url.lower():
                    detections.append(f"AI-ENDPOINT:{sig}")
                    score += 40
                    matched_vendor = True
                    debug_info.append(f"Network matched AI endpoint: {sig}")
                    break

        if not matched_vendor:
            hits = fuzzy_ai_detection(url)
            if hits >= 3:
                detections.append("NET-AI-Heuristic")
                score += 20
                debug_info.append(f"Network AI keyword cluster: {hits} hits")
            elif hits >= 1:
                score += 5
                debug_info.append(f"Network AI keyword weak hit: {hits} hits")

        suspicious_tokens = ["chat", "bot", "assistant", "ai", "inference", "generate"]
        if any(tok in path for tok in suspicious_tokens):
            score += 10
            debug_info.append(f"Suspicious path: {path}")
            if not matched_vendor:
                parsed = urlparse(url)
                domain = parsed.netloc
                if domain:
                    LEARNED_SIGNATURES.add(domain)

    detections = list(set(detections))
    return detections, score, debug_info


def fetch_with_playwright(url):
    try:
        from playwright.sync_api import sync_playwright
        PLAYWRIGHT_AVAILABLE = True
    except ImportError:
        PLAYWRIGHT_AVAILABLE = False

    if not PLAYWRIGHT_AVAILABLE:
        return None, [], []

    html = ""
    network_urls = []
    resource_info = []  # (url, mime_type)

    try:
        with sync_playwright() as p:
            if tor_mode:
                browser = p.chromium.launch(
                    headless=True,
                    proxy={"server": "socks5://127.0.0.1:9150"}
                )
            else:
                browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            def on_request(request):
                network_urls.append(request.url)

            def on_response(response):
                try:
                    resource_info.append((response.url, response.headers.get("content-type", "")))
                except:
                    pass

            def on_websocket(ws):
                try:
                    network_urls.append(ws.url)
                    resource_info.append((ws.url, "websocket"))
                except:
                    pass

            page.on("request", on_request)
            page.on("response", on_response)
            page.on("websocket", on_websocket)

            page.goto(url, wait_until="networkidle", timeout=25000)
            html = page.content()
            browser.close()
    except:
        return None, [], []

    return html, network_urls, resource_info


def is_same_domain(base, new):
    return urlparse(base).netloc == urlparse(new).netloc


def classify_file(url, mime_type=""):
    url = url.split("#")[0].split("?")[0]
    parsed = urlparse(url)
    path = parsed.path or ""
    lower = path.lower()

    if lower.endswith((".html", ".htm", "/")) or mime_type.startswith("text/html"):
        return "html"
    if lower.endswith(".js") or "javascript" in mime_type:
        return "js"
    if lower.endswith(".css") or "text/css" in mime_type:
        return "css"
    if lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")) or mime_type.startswith("image/"):
        return "img"
    if lower.endswith(".json") or "application/json" in mime_type:
        return "json"
    if lower.endswith((".woff", ".woff2", ".ttf", ".otf")) or mime_type.startswith("font/"):
        return "font"
    if parsed.scheme in ("ws", "wss") or "websocket" in mime_type.lower():
        return "ws"
    if "/api/" in lower or "/api-" in lower or "/v1/" in lower or "/v2/" in lower:
        return "api"
    if any(tok in lower for tok in ["/chat", "/inference", "/generate", "/completion"]):
        return "api"
    return "other"


def register_file(url, source_page, mime_type=""):
    global discovered_domains
    ftype = classify_file(url, mime_type)
    files_found[ftype].add(url)
    files_flat.append((url, ftype, source_page))
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        domain = parsed.netloc.split(":")[0]
        discovered_domains.add(domain)


def discover_links_and_files(url, soup):
    links = set()

    for tag in soup.find_all("a", href=True):
        href = urljoin(url, tag["href"])
        links.add(href)
        register_file(href, url)

    for tag in soup.find_all("script", src=True):
        src = urljoin(url, tag["src"])
        links.add(src)
        register_file(src, url)

    for tag in soup.find_all("link", href=True):
        href = urljoin(url, tag["href"])
        links.add(href)
        register_file(href, url)

    for tag in soup.find_all("img", src=True):
        src = urljoin(url, tag["src"])
        register_file(src, url)

    for tag in soup.find_all("iframe", src=True):
        src = urljoin(url, tag["src"])
        links.add(src)
        register_file(src, url)

    for tag in soup.find_all("form", action=True):
        action = urljoin(url, tag["action"])
        links.add(action)
        register_file(action, url)

        method = (tag.get("method") or "GET").upper()
        inputs = []
        for inp in tag.find_all("input"):
            name = inp.get("name") or inp.get("id") or ""
            if name:
                inputs.append(name)
        inputs_str = ", ".join(inputs)
        forms_found.append((url, action, method, inputs_str))

    return links


def fingerprint_tech(url, response, soup):
    server = response.headers.get("Server")
    if server:
        tech_fingerprints["server"].add(server)

    x_powered = response.headers.get("X-Powered-By")
    if x_powered:
        tech_fingerprints["x_powered_by"].add(x_powered)

    for meta in soup.find_all("meta"):
        name = (meta.get("name") or "").lower()
        gen = (meta.get("content") or "").lower()
        if "generator" in name or "generator" in gen:
            tech_fingerprints["cms"].add(meta.get("content", ""))

    for script in soup.find_all("script", src=True):
        src = script["src"].lower()
        if "jquery" in src:
            tech_fingerprints["js_libs"].add("jQuery")
        if "react" in src:
            tech_fingerprints["js_libs"].add("React")
        if "vue" in src:
            tech_fingerprints["js_libs"].add("Vue")
        if "angular" in src:
            tech_fingerprints["js_libs"].add("Angular")

    text = response.text.lower()
    if "wp-content" in text or "wp-includes" in text:
        tech_fingerprints["cms"].add("WordPress")

    # WAF detection
    headers = {k.lower(): v for k, v in response.headers.items()}
    server_l = (server or "").lower()

    if "cloudflare" in server_l or "cf-ray" in headers or "cf-cache-status" in headers:
        tech_fingerprints["waf"].add("Cloudflare")
    if "akamai" in server_l or any("akamai" in k for k in headers.keys()):
        tech_fingerprints["waf"].add("Akamai")
    if "incapsula" in server_l or "incapsula" in str(headers):
        tech_fingerprints["waf"].add("Imperva/Incapsula")
    if "sucuri" in str(headers):
        tech_fingerprints["waf"].add("Sucuri")
    if "aws" in server_l and "x-amzn" in str(headers):
        tech_fingerprints["waf"].add("AWS WAF")
    if "f5" in server_l or "big-ip" in str(headers).lower():
        tech_fingerprints["waf"].add("F5")
    if "mod_security" in server_l or "modsecurity" in str(headers).lower():
        tech_fingerprints["waf"].add("ModSecurity")

    # HTTP fingerprint
    try:
        length = len(response.content)
    except:
        length = 0
    tech_fingerprints["http"].add(f"{url} -> {response.status_code}, len={length}")


def discover_parameters(url):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    for param, values in qs.items():
        if param not in parameters_found:
            parameters_found[param] = set()
        parameters_found[param].add(url)


def crawl(url, depth, results_box, tree, parent_node, found_box, scanned_tree,
          files_tree, files_grouped_tabs):
    global pause_flag, stop_flag, js_mode, debug_mode, hide_low_conf

    if stop_flag:
        return

    while pause_flag and not stop_flag:
        time.sleep(0.1)

    if depth == 0 or url in visited:
        return

    visited.add(url)

    results_box.insert(tk.END, f"[SCAN] {url}\n", "crawl")
    results_box.see(tk.END)

    r = safe_request(url)
    if not r:
        results_box.insert(tk.END, f"[ERROR] {url}\n", "error")
        scanned_tree.insert("", "end", values=(url, "ERROR", 0))
        return

    register_file(url, url, r.headers.get("content-type", ""))

    soup_html = BeautifulSoup(r.text, "html.parser")
    scripts_html = soup_html.find_all("script")

    fingerprint_tech(url, r, soup_html)
    discover_parameters(url)

    scripts_all = list(scripts_html)
    network_urls = []
    resource_info = []

    if js_mode:
        results_box.insert(tk.END, f"[JS] Enhanced scan with headless browser: {url}\n", "crawl")
        results_box.see(tk.END)
        html_js, network_urls, resource_info = fetch_with_playwright(url)
        if html_js:
            soup_js = BeautifulSoup(html_js, "html.parser")
            scripts_js = soup_js.find_all("script")
            scripts_all.extend(scripts_js)
        results_box.insert(tk.END, f"[NET] Captured {len(network_urls)} network URLs\n", "crawl")
        results_box.see(tk.END)

        for res_url, mime in resource_info:
            register_file(res_url, url, mime)
            discover_parameters(res_url)

    detections, score, debug_info = score_and_detect(scripts_all, network_urls)

    has_vendor = any(
        not d.startswith("AI-") and not d.startswith("NET-AI") and not d.startswith("AI-ENDPOINT")
        for d in detections
    )
    is_low_conf = (score < 30 and not has_vendor)

    if detections and not (hide_low_conf and is_low_conf):
        status = "FOUND"
        msg = f"[FOUND] {url}\n  - {', '.join(detections)}\n  - Score: {score}\n"
        results_box.insert(tk.END, msg, "found")
        found_box.insert(tk.END, msg, "found")
    else:
        status = "OK" if not detections or is_low_conf else "FOUND"
        msg = f"[OK] {url} — score {score}, detections: {', '.join(detections) or 'none'}\n"
        results_box.insert(tk.END, msg, "ok")

    scanned_tree.insert("", "end", values=(url, status, score))

    if debug_mode and debug_info:
        results_box.insert(tk.END, "  [DEBUG]\n", "crawl")
        for line in debug_info:
            results_box.insert(tk.END, f"    - {line}\n", "crawl")

    node = tree.insert(parent_node, "end", text=url)

    links = discover_links_and_files(url, soup_html)
    for new in links:
        if stop_flag:
            return
        while pause_flag and not stop_flag:
            time.sleep(0.1)

        if is_same_domain(url, new) and new not in visited:
            results_box.insert(tk.END, f"[crawl] → {new}\n", "crawl")
            results_box.see(tk.END)
            crawl(new, depth - 1, results_box, tree, node, found_box,
                  scanned_tree, files_tree, files_grouped_tabs)

    rebuild_files_views(files_tree, files_grouped_tabs)


def rebuild_files_views(files_tree, files_grouped_tabs):
    for i in files_tree.get_children():
        files_tree.delete(i)

    def add_to_tree(path):
        parts = [p for p in path.split("/") if p]
        if not parts:
            return
        parent = ""
        for part in parts:
            existing = None
            for child in files_tree.get_children(parent):
                if files_tree.item(child, "text") == part:
                    existing = child
                    break
            if existing is None:
                existing = files_tree.insert(parent, "end", text=part)
            parent = existing

    all_files = set()
    for ftype, urls in files_found.items():
        for u in urls:
            parsed = urlparse(u)
            path = parsed.path or "/"
            all_files.add(path)

    for path in sorted(all_files):
        add_to_tree(path)

    for ftype, widget in files_grouped_tabs.items():
        treeview = widget
        for i in treeview.get_children():
            treeview.delete(i)
        for url in sorted(files_found[ftype]):
            treeview.insert("", "end", values=(url, ftype))


def subdomain_recon(base_url, results_box, subdomain_tree):
    parsed = urlparse(base_url)
    root_domain = parsed.netloc.split(":")[0]
    parts = root_domain.split(".")
    if len(parts) < 2:
        return

    base_root = ".".join(parts[-2:])
    common_subs = ["www", "dev", "test", "staging", "api", "admin", "beta", "old"]

    results_box.insert(tk.END, f"\n[SUBDOMAIN] Starting light subdomain recon on *.{base_root}\n", "crawl")

    for sub in common_subs:
        if stop_flag:
            break
        host = f"{sub}.{base_root}"
        url = f"{parsed.scheme}://{host}"
        r = safe_request(url)
        if r and r.status_code < 500:
            subdomains_found.add(url)
            results_box.insert(tk.END, f"[SUBDOMAIN] Found: {url} (status {r.status_code})\n", "ok")
            subdomain_tree.insert("", "end", values=(url, r.status_code))


def directory_fuzz(base_url, results_box, dir_tree):
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    results_box.insert(tk.END, "\n[DIR-FUZZ] Fuzzing common directories...\n", "crawl")

    for word in DIR_FUZZ_WORDS:
        if stop_flag:
            break
        target = f"{base}/{word}/"
        r = safe_request(target)
        if r and r.status_code not in (404, 400):
            results_box.insert(tk.END, f"[DIR-FUZZ] {target} (status {r.status_code})\n", "ok")
            dir_tree.insert("", "end", values=(target, r.status_code))


def extract_js_endpoints_for_all(results_box, js_tree):
    url_pattern = re.compile(r'https?://[^\s\'"<>]+')
    rel_pattern = re.compile(r'["\'](/[^"\']+)["\']')

    for js_url in sorted(files_found["js"]):
        if stop_flag:
            break
        r = safe_request(js_url)
        if not r or r.status_code >= 400:
            continue
        text = r.text

        abs_urls = url_pattern.findall(text)
        for u in abs_urls:
            js_endpoints.add((u, js_url))

        rel_urls = rel_pattern.findall(text)
        for path in rel_urls:
            full = urljoin(js_url, path)
            js_endpoints.add((full, js_url))

    for endpoint, src in sorted(js_endpoints):
        js_tree.insert("", "end", values=(endpoint, src))


def tls_fingerprint_domain(domain):
    try:
        ctx = ssl.create_default_context()
        if tor_mode and HAVE_SOCKS:
            s = socks.socksocket()
            s.set_proxy(socks.SOCKS5, "127.0.0.1", 9150)
            s.settimeout(10)
            s.connect((domain, 443))
            sslsock = ctx.wrap_socket(s, server_hostname=domain)
        else:
            s = socket.create_connection((domain, 443), timeout=10)
            sslsock = ctx.wrap_socket(s, server_hostname=domain)

        cert = sslsock.getpeercert()
        sslsock.close()
    except:
        return None

    issuer = ""
    try:
        issuer_parts = cert.get("issuer", [])
        if issuer_parts:
            issuer = ", ".join("=".join(x) for x in issuer_parts[0])
    except:
        issuer = ""

    not_after = cert.get("notAfter", "")
    sans = []
    try:
        for t, val in cert.get("subjectAltName", []):
            if t == "DNS":
                sans.append(val)
    except:
        pass

    return {
        "domain": domain,
        "issuer": issuer,
        "expires": not_after,
        "san": ", ".join(sans)
    }


def tls_scan_all_domains(results_box, tls_tree):
    for dom in sorted(discovered_domains):
        if stop_flag:
            break
        if dom in tls_fingerprints:
            info = tls_fingerprints[dom]
        else:
            results_box.insert(tk.END, f"[TLS] Fingerprinting {dom}...\n", "crawl")
            results_box.see(tk.END)
            info = tls_fingerprint_domain(dom)
            if not info:
                continue
            tls_fingerprints[dom] = info

        tls_tree.insert(
            "",
            "end",
            values=(info["domain"], info["issuer"], info["expires"], info["san"])
        )


def threaded_scan(url_entry, depth_entry, results_box, tree, found_box, scanned_tree,
                  files_tree, files_grouped_tabs, files_flat_tree,
                  subdomain_tree, dir_tree, js_tree, forms_tree,
                  waf_tree, tls_tree, param_tree,
                  js_var, debug_var, hide_low_var, tor_var):
    def run():
        global stop_flag, pause_flag, js_mode, debug_mode, hide_low_conf, LEARNED_SIGNATURES
        global files_found, files_flat, subdomains_found, tech_fingerprints, parameters_found
        global tor_mode, js_endpoints, forms_found, discovered_domains, tls_fingerprints

        stop_flag = False
        pause_flag = False
        js_mode = bool(js_var.get())
        debug_mode = bool(debug_var.get())
        hide_low_conf = bool(hide_low_var.get())
        tor_mode = bool(tor_var.get())
        LEARNED_SIGNATURES.clear()

        files_found = {
            "html": set(),
            "js": set(),
            "css": set(),
            "img": set(),
            "json": set(),
            "api": set(),
            "ws": set(),
            "font": set(),
            "other": set()
        }
        files_flat = []
        subdomains_found = set()
        tech_fingerprints = {
            "server": set(),
            "x_powered_by": set(),
            "frameworks": set(),
            "cms": set(),
            "js_libs": set(),
            "waf": set(),
            "http": set()
        }
        parameters_found = {}
        js_endpoints = set()
        forms_found = []
        discovered_domains = set()
        tls_fingerprints = {}

        url = normalize_url(url_entry.get().strip())
        try:
            depth = int(depth_entry.get().strip())
        except:
            depth = 1

        parsed = urlparse(url)
        if parsed.hostname and parsed.hostname.endswith(".onion") and not tor_mode:
            results_box.insert(
                tk.END,
                "[WARNING] .onion domain detected. Enable Tor Mode to scan this site reliably.\n",
                "error"
            )

        visited.clear()
        results_box.delete(1.0, tk.END)
        found_box.delete(1.0, tk.END)

        for widget in (tree, scanned_tree, files_tree, files_flat_tree,
                       subdomain_tree, dir_tree, js_tree, forms_tree,
                       waf_tree, tls_tree, param_tree):
            for i in widget.get_children():
                widget.delete(i)
        for ftype, widget in files_grouped_tabs.items():
            tv = widget
            for i in tv.get_children():
                tv.delete(i)

        mode_label = "HTML + JS/Network" if js_mode else "HTML-only"
        tor_label = "Tor Mode ON" if tor_mode else "Tor Mode OFF"

        results_box.insert(
            tk.END,
            f"Starting scan: {url} (depth {depth}) — Mode: {mode_label} — {tor_label}\n",
            "crawl"
        )
        root = tree.insert("", "end", text=url)

        # Normal crawl
        crawl(url, depth, results_box, tree, root, found_box,
              scanned_tree, files_tree, files_grouped_tabs)

        # Recon: forced paths, bruteforce, directory probing
        base = url.rstrip("/")
        recon_targets = set()

        for p in FORCED_PATHS:
            recon_targets.add(base + p)
        for p in BRUTE_PATHS:
            recon_targets.add(base + p)
        for p in DIR_PROBE_PATHS:
            recon_targets.add(base + p)

        results_box.insert(tk.END, "\n[RECON] Probing common hidden/admin paths...\n", "crawl")

        recon_root = tree.insert("", "end", text="[RECON]")
        for target in sorted(recon_targets):
            if stop_flag:
                break
            if target in visited:
                continue
            results_box.insert(tk.END, f"[RECON-SCAN] {target}\n", "crawl")
            results_box.see(tk.END)
            crawl(target, 1, results_box, tree, recon_root, found_box,
                  scanned_tree, files_tree, files_grouped_tabs)

        # Subdomain recon
        subdomain_recon(url, results_box, subdomain_tree)

        # Directory fuzzing
        directory_fuzz(url, results_box, dir_tree)

        # JS endpoint extraction
        results_box.insert(tk.END, "\n[JS-ENDPOINTS] Extracting endpoints from JS files...\n", "crawl")
        extract_js_endpoints_for_all(results_box, js_tree)

        # Forms tab
        for page, action, method, inputs_str in forms_found:
            forms_tree.insert("", "end", values=(page, action, method, inputs_str))

        # WAF/HTTP tab (tech_fingerprints)
        for category, values in tech_fingerprints.items():
            for v in values:
                waf_tree.insert("", "end", values=(category, v))

        # TLS/SSL fingerprinting for all discovered domains
        results_box.insert(tk.END, "\n[TLS] Fingerprinting discovered domains...\n", "crawl")
        tls_scan_all_domains(results_box, tls_tree)

        # Populate flat files view
        for furl, ftype, src in files_flat:
            files_flat_tree.insert("", "end", values=(furl, ftype, src))

        # Populate parameter discovery view
        for param, urls in parameters_found.items():
            param_tree.insert("", "end", values=(param, len(urls), ", ".join(list(urls)[:5])))

        if LEARNED_SIGNATURES:
            results_box.insert(
                tk.END,
                "\n[LEARNED] Candidate chatbot/AI-related domains observed:\n",
                "crawl"
            )
            for dom in sorted(LEARNED_SIGNATURES):
                results_box.insert(tk.END, f"  - {dom}\n", "crawl")

        results_box.insert(tk.END, "\nScan complete.\n", "crawl")

    threading.Thread(target=run, daemon=True).start()


def run_gui():
    global pause_flag, stop_flag

    win = tk.Tk()
    win.title("AI/Chatbot & Recon Mapper (Tor-capable)")

    nb = ttk.Notebook(win)

    tree_frame = ttk.Frame(nb)
    scanned_frame = ttk.Frame(nb)
    found_frame = ttk.Frame(nb)
    files_tree_frame = ttk.Frame(nb)
    files_flat_frame = ttk.Frame(nb)
    files_grouped_frame = ttk.Frame(nb)

    subdomain_frame = ttk.Frame(nb)
    dir_frame = ttk.Frame(nb)
    js_endpoints_frame = ttk.Frame(nb)
    forms_frame = ttk.Frame(nb)
    waf_frame = ttk.Frame(nb)
    tls_frame = ttk.Frame(nb)
    param_frame = ttk.Frame(nb)

    log_frame = ttk.Frame(nb)

    nb.add(tree_frame, text="Crawl Tree")
    nb.add(scanned_frame, text="Scanned Pages")
    nb.add(found_frame, text="Found Only")
    nb.add(files_tree_frame, text="Files Tree")
    nb.add(files_flat_frame, text="Files Flat")
    nb.add(files_grouped_frame, text="Files Grouped")

    nb.add(subdomain_frame, text="Subdomains")
    nb.add(dir_frame, text="Dir Fuzz")
    nb.add(js_endpoints_frame, text="JS Endpoints")
    nb.add(forms_frame, text="Forms")
    nb.add(waf_frame, text="WAF / HTTP")
    nb.add(tls_frame, text="TLS / SSL")
    nb.add(param_frame, text="Parameters")

    nb.add(log_frame, text="Log")

    nb.grid(row=0, column=0, columnspan=4, sticky="nsew")

    results_box = scrolledtext.ScrolledText(log_frame, width=100, height=30)
    results_box.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame)
    tree.pack(fill="both", expand=True)

    found_box = scrolledtext.ScrolledText(found_frame, width=100, height=30)
    found_box.pack(fill="both", expand=True)

    scanned_tree = ttk.Treeview(scanned_frame, columns=("url", "status", "score"), show="headings")
    scanned_tree.heading("url", text="URL")
    scanned_tree.heading("status", text="Status")
    scanned_tree.heading("score", text="Score")
    scanned_tree.column("url", width=500)
    scanned_tree.column("status", width=80)
    scanned_tree.column("score", width=60)
    scanned_tree.pack(fill="both", expand=True)

    files_tree = ttk.Treeview(files_tree_frame)
    files_tree.pack(fill="both", expand=True)

    files_flat_tree = ttk.Treeview(files_flat_frame, columns=("url", "type", "source"), show="headings")
    files_flat_tree.heading("url", text="File URL")
    files_flat_tree.heading("type", text="Type")
    files_flat_tree.heading("source", text="Source Page")
    files_flat_tree.column("url", width=500)
    files_flat_tree.column("type", width=80)
    files_flat_tree.column("source", width=300)
    files_flat_tree.pack(fill="both", expand=True)

    files_grouped_nb = ttk.Notebook(files_grouped_frame)
    files_grouped_nb.pack(fill="both", expand=True)

    files_grouped_tabs = {}
    for ftype in ["html", "js", "css", "img", "json", "api", "ws", "font", "other"]:
        frame = ttk.Frame(files_grouped_nb)
        files_grouped_nb.add(frame, text=ftype.upper())
        tv = ttk.Treeview(frame, columns=("url", "type"), show="headings")
        tv.heading("url", text="File URL")
        tv.heading("type", text="Type")
        tv.column("url", width=600)
        tv.column("type", width=80)
        tv.pack(fill="both", expand=True)
        files_grouped_tabs[ftype] = tv

    subdomain_tree = ttk.Treeview(subdomain_frame, columns=("url", "status"), show="headings")
    subdomain_tree.heading("url", text="Subdomain URL")
    subdomain_tree.heading("status", text="Status")
    subdomain_tree.column("url", width=500)
    subdomain_tree.column("status", width=80)
    subdomain_tree.pack(fill="both", expand=True)

    dir_tree = ttk.Treeview(dir_frame, columns=("url", "status"), show="headings")
    dir_tree.heading("url", text="Directory URL")
    dir_tree.heading("status", text="Status")
    dir_tree.column("url", width=500)
    dir_tree.column("status", width=80)
    dir_tree.pack(fill="both", expand=True)

    js_tree = ttk.Treeview(js_endpoints_frame, columns=("endpoint", "source"), show="headings")
    js_tree.heading("endpoint", text="Endpoint URL")
    js_tree.heading("source", text="Source JS File")
    js_tree.column("endpoint", width=600)
    js_tree.column("source", width=400)
    js_tree.pack(fill="both", expand=True)

    forms_tree = ttk.Treeview(forms_frame, columns=("page", "action", "method", "inputs"), show="headings")
    forms_tree.heading("page", text="Page URL")
    forms_tree.heading("action", text="Action URL")
    forms_tree.heading("method", text="Method")
    forms_tree.heading("inputs", text="Inputs")
    forms_tree.column("page", width=400)
    forms_tree.column("action", width=400)
    forms_tree.column("method", width=80)
    forms_tree.column("inputs", width=400)
    forms_tree.pack(fill="both", expand=True)

    waf_tree = ttk.Treeview(waf_frame, columns=("category", "value"), show="headings")
    waf_tree.heading("category", text="Category")
    waf_tree.heading("value", text="Value")
    waf_tree.column("category", width=150)
    waf_tree.column("value", width=500)
    waf_tree.pack(fill="both", expand=True)

    tls_tree = ttk.Treeview(tls_frame, columns=("domain", "issuer", "expires", "san"), show="headings")
    tls_tree.heading("domain", text="Domain")
    tls_tree.heading("issuer", text="Issuer")
    tls_tree.heading("expires", text="Expires")
    tls_tree.heading("san", text="SANs")
    tls_tree.column("domain", width=200)
    tls_tree.column("issuer", width=300)
    tls_tree.column("expires", width=200)
    tls_tree.column("san", width=500)
    tls_tree.pack(fill="both", expand=True)

    param_tree = ttk.Treeview(param_frame, columns=("param", "count", "examples"), show="headings")
    param_tree.heading("param", text="Parameter")
    param_tree.heading("count", text="# URLs")
    param_tree.heading("examples", text="Example URLs")
    param_tree.column("param", width=150)
    param_tree.column("count", width=60)
    param_tree.column("examples", width=500)
    param_tree.pack(fill="both", expand=True)

    for box in (results_box,):
        box.tag_config("found", foreground="red")
        box.tag_config("ok", foreground="green")
        box.tag_config("crawl", foreground="blue")
        box.tag_config("error", foreground="orange")

    found_box.tag_config("found", foreground="red")

    tk.Label(win, text="URL:").grid(row=1, column=0, sticky="e")
    url_entry = tk.Entry(win, width=50)
    url_entry.grid(row=1, column=1, sticky="w", columnspan=3)

    tk.Label(win, text="Depth:").grid(row=2, column=0, sticky="e")
    depth_entry = tk.Entry(win, width=5)
    depth_entry.insert(0, "8")
    depth_entry.grid(row=2, column=1, sticky="w")

    js_var = tk.BooleanVar(value=False)
    debug_var = tk.BooleanVar(value=False)
    hide_low_var = tk.BooleanVar(value=True)
    tor_var = tk.BooleanVar(value=False)

    js_checkbox = tk.Checkbutton(win, text="Enable JS/Network mode (Playwright)", variable=js_var)
    js_checkbox.grid(row=3, column=0, columnspan=2, sticky="w")

    debug_checkbox = tk.Checkbutton(win, text="Heuristic debug mode", variable=debug_var)
    debug_checkbox.grid(row=3, column=2, sticky="w")

    hide_low_checkbox = tk.Checkbutton(
        win,
        text="Hide low-confidence heuristic hits (<30)",
        variable=hide_low_var
    )
    hide_low_checkbox.grid(row=3, column=3, sticky="w")

    tor_checkbox = tk.Checkbutton(
        win,
        text="Enable Tor Mode",
        variable=tor_var
    )
    tor_checkbox.grid(row=4, column=0, sticky="w")

    start_btn = tk.Button(
        win,
        text="Start Scan",
        command=lambda: threaded_scan(
            url_entry, depth_entry, results_box, tree, found_box, scanned_tree,
            files_tree, files_grouped_tabs, files_flat_tree,
            subdomain_tree, dir_tree, js_tree, forms_tree,
            waf_tree, tls_tree, param_tree,
            js_var, debug_var, hide_low_var, tor_var
        )
    )
    start_btn.grid(row=5, column=0)

    pause_btn = tk.Button(win, text="Pause", command=lambda: toggle_pause())
    pause_btn.grid(row=5, column=1)

    stop_btn = tk.Button(win, text="Stop", command=lambda: do_stop())
    stop_btn.grid(row=5, column=2)

    def toggle_pause():
        global pause_flag
        pause_flag = not pause_flag

    def do_stop():
        global stop_flag
        stop_flag = True

    win.mainloop()


if __name__ == "__main__":
    run_gui()
