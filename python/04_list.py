"""
======================================================================
MODUL 4: STRUKTUR DATA LIST (ARRAY DINAMIS DI PYTHON)
======================================================================
Membahas:
1. Membuat List & Indexing (Positif & Negatif)
2. Slicing List (Memotong Sebagian Data)
3. Menambah Data: `append()`, `insert()`, `extend()`
4. Menghapus Data: `remove()`, `pop()`, `del`, `clear()`
5. Operasi List: `len()`, `sort()`, `reverse()`, `in` (Pengecekan)
6. Looping Melalui Elemen List
======================================================================
"""

# -------------------------------------------------------------------
# 1. Membuat List & Indexing
# -------------------------------------------------------------------
print("--- 1. MEMBUAT LIST & INDEXING ---")
perangkat = ["Router-Mikrotik", "Switch-Cisco", "Server-Ubuntu", "Access-Point"]

print("List Perangkat:", perangkat)
print("Elemen Pertama (Index 0)  :", perangkat[0])
print("Elemen Ketiga  (Index 2)  :", perangkat[2])
print("Elemen Terakhir (Index -1):", perangkat[-1])

# -------------------------------------------------------------------
# 2. Slicing List [start:stop] (stop tidak diikutsertakan)
# -------------------------------------------------------------------
print("\n--- 2. SLICING LIST ---")
port_list = [21, 22, 25, 53, 80, 110, 143, 443, 3306]

print("Semua Port      :", port_list)
print("3 Port Pertama  :", port_list[0:3])    # Index 0, 1, 2
print("Port dari idx 4 :", port_list[4:])     # Dari index 4 sampai akhir
print("Port 3 Terakhir :", port_list[-3:])    # 3 elemen paling belakang

# -------------------------------------------------------------------
# 3. Menambah Elemen ke List
# -------------------------------------------------------------------
print("\n--- 3. MENAMBAH ELEMEN LIST ---")
servers = ["web-prod-01", "web-prod-02"]
print("Awal        :", servers)

# append() -> Tambah di posisi paling akhir
servers.append("db-prod-01")
print("Setelah append:", servers)

# insert(index, item) -> Sisipkan di posisi tertentu
servers.insert(1, "lb-nginx-01")
print("Setelah insert:", servers)

# extend() -> Gabungkan list lain
backup_servers = ["backup-s3", "dr-server"]
servers.extend(backup_servers)
print("Setelah extend:", servers)

# -------------------------------------------------------------------
# 4. Menghapus Elemen dari List
# -------------------------------------------------------------------
print("\n--- 4. MENGHAPUS ELEMEN LIST ---")
# pop() -> Menghapus & mengembalikan elemen terakhir (atau index tertentu)
removed_server = servers.pop()
print(f"Dihapus dengan pop() : {removed_server}")
print("Sisa server          :", servers)

# remove(nilai) -> Menghapus berdasarkan nilai yang cocok
servers.remove("web-prod-02")
print("Setelah remove('web-prod-02'):", servers)

# -------------------------------------------------------------------
# 5. Operasi & Fungsi Bawaan List
# -------------------------------------------------------------------
print("\n--- 5. OPERASI UMUM LIST ---")
ip_octets = [192, 168, 10, 254, 5, 80]

print("Jumlah Elemen (len) :", len(ip_octets))
print("Nilai Tertinggi (max):", max(ip_octets))
print("Nilai Terendah (min) :", min(ip_octets))

# Pengecekan Keberadaan Nilai (in / not in)
if 80 in ip_octets:
    print("Angka 80 ditemukan dalam daftar octet.")

# Mengurutkan (sort)
ip_octets.sort()
print("Setelah Diurutkan (Ascending) :", ip_octets)
ip_octets.reverse()
print("Setelah Dibalik (Descending)  :", ip_octets)

# -------------------------------------------------------------------
# 6. Looping Melalui List
# -------------------------------------------------------------------
print("\n--- 6. LOOPING ELEMEN LIST ---")
service_list = ["SSH", "Nginx", "Docker", "MySQL"]

for svc in service_list:
    print(f"Service status: {svc} [RUNNING]")

print("\n" + "="*50)
print("✅ Modul 4 Selesai dipelajari!")
print("="*50)
