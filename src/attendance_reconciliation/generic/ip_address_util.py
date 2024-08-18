import fcntl
import socket
import struct
import subprocess

import netifaces

try:
    from netifaces import AF_INET, ifaddresses
except ModuleNotFoundError as e:
    raise SystemExit(f"Requires {e.name} module. Run 'pip install {e.name}' "
                     f"and try again.")


def get_ip_linux(interface: str) -> str:
    """
    Uses the Linux SIOCGIFADDR ioctl to find the IP address associated
    with a network interface, given the name of that interface, e.g.
    "eth0". Only works on GNU/Linux distributions.
    Source: https://bit.ly/3dROGBN
    Returns:
        The IP address in quad-dotted notation of four decimal integers.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    return socket.inet_ntoa(packed_addr)


def get_ip_cross(interface: str) -> str:
    """
    Cross-platform solution that should work under Linux, macOS and
    Windows.
    :rtype: object
    """
    try:
        return ifaddresses(interface)[AF_INET][0]['addr']
    except Exception:
        return None


def get_next_ip(ip_address):
    ip_parts = ip_address.split('.')
    ip_int = int(ip_parts[0]) << 24 | int(ip_parts[1]) << 16 | int(ip_parts[2]) << 8 | int(ip_parts[3])
    next_ip_int = ip_int + 1
    next_ip_parts = [(next_ip_int >> 24) & 255, (next_ip_int >> 16) & 255, (next_ip_int >> 8) & 255, next_ip_int & 255]
    next_ip_address = '.'.join(map(str, next_ip_parts))
    return next_ip_address


def get_previous_ip(ip_address):
    ip_parts = ip_address.split('.')
    ip_int = int(ip_parts[0]) << 24 | int(ip_parts[1]) << 16 | int(ip_parts[2]) << 8 | int(ip_parts[3])
    previous_ip_int = ip_int - 1
    previous_ip_parts = [(previous_ip_int >> 24) & 255, (previous_ip_int >> 16) & 255, (previous_ip_int >> 8) & 255,
                         previous_ip_int & 255]
    previous_ip_address = '.'.join(map(str, previous_ip_parts))
    return previous_ip_address


def check_ip_configuration(interface):
    # Get the IP address settings for the interface
    result = subprocess.run(["ip", "addr", "show", "dev", interface], capture_output=True, text=True)
    output = result.stdout

    # Check if the IP address is obtained via DHCP or configured statically
    if "dynamic" in output or "dhcp" in output:
        return "DHCP"
    elif "inet" in output:
        return "STATIC"
    else:
        return "No IP address found"


def get_all_network_details():
    interface_info = {}

    for interface in netifaces.interfaces():
        try:
            interface_info[interface] = {"interface": interface, "ipv4": "", "subnet": "", "gateway": "", "mac": ""}
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                ipv4_info = addresses[netifaces.AF_INET][0]
                interface_info[interface]['ipv4'] = ipv4_info['addr']
                interface_info[interface]['subnet'] = ipv4_info['netmask']
                try:
                    interface_info[interface]['gateway'] = netifaces.gateways()['default'][netifaces.AF_INET][0]
                except Exception:
                    interface_info[interface]['gateway'] = ''

            try:
                mac_address = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
                interface_info[interface]['mac'] = mac_address
            except KeyError:
                interface_info[interface]['mac'] = "Not available"
        except Exception:
            pass
    return interface_info


def subnet_mask_to_cidr(subnet_mask):
    # Split the subnet mask into octets
    octets = subnet_mask.split('.')

    # Convert each octet to binary
    binary_octets = [bin(int(octet))[2:].zfill(8) for octet in octets]

    # Count the number of '1' bits in the binary representation
    cidr = sum(bit == '1' for octet in binary_octets for bit in octet)

    return cidr


def set_static_ip(interface, ip_address, subnet_mask, gateway, dns, metric):
    # Backup the original dhcpcd.conf file
    # base_path = "/home/akshay/Office/Code/PDU/pdu-backend/files"
    base_path = "/etc"
    subprocess.run(["sudo", "cp", f'{base_path}/dhcpcd.conf', f'{base_path}/dhcpcd.conf.bak'])
    # subprocess.run(["cp", f'{base_path}/dhcpcd.conf', f'{base_path}/dhcpcd.conf.bak'])
    cidr = subnet_mask_to_cidr(subnet_mask)
    # Open dhcpcd.conf file for writing
    with open(f'{base_path}/dhcpcd.conf', "a") as f:
        f.write("\n")
        f.write(f"interface {interface}\n")
        f.write(f"metric {metric}\n")
        f.write(f"static ip_address={ip_address}/{cidr}\n")
        if gateway.strip() != "":
            f.write(f"static routers={gateway}\n")
        if dns.strip() != "":
            f.write(f"static domain_name_servers={dns}\n")
    subprocess.run(["sudo", "ifdown", interface])
    subprocess.run(["sudo", "ifup", interface])
    print("Static IP configuration applied successfully.")


def remove_static_ip(interface):
    # Backup the original dhcpcd.conf file
    # base_path = "/home/akshay/Office/Code/PDU/pdu-backend/files"
    base_path = "/etc"
    subprocess.run(["sudo", "cp", f'{base_path}/dhcpcd.conf', f'{base_path}/dhcpcd.conf.bak'])
    # subprocess.run(["cp", f'{base_path}/dhcpcd.conf', f'{base_path}/dhcpcd.conf.bak'])
    # Open dhcpcd.conf file for reading
    with open(f'{base_path}/dhcpcd.conf', "r") as f:
        lines = f.readlines()

    # Open dhcpcd.conf file for writing
    with open(f'{base_path}/dhcpcd.conf', "w") as f:
        skip_interface = False
        last_line = ""
        is_not_first_line = False
        for line in lines:

            if line.strip() == "" and last_line.strip() == "" and is_not_first_line:
                continue
            is_not_first_line = True
            last_line = line.strip()
            if skip_interface:
                if line.strip() == "":
                    skip_interface = False
                continue

                # Skip the lines related to the specified interface
            if line.startswith(f"interface {interface}"):
                skip_interface = True
                continue
            f.write(line)


def set_metric(interface, metric):
    # Backup the original dhcpcd.conf file
    # base_path = "/home/akshay/Office/Code/PDU/pdu-backend/files"
    base_path = "/etc"
    subprocess.run(["sudo", "cp", f'{base_path}/dhcpcd.conf', f'{base_path}/dhcpcd.conf.bak'])
    # subprocess.run(["cp", f'{base_path}/dhcpcd.conf', f'{base_path}/dhcpcd.conf.bak'])
    with open(f'{base_path}/dhcpcd.conf', "a") as f:
        f.write("\n")
        f.write(f"interface {interface}\n")
        f.write(f"metric {metric}\n")


def remove_wifi_settings():
    target_path = "/etc/wpa_supplicant"
    base_path = "/home/vaa/data-drive/pdu-backend/files"
    file_name = "wpa_supplicant.conf"
    subprocess.run(["sudo", "cp", f'{target_path}/{file_name}', f'{base_path}/{file_name}'])
    subprocess.run(["sudo", "chown", 'vaa:vaa', f'{base_path}/{file_name}'])
    # Open dhcpcd.conf file for reading
    with open(f'{base_path}/{file_name}', "r") as f:
        lines = f.readlines()

    # Open dhcpcd.conf file for writing
    with open(f'{base_path}/{file_name}', "w") as f:
        skip_interface = False
        last_line = ""
        is_not_first_line = False
        for line in lines:

            if line.strip() == "" and last_line.strip() == "" and is_not_first_line:
                continue
            is_not_first_line = True
            last_line = line.strip()
            if skip_interface:
                if line.strip() == "":
                    skip_interface = False
                continue

                # Skip the lines related to the specified interface
            if line.startswith("network={"):
                skip_interface = True
                continue
            f.write(line)


def add_wifi_settings(wifi_setting_list):
    base_path = "/home/vaa/data-drive/pdu-backend/files"
    file_name = "wpa_supplicant.conf"
    target_path = "/etc/wpa_supplicant"

    total_wifi = len(wifi_setting_list)
    for i in range(len(wifi_setting_list)):
        wifi_setting = wifi_setting_list[i]
        ssid = wifi_setting["ssid"]
        password = wifi_setting["password"]
        priority = wifi_setting["priority"]
        id_str = f'option{wifi_setting["id"]}'
        # Open {file_name} file for writing
        with open(f'{base_path}/{file_name}', "a") as f:
            f.write("\n")
            f.write("network={\n")
            f.write(f'    ssid="{ssid}"\n')
            f.write(f'    psk="{password}"\n')
            f.write(f'    priority={priority}\n')
            f.write(f'    id_str="{id_str}"\n')
            f.write("}\n")
            if total_wifi == (i + 1):
                f.write("\n")
    subprocess.run(["sudo", "cp", f'{base_path}/{file_name}', f'{target_path}/{file_name}'])
    # subprocess.run(["sudo", "ifdown", "wlan0"])
    # subprocess.run(["sudo", "ifup", "wlan0"])
