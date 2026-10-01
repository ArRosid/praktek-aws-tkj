"""
======================================================================
MODUL 6: STRUKTUR DATA BERSARANG (NESTED LIST & DICTIONARY)
======================================================================
Membahas:
1. List di dalam List (2D Matrix / Grid)
2. List di dalam Dictionary (Contoh: Konfigurasi dengan banyak port/IP)
3. Dictionary di dalam Dictionary (Konfigurasi Multi-Region/VPC)
4. List of Dictionaries (Tabel Data: Rekaman Inventaris / Server List)
5. Cara Menjelajahi dan Memodifikasi Data Bersarang
======================================================================
"""

# -------------------------------------------------------------------
# 1. List di dalam Dictionary
# -------------------------------------------------------------------
print("--- 1. LIST DI DALAM DICTIONARY ---")
firewall_rules = {
    "group_name": "sg-web-tkj",
    "vpc_id": "vpc-0123456789abcdef0",
    "allowed_ports": [22, 80, 443, 8080],
    "tags": ["web", "frontend", "public"]
}

print("Nama Security Group :", firewall_rules["group_name"])
print("Port Pertama        :", firewall_rules["allowed_ports"][0])  # Index 0 dari list
print("Daftar Port Allowed :")
for port in firewall_rules["allowed_ports"]:
    print(f" - Port {port}/TCP")

# Menambahkan port baru ke list di dalam dict
firewall_rules["allowed_ports"].append(3306)
print("Updated Ports       :", firewall_rules["allowed_ports"])

# -------------------------------------------------------------------
# 2. Dictionary di dalam Dictionary (Nested Dict)
# -------------------------------------------------------------------
print("\n--- 2. DICTIONARY DI DALAM DICTIONARY ---")
aws_infrastructure = {
    "vpc_main": {
        "cidr_block": "10.0.0.0/16",
        "subnets": {
            "subnet_public_1a": {"cidr": "10.0.1.0/24", "az": "ap-southeast-1a"},
            "subnet_private_1b": {"cidr": "10.0.2.0/24", "az": "ap-southeast-1b"}
        }
    }
}

# Mengakses nested dictionary
cidr_utama = aws_infrastructure["vpc_main"]["cidr_block"]
az_private = aws_infrastructure["vpc_main"]["subnets"]["subnet_private_1b"]["az"]

print(f"VPC CIDR       : {cidr_utama}")
print(f"AZ Subnet Priv : {az_private}")

# -------------------------------------------------------------------
# 3. List of Dictionaries (Struktur Data Standar API / Database)
# -------------------------------------------------------------------
print("\n--- 3. LIST OF DICTIONARIES (INVENTARIS SERVER) ---")
servers = [
    {
        "id": "srv-01",
        "hostname": "gateway-tkj",
        "role": "router",
        "ip": "192.168.1.1",
        "is_online": True
    },
    {
        "id": "srv-02",
        "hostname": "dns-tkj",
        "role": "dns-server",
        "ip": "192.168.1.2",
        "is_online": True
    },
    {
        "id": "srv-03",
        "hostname": "web-backup",
        "role": "backup",
        "ip": "192.168.1.50",
        "is_online": False
    }
]

# Mengakses elemen tertentu
print("Server ke-2:", servers[1]["hostname"], "(IP:", servers[1]["ip"] + ")")

# Looping melalui list of dictionaries
print("\nStatus Seluruh Server:")
for srv in servers:
    status_icon = "🟢 ONLINE" if srv["is_online"] else "🔴 OFFLINE"
    print(f"[{srv['id']}] {srv['hostname'].ljust(12)} - {srv['ip'].ljust(15)} : {status_icon}")

# -------------------------------------------------------------------
# 4. Modifikasi Data Bersarang
# -------------------------------------------------------------------
print("\n--- 4. MODIFIKASI DATA BERSARANG ---")
# Menyalakan server ke-3 (index 2)
servers[2]["is_online"] = True
print(f"Status terbaru {servers[2]['hostname']}: is_online = {servers[2]['is_online']}")

print("\n" + "="*50)
print("✅ Modul 6 Selesai dipelajari!")
print("="*50)
