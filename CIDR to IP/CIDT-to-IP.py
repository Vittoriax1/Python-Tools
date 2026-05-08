import ipaddress

def get_network_class(ip):
    first_octet = int(str(ip).split(".")[0])

    if 1 <= first_octet <= 126:
        return "Class A"
    elif 128 <= first_octet <= 191:
        return "Class B"
    elif 192 <= first_octet <= 223:
        return "Class C"
    elif 224 <= first_octet <= 239:
        return "Class D (Multicast)"
    elif 240 <= first_octet <= 254:
        return "Class E (Reserved)"
    else:
        return "Unknown"

def expand_cidr_range(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=False)

        all_hosts = list(network.hosts())
        if len(all_hosts) == 0:
            print("This CIDR has no usable host addresses.")
            return

        first_ip = all_hosts[0]
        last_ip = all_hosts[-1]

        net_class = get_network_class(network.network_address)

        privacy = "Private Network" if network.is_private else "Public Network"

        print(f"\n--- CIDR Information ---")
        print(f"CIDR: {cidr}")
        print(f"Network Address: {network.network_address}")
        print(f"Broadcast Address: {network.broadcast_address}")
        print(f"Total Hosts: {network.num_addresses}")
        print(f"Network Class: {net_class}")
        print(f"Privacy Type: {privacy}")

        print("\nUsable IP Range:")
        print(f"{first_ip} - {last_ip}")
        print("------------------------\n")

    except ValueError:
        print("Invalid CIDR format. Example: 192.168.1.0/24")

if __name__ == "__main__":
    while True:
        cidr_input = input("Enter a CIDR (example: 10.0.0.0/24): ")
        expand_cidr_range(cidr_input)

        again = input("Check another CIDR? (y/n): ").strip().lower()
        if again != "y":
            print("Exiting...")
            break
