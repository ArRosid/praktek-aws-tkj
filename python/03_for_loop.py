"""
======================================================================
MODUL 3: PERULANGAN (FOR & WHILE LOOP)
======================================================================
Membahas:
1. Perulangan `for` dengan `range()`
2. Iterasi Karakter Teks (String)
3. Kontrol Loop: `break` dan `continue`
4. Perulangan `while`
5. Studi Kasus: Simulasi Batch Generate IP Address
======================================================================
"""

# -------------------------------------------------------------------
# 1. Perulangan `for` dengan `range()`
# -------------------------------------------------------------------
print("--- 1. FOR DENGAN RANGE ---")

# range(stop) -> 0 sampai 4
print("Hitung 0 sampai 4:")
for i in range(5):
    print(f"Index ke-{i}")

# range(start, stop) -> 1 sampai 5
print("\nHitung 1 sampai 5:")
for count in range(1, 6):
    print(f"Paket data ke-{count} terkirim...")

# range(start, stop, step) -> lompat 2
print("\nBilangan Genap 2 sampai 10:")
for genap in range(2, 11, 2):
    print(genap, end=" ")
print()

# -------------------------------------------------------------------
# 2. Iterasi Karakter Teks (String)
# -------------------------------------------------------------------
print("\n--- 2. LOOPING KARAKTER TEKS (STRING) ---")
protokol = "TCP"
for huruf in protokol:
    print(f"Karakter: {huruf}")

# -------------------------------------------------------------------
# 3. Kontrol Loop: `break` dan `continue`
# -------------------------------------------------------------------
print("\n--- 3. PENGGUNAAN BREAK & CONTINUE ---")

print("Contoh `continue` (Melewatkan IP .5):")
for host in range(1, 7):
    if host == 5:
        print(f"-> 192.168.1.{host} (Dilewati/Maintenance)")
        continue
    print(f"Checking IP: 192.168.1.{host}")

print("\nContoh `break` (Berhenti saat menemukan IP bermasalah):")
for host in range(1, 10):
    if host == 4:
        print(f"⚠️ Ditemukan IP konflik pada 192.168.1.{host}! Scan dihentikan.")
        break
    print(f"IP 192.168.1.{host}: Normal")

# -------------------------------------------------------------------
# 4. Perulangan `while`
# -------------------------------------------------------------------
print("\n--- 4. WHILE LOOP (SIMULASI RETRY KONEKSI) ---")
percobaan = 1
max_percobaan = 3
koneksi_berhasil = False

while percobaan <= max_percobaan:
    print(f"Percobaan ke-{percobaan}: Menghubungkan ke Server AWS...")
    if percobaan == 3:
        koneksi_berhasil = True
        print("✅ Terkoneksi ke server!")
        break
    percobaan += 1

# -------------------------------------------------------------------
# 5. Studi Kasus: Simulasi Batch Generate IP Address
# -------------------------------------------------------------------
print("\n--- 5. STUDI KASUS: GENERATE DAFTAR IP LAB TKJ ---")
subnet_prefix = "10.10.1."
jumlah_komputer_lab = 5

for pc in range(1, jumlah_komputer_lab + 1):
    ip_address = f"{subnet_prefix}{pc}"
    print(f"PC-LAB-TKJ-{pc:02d} -> IP: {ip_address}")

print("\n" + "="*50)
print("✅ Modul 3 Selesai dipelajari!")
print("="*50)
