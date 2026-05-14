import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import pyperclip
import time
import threading
import datetime

LOG_FILE = "clipboard_log.txt"

class ClipboardMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Monitor")
        self.root.geometry("400x400")

        self.text_area = ScrolledText(root, wrap="word", font=("Consolas", 10))
        self.text_area.pack(fill="both", expand=True)

        self.last_clipboard = ""

        # Start monitoring in a background thread
        self.monitoring = True
        thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        thread.start()

    def monitor_clipboard(self):
        while self.monitoring:
            current = pyperclip.paste()
            if current != self.last_clipboard:
                self.last_clipboard = current
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                entry = f"[{timestamp}]\n{current}\n{'-'*40}\n"

                # Insert into GUI
                self.text_area.insert("end", entry)
                self.text_area.see("end")

                # Save to log
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(entry)

            time.sleep(0.3)

    def on_close(self):
        self.monitoring = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
