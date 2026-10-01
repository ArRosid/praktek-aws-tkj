"""
======================================================================
MODUL 5: STRUKTUR DATA DICTIONARY (KEY-VALUE PAIR)
======================================================================
Membahas:
1. Konsep Key-Value dan Cara Membuat Dictionary
2. Mengakses Nilai (Bracket `[]` vs Method `.get()`)
3. Menambah dan Mengubah Data Dictionary
4. Menghapus Data (`pop()`, `del`)
5. Iterasi Dictionary: `.keys()`, `.values()`, `.items()`
6. Method Tambahan: `.update()`, `.clear()`
======================================================================
"""

# -------------------------------------------------------------------
# 1. Membuat Dictionary & Mengakses Data
# -------------------------------------------------------------------
print("--- 1. MEMBUAT DICTIONARY ---")
ec2_instance = {
    "instance_id": "i-0a1b2c3d4e5f",
    "name": "Web-Server-TKJ",
    "instance_type": "t3.micro",
    "public_ip": "13.250.12.45",
    "state": "running",
    "vcpu": 2,
    "ram_gb": 1.0
}

print("Informasi Instance:")
print("Nama Instance :", ec2_instance["name"])
print("Public IP     :", ec2_instance["public_ip"])

# -------------------------------------------------------------------
# 2. Mengakses Nilai dengan Aman (.get())
# -------------------------------------------------------------------
print("\n--- 2. AKSES DENGAN METHOD .get() ---")
# Keuntungan .get(): Tidak error jika key tidak ada, melainkan mengembalikan nilai default
security_group = ec2_instance.get("security_group", "default-sg (Tidak Ditemukan)")
print("Security Group:", security_group)

# -------------------------------------------------------------------
# 3. Menambah & Memperbarui Data
# -------------------------------------------------------------------
print("\n--- 3. MENAMBAH & MENGUBAH DATA ---")
# Mengubah nilai yang sudah ada
ec2_instance["state"] = "stopped"

# Menambah key baru
ec2_instance["storage_gb"] = 30
ec2_instance["environment"] = "Production"

print("Status Baru :", ec2_instance["state"])
print("Storage     :", ec2_instance["storage_gb"], "GB")

# Method update() untuk multi fields sekaligus
ec2_instance.update({
    "monitoring": "enabled",
    "cost_center": "TKJ-Lab-01"
})
print("Setelah update:", ec2_instance)

# -------------------------------------------------------------------
# 4. Menghapus Elemen Dictionary
# -------------------------------------------------------------------
print("\n--- 4. MENGHAPUS ELEMEN ---")
# pop(key) -> Menghapus dan mengembalikan nilai yang dihapus
removed_field = ec2_instance.pop("cost_center")
print(f"Field yang dihapus: {removed_field}")

# -------------------------------------------------------------------
# 5. Iterasi / Looping Dictionary
# -------------------------------------------------------------------
print("\n--- 5. ITERASI PADA DICTIONARY ---")

print("\nA. Mengambil Semua Keys:")
for key in ec2_instance.keys():
    print(f"- {key}")

print("\nB. Mengambil Semua Values:")
for val in ec2_instance.values():
    print(f"- {val}")

print("\nC. Mengambil Key dan Value Bersamaan (.items()):")
for key, value in ec2_instance.items():
    print(f"{key.ljust(15)} : {value}")

print("\n" + "="*50)
print("✅ Modul 5 Selesai dipelajari!")
print("="*50)
