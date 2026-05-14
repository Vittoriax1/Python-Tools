
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
        self.root.title("PaperClip")
        self.root.geometry("400x400")
        self.root.minsize(400, 400)

        # Header Frame
        header = tk.Frame(root, bg="black", height=40)
        header.pack(fill="x")

        header_label = tk.Label(
            header,
            text="PaperClip",
            bg="black",
            fg="white",
            font=("Segoe UI", 14, "bold"),
            pady=5
        )
        header_label.pack(side="left", padx=10)

        # --- Clear Button ---
        clear_button = tk.Button(
            header,
            text="Clear",
            bg="black",
            fg="white",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            command=self.clear_clipboard_and_screen
        )
        clear_button.pack(side="right", padx=10)

        # Main text area
        self.text_area = ScrolledText(
            root,
            wrap="word",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            borderwidth=0
        )
        self.text_area.pack(fill="both", expand=True)

        self.last_clipboard = ""

        # Start monitoring thread
        self.monitoring = True
        thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        thread.start()

    def clear_clipboard_and_screen(self):
        # Clear system clipboard
        pyperclip.copy("")

        # Clear on-screen text
        self.text_area.delete("1.0", "end")

        # Reset last_clipboard so new copies show up again
        self.last_clipboard = ""

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
