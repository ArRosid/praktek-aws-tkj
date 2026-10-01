"""
======================================================================
MODUL 2: PERCABANGAN & LOGIKA (IF - ELIF - ELSE)
======================================================================
Membahas:
1. Operator Perbandingan (==, !=, >, <, >=, <=)
2. Operator Logika (and, or, not)
3. Struktur if, elif, dan else
4. Nested if (Percabangan Bersarang)
5. Studi Kasus Jaringan: Cek Status Port & Kuota Bandwidth
======================================================================
"""

# -------------------------------------------------------------------
# 1. Dasar Percabangan (if - else)
# -------------------------------------------------------------------
print("--- 1. DASAR IF - ELSE ---")
ping_latency_ms = 45

if ping_latency_ms < 50:
    print(f"Latency {ping_latency_ms} ms: Koneksi Sangat Baik 🟢")
else:
    print(f"Latency {ping_latency_ms} ms: Koneksi Lambat 🔴")

# -------------------------------------------------------------------
# 2. Struktur Multi Kondisi (if - elif - else)
# -------------------------------------------------------------------
print("\n--- 2. IF - ELIF - ELSE (STATUS UTILISASI CPU) ---")
cpu_usage_percent = 78

if cpu_usage_percent >= 90:
    status = "CRITICAL: Beban Server Terlalu Tinggi! ⚠️"
elif cpu_usage_percent >= 70:
    status = "WARNING: Server Mulai Sibuk! 🟡"
elif cpu_usage_percent >= 40:
    status = "NORMAL: Beban Server Stabil 🟢"
else:
    status = "IDLE: Server Santai 🔵"

print(f"Penggunaan CPU: {cpu_usage_percent}% -> Status: {status}")

# -------------------------------------------------------------------
# 3. Operator Logika (and, or, not)
# -------------------------------------------------------------------
print("\n--- 3. OPERATOR LOGIKA (and, or, not) ---")
is_authenticated = True
user_role = "admin"
port = 22

# Menggunakan 'and'
if is_authenticated and user_role == "admin":
    print("Akses Diterima: Membuka dashboard konfigurasi root.")
else:
    print("Akses Ditolak: Anda bukan admin terdaftar.")

# Menggunakan 'or'
protocol = "https"
if protocol == "http" or protocol == "https":
    print(f"Protokol '{protocol}' adalah protokol web yang valid.")

# Menggunakan 'not'
is_firewall_disabled = False
if not is_firewall_disabled:
    print("Firewall dalam kondisi AKTIF dan AMAN.")

# -------------------------------------------------------------------
# 4. Studi Kasus: Deteksi Port & Layanan Jaringan
# -------------------------------------------------------------------
print("\n--- 4. STUDI KASUS: DETEKSI PROTOKOL PORT ---")
target_port = 443

if target_port == 80:
    service = "HTTP (Web Tidak Terenkripsi)"
elif target_port == 443:
    service = "HTTPS (Web Aman / SSL)"
elif target_port == 22:
    service = "SSH (Remote Terminal Secure)"
elif target_port == 53:
    service = "DNS (Domain Name System)"
elif target_port == 3306:
    service = "MySQL / MariaDB Database"
else:
    service = "Custom Service / Unknown Port"

print(f"Port {target_port} adalah layanan: {service}")

# -------------------------------------------------------------------
# 5. Percabangan Bersarang (Nested IF)
# -------------------------------------------------------------------
print("\n--- 5. NESTED IF (CEK AKSES SERVER AWS) ---")
server_region = "ap-southeast-1"  # Singapore
ip_whitelisted = True

if server_region == "ap-southeast-1":
    if ip_whitelisted:
        print("✅ Berhasil terhubung ke instance AWS EC2 Singapore!")
    else:
        print("❌ Gagal: IP Public Anda belum terdaftar di Security Group AWS.")
else:
    print("❌ Gagal: Region tidak diizinkan.")

print("\n" + "="*50)
print("✅ Modul 2 Selesai dipelajari!")
print("="*50)
