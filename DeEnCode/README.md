# DeEnCode
DeEnCode.py is a multi‑purpose encoding and decoding utility designed to assist with text transformation, data inspection, and common operations used in CTFs, cybersecurity labs, and general technical workflows.
This tool provides a menu‑driven interface that allows users to easily convert between formats such as Base64, Hex, URL encoding, HTML escaping, ROT13, and more — all within a safe and controlled environment.

## Features

- Base64 Encode/Decode
Convert text to and from Base64 safely.
- URL Encode/Decode
Transform text into URL‑safe strings or decode encoded URLs.
- HTML Escape/Unescape
Convert <, >, and & into HTML‑safe characters (and back).
- Hex Encode/Decode
View text as hex or decode hex back into readable strings.
- ROT13
Classic substitution cipher commonly seen in CTFs.
- XOR With Key
Perform simple XOR operations using a user‑supplied key (output in hex).
- Auto‑Detect Encoding
Attempts to recognize whether input is Base64, Hex, or URL‑encoded.
- Binary ↔ ASCII Conversions
Convert 8‑bit binary to ASCII text or ASCII text to binary.
- File Input and Output
Load text directly from files or save your output to a file.
- Persistent Loop Mode
Continue performing multiple operations in a single session without restarting.

## Requirements

Python 3.8 or newer
No external libraries required (standard library only)

## Usage
Run the script:
python3 DeEnCode.py

You will see a menu like:
--- Encoder / Decoder Tool ---
1. Base64 Encode
2. Base64 Decode
3. URL Encode
4. URL Decode
5. HTML Escape
6. HTML Unescape
7. Hex Encode
8. Hex Decode
9. ROT13 Encode/Decode
10. XOR with Key
11. Auto-Detect Encoding
12. Binary to ASCII
13. ASCII to Binary
14. Load Input from File
15. Save Output to File
0. Exit

Enter the desired option, then provide input text or a file path as requested.

## Examples

### Base64 Decoding
Input:
2
IkhlbGxvLCB3b3JsZC4gSGVsbG8sIHdvcmxkLiBIZWxsbywgd29ybGQuIg==

Output:
"Hello, world. Hello, world. Hello, world."

### URL Encoding
Input:
3
hello world!

Output:
hello%20world%21

### Binary to ASCII
Input:
12
01001000 01101001

Output:
Hi


##Intended Use

This tool is designed for:
- Cybersecurity students
- CTF participants
- Developers and sysadmins
- Lab experimentation
- General text encoding/decoding tasks
