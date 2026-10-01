"""
======================================================================
MODUL 7: TINGKAT LANJUT (ADVANCED INTEGRATION)
======================================================================
Membahas:
Penggabungan menyeluruh konsep:
- List & Dictionaries
- Struktur Data Bersarang (Nested Data)
- Perulangan (For / While Loop)
- Logika Percabangan Kompleks (If-Elif-Else & Operator Logika)

STUDI KASUS PROYEK NYATA:
"Sistem Audit Keamanan & Monitoring Resource Cloud / Lab TKJ"
1. Memfilter server berdasarkan beban CPU, RAM, dan status.
2. Mendeteksi pelanggaran port keamanan (Security Group Audit).
3. Mengkalkulasi statistik penggunaan resource.
4. Menghasilkan laporan evaluasi otomatis.
======================================================================
"""

# -------------------------------------------------------------------
# Data Simulasi: Infrastruktur Cloud & Lab Server TKJ
# -------------------------------------------------------------------
cloud_infrastructure = [
    {
        "instance_id": "i-001-web",
        "name": "Frontend-WebServer",
        "type": "t3.medium",
        "region": "ap-southeast-1",
        "status": "running",
        "cpu_usage": 88.5,       # Persen
        "ram_usage": 72.0,       # Persen
        "open_ports": [80, 443, 22],
        "tags": {"env": "prod", "tier": "frontend", "managed_by": "TKJ-Team"}
    },
    {
        "instance_id": "i-002-db",
        "name": "Database-MySQL-Primary",
        "type": "r5.large",
        "region": "ap-southeast-1",
        "status": "running",
        "cpu_usage": 94.0,       # Persen (Kritis)
        "ram_usage": 91.5,       # Persen (Kritis)
        "open_ports": [3306, 22, 21],  # Port 21 (FTP tidak aman)
        "tags": {"env": "prod", "tier": "database", "managed_by": "DBA-Team"}
    },
    {
        "instance_id": "i-003-dev",
        "name": "Dev-Testing-Server",
        "type": "t3.micro",
        "region": "us-east-1",
        "status": "stopped",
        "cpu_usage": 0.0,
        "ram_usage": 0.0,
        "open_ports": [8080, 22],
        "tags": {"env": "dev", "tier": "sandbox", "managed_by": "Siswa-TKJ"}
    },
    {
        "instance_id": "i-004-mon",
        "name": "Prometheus-Monitoring",
        "type": "t3.small",
        "region": "ap-southeast-1",
        "status": "running",
        "cpu_usage": 45.0,
        "ram_usage": 55.0,
        "open_ports": [9090, 3000, 22],
        "tags": {"env": "prod", "tier": "ops", "managed_by": "TKJ-Team"}
    }
]

print("=" * 70)
print("🚀 SISTEM MONITORING & AUDIT INFRASTRUKTUR CLOUD TKJ")
print("=" * 70)

# -------------------------------------------------------------------
# 1. FILTER & MONITORING KESEHATAN RESOURCE (CPU & RAM)
# -------------------------------------------------------------------
print("\n📊 [1] ANALISIS KESEHATAN RESOURCE SERVER:")

high_load_servers = []
running_count = 0
stopped_count = 0

for index, server in enumerate(cloud_infrastructure, start=1):
    srv_name = server["name"]
    srv_status = server["status"]
    cpu = server["cpu_usage"]
    ram = server["ram_usage"]

    if srv_status == "running":
        running_count += 1
        # Evaluasi beban server
        if cpu >= 90 or ram >= 90:
            health_badge = "🔴 CRITICAL OVERLOAD"
            high_load_servers.append({
                "name": srv_name,
                "cpu": cpu,
                "ram": ram,
                "reason": "CPU atau RAM melebihi 90%"
            })
        elif cpu >= 70 or ram >= 70:
            health_badge = "🟡 WARNING (Tinggi)"
        else:
            health_badge = "🟢 HEALTHY (Normal)"

        print(f" [{index}] {srv_name.ljust(25)} | CPU: {cpu:5.1f}% | RAM: {ram:5.1f}% | {health_badge}")
    else:
        stopped_count += 1
        print(f" [{index}] {srv_name.ljust(25)} | Status: ⏸️ STOPPED")

# -------------------------------------------------------------------
# 2. AUDIT KEAMANAN PORT JARINGAN (SECURITY AUDIT)
# -------------------------------------------------------------------
print("\n🔒 [2] AUDIT KEAMANAN PORT & PROTOKOL:")
insecure_ports = {
    21: "FTP (Plaintext Transfer - Sangat Rentan)",
    23: "Telnet (Unencrypted Remote Access)",
    80: "HTTP (Gunakan HTTPS port 443 untuk Production)"
}

security_findings = []

for server in cloud_infrastructure:
    # Hanya audit server yang running dan di environment production
    if server["status"] == "running" and server["tags"].get("env") == "prod":
        for port in server["open_ports"]:
            if port in insecure_ports:
                warning_detail = {
                    "server": server["name"],
                    "port": port,
                    "risk": insecure_ports[port]
                }
                security_findings.append(warning_detail)

if len(security_findings) > 0:
    for item in security_findings:
        print(f" ⚠️ [RISK ALERT] Server '{item['server']}' membuka Port {item['port']}: {item['risk']}")
else:
    print(" ✅ Seluruh server lolos audit keamanan port.")

# -------------------------------------------------------------------
# 3. STATISTIK PENGGUNAAN & RINGKASAN DATA
# -------------------------------------------------------------------
print("\n📈 [3] RINGKASAN STATISTIK & LAPORAN EKSEKUTIF:")

total_cpu_running = 0.0
total_ram_running = 0.0

for server in cloud_infrastructure:
    if server["status"] == "running":
        total_cpu_running += server["cpu_usage"]
        total_ram_running += server["ram_usage"]

avg_cpu = total_cpu_running / running_count if running_count > 0 else 0
avg_ram = total_ram_running / running_count if running_count > 0 else 0

print(f" • Total Server Terdaftar : {len(cloud_infrastructure)} unit")
print(f" • Server Running          : {running_count} unit")
print(f" • Server Stopped          : {stopped_count} unit")
print(f" • Rata-rata CPU (Running) : {avg_cpu:.2f}%")
print(f" • Rata-rata RAM (Running) : {avg_ram:.2f}%")

# -------------------------------------------------------------------
# 4. REKOMENDASI TINDAKAN OTOMATIS
# -------------------------------------------------------------------
print("\n💡 [4] REKOMENDASI TINDAKAN OTOMATIS (AUTOSCALING & ACTION):")
if len(high_load_servers) > 0:
    print(" 🚨 Server yang memerlukan tindakan segera:")
    for alert in high_load_servers:
        print(f"   - {alert['name']}: {alert['reason']} (CPU: {alert['cpu']}%, RAM: {alert['ram']}%)")
        print(f"     👉 Rekomendasi: Upgrade instance type atau aktifkan Auto-Scaling!")
else:
    print(" 👍 Tidak ada server dalam kondisi kritis saat ini.")

print("\n" + "=" * 70)
print("✅ Modul 7 Advanced Selesai Dijalankan!")
print("=" * 70)
