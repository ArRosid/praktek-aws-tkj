# ⚡ SIMBAR TKJ - Sistem Inventaris Laboratorium Komputer & Jaringan
> **Aplikasi Web Manajemen Inventaris Lab TKJ berbasis Python Flask, Boto3, AWS DynamoDB & S3 Private Storage.**

Panduan lengkap ini dibuat untuk praktikum dari awal (*step-by-step*): mulai dari membuat tabel DynamoDB, bucket S3, peluncuran EC2 Instance, konfigurasi kredensial `.env`, hingga aplikasi berjalan dan bisa diakses publik.

---

## 📁 Struktur Folder Project

```
inventory-tkj/
├── app.py                  # Backend Flask + Boto3 (Membaca PORT & .env)
├── sample.env              # Template konfigurasi environment
├── requirements.txt        # Library: flask, boto3, python-dotenv, gunicorn
├── README.md               # Panduan lengkap step-by-step
├── templates/
│   └── index.html          # File HTML (UI Dashboard Inventaris TKJ)
└── static/
    ├── css/
    │   └── style.css       # File CSS (Cyber Slate & Neon Cyan Glassmorphic)
    └── js/
        └── app.js          # File JS (Fetch API ke Flask REST Endpoint)
```

---

## 🛠️ Langkah 1: Membuat Tabel di AWS DynamoDB

1. Buka **AWS Management Console** dan cari layanan **DynamoDB**.
2. Klik tombol **Create table**.
3. Isi konfigurasi tabel:
   - **Table name**: `tkj_inventory`
   - **Partition key**: `id`
   - **Tipe data**: `String`
4. Klik **Create table** dan tunggu statusnya menjadi **Active**.

---

## 🪣 Langkah 2: Membuat Bucket di AWS S3 (100% Private)

1. Buka layanan **Amazon S3** di AWS Console.
2. Klik tombol **Create bucket**.
3. Isi konfigurasi bucket:
   - **Bucket name**: Masukkan nama unik global, contoh: `tkj-inventory-foto-smk1` *(hanya huruf kecil, angka, dan tanda strip)*.
   - **AWS Region**: Pilih region yang sama dengan DynamoDB (contoh: `us-east-1`).
4. Klik **Create bucket**.

---

## 🔑 Langkah 3: Mengambil Kredensial AWS

### Opsi A: Jika Menggunakan AWS Academy / Learner Lab
1. Buka dashboard **AWS Academy Learner Lab**.
2. Klik tombol **AWS Details** di pojok kanan atas.
3. Klik **Show** pada bagian **AWS CLI credentials**.
4. Salin ketiga baris nilai berikut:
   - `aws_access_key_id`
   - `aws_secret_access_key`
   - `aws_session_token`

---

## 🖥️ Langkah 4: Membuat & Mengonfigurasi EC2 Instance

1. Buka layanan **Amazon EC2** -> Klik **Launch Instances**.
2. Konfigurasi instance:
   - **Name**: `Server-SIMBAR-TKJ`
   - **Application and OS Images (AMI)**: **Ubuntu Server 22.04 LTS** atau **Ubuntu Server 24.04 LTS** (Free tier eligible).
   - **Key pair (login)**: Pilih key pair yang sudah ada.
3. **Network settings (Security Group)**:
   - Centang **Allow SSH traffic from** -> `Anywhere (0.0.0.0/0)` *(Port 22)*.
   - Centang **Allow HTTP traffic from the internet** *(Port 80)*.
   - Klik tombol **Edit** pada bagian Network settings:
     - Klik **Add security group rule**.
     - **Type**: `Custom TCP`
     - **Port range**: `5000` *(atau sesuai port yang diatur di `.env`)*
     - **Source type**: `Anywhere` (`0.0.0.0/0`)
4. Klik **Launch Instance**.
5. Tunggu hingga status instance menjadi **Running**, lalu salin **Public IPv4 address** instance tersebut.

---

## 🚀 Langkah 5: Deploy & Menjalankan Aplikasi di EC2

### 1. Connect ke EC2 
Silahkan connect ke ec2 instance dari aws console

### 2. Update Sistem & Install Python Pip
```bash
sudo apt update
sudo apt install -y python3-pip git
```

### 3. Clone Repository ke EC2
Clone repository dari GitHub:

```bash
# Clone repository
git clone https://github.com/ArRosid/praktek-aws-tkj.git

# Masuk ke direktori project
cd praktek-aws-tkj/inventory-tkj

# Install library python (gunakan --break-system-packages di Ubuntu 24.04)
pip3 install -r requirements.txt --break-system-packages
```

### 4. Konfigurasi Environment File (`.env`)
Salin file template `sample.env` menjadi `.env`:

```bash
cp sample.env .env
```

Edit file `.env` menggunakan nano:
```bash
nano .env
```

Isi dengan konfigurasi Anda:
```ini
AWS_DEFAULT_REGION=us-east-1
DYNAMODB_TABLE_NAME=tkj_inventory
S3_BUCKET_NAME=tkj-inventory-foto-smk1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalrXUtn...
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjE...
PORT=5000
```
*(Tekan `Ctrl + O` lalu `Enter` untuk menyimpan, kemudian `Ctrl + X` untuk keluar dari nano).*

---

### 5. Jalankan Server Aplikasi
Jalankan aplikasi dengan perintah:
```bash
python3 app.py
```

Jika output terminal menampilkan:
```
==================================================
      SIMBAR TKJ - INVENTORY MANAGEMENT SERVER    
==================================================
Region   : us-east-1
DynamoDB : tkj_inventory
S3 Bucket: tkj-inventory-foto-smk1
Port     : 5000
URL      : http://0.0.0.0:5000
==================================================
```
Aplikasi sudah **berhasil berjalan**! 🎉

Buka browser di laptop dan akses:
```
http://<IP-PUBLIC-EC2>:5000
```
*(Ganti `<IP-PUBLIC-EC2>` dengan IP Publik EC2 Anda)*.

---
