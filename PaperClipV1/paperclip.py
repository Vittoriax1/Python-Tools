import time
import pyperclip

def monitor_clipboard():
    last = ""
    print("Monitoring your clipboard... Press Ctrl+C to stop.")

    while True:
        try:
            current = pyperclip.paste()
            if current != last:
                print(f"\nNew clipboard content:\n{current}\n{'-'*40}")
                last = current
            time.sleep(0.3)
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
            break

if __name__ == "__main__":
    monitor_clipboard()
