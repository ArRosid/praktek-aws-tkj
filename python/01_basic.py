"""
======================================================================
MODUL 1: DASAR-DASAR PYTHON (BASIC)
======================================================================
Membahas:
1. Menampilkan Output (print)
2. Variabel dan Aturan Penamaan
3. Tipe Data Dasar (String, Integer, Float, Boolean)
4. Format String (f-string)
5. Operator Aritmatika & Perbandingan
6. Menerima Input dari Pengguna
======================================================================
"""

# -------------------------------------------------------------------
# 1. Menampilkan Output & Komentar
# -------------------------------------------------------------------
print("--- 1. OUTPUT DASAR ---")
print("Selamat Datang di Lab Pemrograman Python TKJ & AWS!")

# -------------------------------------------------------------------
# 2. Variabel dan Tipe Data
# -------------------------------------------------------------------
print("\n--- 2. TIPE DATA & VARIABEL ---")
hostname = "Router-Utama-TKJ"     # String (str): teks
port_ssh = 22                     # Integer (int): bilangan bulat
bandwidth_mbps = 100.5            # Float (float): desimal
is_active = True                  # Boolean (bool): True / False

print("Hostname       :", hostname, "| Tipe:", type(hostname))
print("Port SSH       :", port_ssh, "| Tipe:", type(port_ssh))
print("Bandwidth      :", bandwidth_mbps, "Mbps | Tipe:", type(bandwidth_mbps))
print("Status Aktif   :", is_active, "| Tipe:", type(is_active))

# -------------------------------------------------------------------
# 3. String Formatting (f-string - Modern Python)
# -------------------------------------------------------------------
print("\n--- 3. FORMAT STRING (f-string) ---")
info = f"Perangkat '{hostname}' berjalan di port {port_ssh} dengan kecepatan {bandwidth_mbps} Mbps."
print(info)

# -------------------------------------------------------------------
# 4. Operator Aritmatika
# -------------------------------------------------------------------
print("\n--- 4. OPERATOR ARITMATIKA ---")
a = 10
b = 3

print(f"{a} + {b}  = {a + b}")    # Penjumlahan
print(f"{a} - {b}  = {a - b}")    # Pengurangan
print(f"{a} * {b}  = {a * b}")    # Perkalian
print(f"{a} / {b}  = {a / b:.2f}") # Pembagian (dibulatkan 2 desimal)
print(f"{a} // {b} = {a // b}")   # Pembagian bulat (floor division)
print(f"{a} % {b}  = {a % b}")    # Sisa bagi (modulus)
print(f"{a} ** {b} = {a ** b}")   # Pangkat (10 pangkat 3)

# -------------------------------------------------------------------
# 5. Konversi Tipe Data (Type Casting) & Input
# -------------------------------------------------------------------
print("\n--- 5. KONVERSI TIPE DATA ---")
str_angka = "8080"
int_port = int(str_angka)  # Mengubah str -> int
print(f"Port setelah di-convert ke integer: {int_port} (Tipe: {type(int_port)})")

# Contoh simulasi input (di-comment agar script bisa jalan otomatis)
# nama_admin = input("Masukkan nama admin: ")
# kuota = int(input("Masukkan kuota (GB): "))
# print(f"Admin: {nama_admin}, Kuota: {kuota * 1024} MB")

print("\n" + "="*50)
print("✅ Modul 1 Selesai dipelajari!")
print("="*50)
