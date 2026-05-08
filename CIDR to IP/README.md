# CIDR Range Analyzer
CIDR_Range_Analyzer.py is a simple, beginner‑friendly Python tool designed to analyze CIDR blocks and display important network information. This script is a helpful utility for security analysts, students, and anyone learning about IP networking.
It safely provides key details such as:
- Network address
- Broadcast address
- Total number of hosts
- Network class (A, B, C, D, E)
- Whether the range is public or private
- Usable IP range (first to last host)
- Option to analyze multiple CIDRs in one session

<i>This tool is intended for educational use, labs, and workflow productivity.</i>

## Features

- CIDR Parsing
Accepts network ranges like 192.168.1.0/24 or 10.0.0.0/16.
- Network Class Detection
Identifies Class A, B, C, D (multicast), or E (reserved).
- Private vs Public Network Detection
Determines whether the CIDR is RFC1918 private space or a public network.
- Usable Host Range Calculation
Displays just the first and last usable IP — clean and fast.
- Loop Mode
You can analyze multiple CIDRs without restarting the script.

## Requirements

Python 3.8+

## Usage

Run the script:

python3 CIDR_Range_Analyzer.py

Enter a CIDR when prompted:

Enter a CIDR (example: 10.0.0.0/24): 

A sample output:

--- CIDR Information ---

CIDR: 192.168.1.0/24

Network Address: 192.168.1.0

Broadcast Address: 192.168.1.255

Total Hosts: 256

Network Class: Class C

Privacy Type: Private Network


Usable IP Range:

192.168.1.1 - 192.168.1.254
------------------------

Afterwards, choose whether to analyze another CIDR:

Check another CIDR? (y/n):

<img width="303" height="220" alt="CIDR-to-IP" src="https://github.com/user-attachments/assets/4013017e-60b5-4d2c-9b9c-d27316b3fd76" />

## Intended Use

This script is safe and intended for:
- Networking education
- Security lab work
- Productivity and workflow enhancement
- Capture-The-Flag practice
- General IP addressing reference

