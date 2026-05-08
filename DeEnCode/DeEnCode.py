import base64
import urllib.parse
import codecs
import binascii
import os
import re

# -----------------------------
# MENU
# -----------------------------
def menu():
    print("\n--- Encoder / Decoder Tool ---")
    print("1. Base64 Encode")
    print("2. Base64 Decode")
    print("3. URL Encode")
    print("4. URL Decode")
    print("5. HTML Escape")
    print("6. HTML Unescape")
    print("7. Hex Encode")
    print("8. Hex Decode")
    print("9. ROT13 Encode/Decode")
    print("10. XOR with Key")
    print("11. Auto-Detect Encoding")
    print("12. Binary to ASCII")
    print("13. ASCII to Binary")
    print("14. Load Input from File")
    print("15. Save Output to File")
    print("0. Exit")
    return input("Choose an option: ")

# -----------------------------
# Encoding / Decoding Functions
# -----------------------------

def base64_encode(data):
    return base64.b64encode(data.encode()).decode()

def base64_decode(data):
    try:
        decoded_bytes = base64.b64decode(data, validate=True)
        return decoded_bytes.decode("utf-8", errors="replace")
    except Exception:
        return "Invalid Base64 input."

def url_encode(data):
    return urllib.parse.quote(data)

def url_decode(data):
    return urllib.parse.unquote(data)

def html_escape(data):
    return (
        data.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

def html_unescape(data):
    return (
        data.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
    )

def hex_encode(data):
    return data.encode().hex()

def hex_decode(data):
    try:
        return bytes.fromhex(data).decode()
    except:
        return "Invalid hex input."

def rot13(data):
    return codecs.encode(data, "rot_13")

def xor_with_key(data, key):
    key_bytes = key.encode()
    result = []
    for i, c in enumerate(data.encode()):
        result.append(c ^ key_bytes[i % len(key_bytes)])
    return ''.join(format(b, '02x') for b in result)

# -----------------------------
# Binary <-> ASCII
# -----------------------------
def binary_to_ascii(data):
    try:
        parts = data.split()
        return ''.join(chr(int(b, 2)) for b in parts)
    except:
        return "Invalid binary input (must be 8-bit binary like 01001000)."

def ascii_to_binary(data):
    return ' '.join(format(ord(c), '08b') for c in data)

# -----------------------------
# Auto Detection
# -----------------------------
def looks_like_base64(data):
    if len(data) % 4 != 0:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9+/=]+", data))

def looks_like_hex(data):
    return bool(re.fullmatch(r"[0-9a-fA-F]+", data))

def auto_detect(data):

    # Base64 detection
    if looks_like_base64(data):
        try:
            decoded = base64.b64decode(data, validate=True).decode()
            return f"Detected Base64 → Decoded: {decoded}"
        except:
            pass

    # Hex detection
    if looks_like_hex(data):
        try:
            decoded = bytes.fromhex(data).decode()
            return f"Detected Hex → Decoded: {decoded}"
        except:
            pass

    # URL encoding detection
    decoded = urllib.parse.unquote(data)
    if decoded != data:
        return f"Detected URL Encoding → Decoded: {decoded}"

    return "Could not auto-detect encoding."

# -----------------------------
# File I/O
# -----------------------------
def load_from_file(path):
    if not os.path.exists(path):
        return None, "File not found."
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(), None
    except:
        return None, "Error reading file."

def save_to_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
        return f"Saved output to: {path}"
    except:
        return "Could not save file."

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    last_output = ""
    input_data = ""

    while True:
        choice = menu()

        if choice == "0":
            print("Goodbye!")
            break

        # Load from file
        if choice == "14":
            path = input("Enter file path: ")
            content, err = load_from_file(path)
            if err:
                print(err)
            else:
                print("\nLoaded Data:\n" + content)
                input_data = content
            continue

        # Save output to file
        if choice == "15":
            if not last_output:
                print("No output to save yet.")
            else:
                path = input("Enter save file path: ")
                print(save_to_file(path, last_output))
            continue

        # Ask for input if not from file
        if not input_data:
            input_data = input("Enter text: ")

        # Perform the chosen operation
        if choice == "1":
            last_output = base64_encode(input_data)
        elif choice == "2":
            last_output = base64_decode(input_data)
        elif choice == "3":
            last_output = url_encode(input_data)
        elif choice == "4":
            last_output = url_decode(input_data)
        elif choice == "5":
            last_output = html_escape(input_data)
        elif choice == "6":
            last_output = html_unescape(input_data)
        elif choice == "7":
            last_output = hex_encode(input_data)
        elif choice == "8":
            last_output = hex_decode(input_data)
        elif choice == "9":
            last_output = rot13(input_data)
        elif choice == "10":
            key = input("XOR key: ")
            last_output = xor_with_key(input_data, key)
        elif choice == "11":
            last_output = auto_detect(input_data)
        elif choice == "12":
            last_output = binary_to_ascii(input_data)
        elif choice == "13":
            last_output = ascii_to_binary(input_data)
        else:
            print("Invalid option.")
            input_data = ""
            continue

        print("\nOutput:\n" + str(last_output))

        # Reset input only AFTER operation
        input_data = ""

if __name__ == "__main__":
    main()
