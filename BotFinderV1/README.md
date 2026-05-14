# BotFinder

A simple GUI‑based website crawler that scans for embedded chatbots, AI widgets, or suspicious AI‑related patterns.

## Overview

BotFinder is a lightweight Python tool designed to analyze websites for signs of chatbot systems or AI‑driven components. It crawls through internal pages, extracts script tags, and checks for known chatbot platform signatures or heuristic indicators of AI use.
It includes a user‑friendly Tkinter GUI with real‑time logs, a pause/resume system, and a crawl tree visualization.
This tool is helpful for cybersecurity analysts, penetration testers, or developers who want to quickly identify whether a site embeds automated chat systems or AI services.

## Features

- Crawls a website recursively up to a chosen depth
- Detects known chatbot service providers (BotPress, Dialogflow, Intercom, Drift, Tawk.to, Crisp, etc.)
- Fuzzy‑search detection of AI keyword heuristics
- Extracts and inspects <script> tags for signatures
- Real‑time log output
- Tree‑view of the entire crawl path
- Pause / Resume / Stop scanning
- Automatic URL normalization
- Protection against infinite loops with visited‑URL tracking
- Threaded scanning to keep the GUI responsive

## Screenshots (Optional)


## Installation
1. Clone the repository
git clone https://github.com/Vittoriax1/Python-Tools/BotFinderV1.git
cd BotFinderV1

2. Install required dependencies
pip install -r requirements.txt

Required libraries include:

requests
beautifulsoup4
rapidfuzz
tkinter (built into Python on Windows/macOS)

3. Run the script
python BotFinder.py

The GUI will open automatically.

## Usage

1. Launch the tool with python BotFinder.py
2. Enter a target URL (example: openai.com)
3. Set the crawl depth (2–3 recommended)
4. Click “Start Scan”
5. Watch real‑time logs appear in the Log tab
Exp6. lore the crawl map in the “Crawl Tree” tab
7. Use:
- Pause — temporarily halt crawling
- Stop — terminate the scan early

### What the scan looks for

BotFinder checks:
- Script URLs matching known chatbot providers
- Fuzzy matches to AI‑related keywords
- JSON structures in scripts or inline code
- Domain‑local crawler behavior

Findings appear as:
[FOUND] https://example.com
  - AI-Heuristic, intercom.io

Or:
[OK] https://example.com — no detections

## Build Instructions (Optional) 
To build a standalone executable using PyInstaller:
pyinstaller --onefile --windowed BotFinder.py

Options:

--onefile bundles everything into a single EXE
--windowed hides the console window

Output will be in the dist/ directory.

## Project Structure 

BotFinder/

│── BotFinder.py

│── requirements.txt

└── README.md

Notes
- BotFinder works best on sites that expose scripts directly.
- Fully dynamic, JS‑only apps (like ChatGPT’s web UI) may not expose detectable endpoints without deeper inspection.
- Depth > 3 may produce long scans depending on the number of internal links.
