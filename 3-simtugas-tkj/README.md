# 📚 SIMTUGAS TKJ - Sistem Pengumpulan Tugas Siswa Berbasis AWS
> **Aplikasi Pengumpulan Dokumen Tugas Siswa (PDF) berbasis Python Flask, Boto3, AWS EC2, VPC Custom, DynamoDB, dan S3 Private Storage.**

Dokumentasi ini disusun secara *step-by-step* untuk praktikum SMK Jurusan **Teknik Komputer dan Jaringan (TKJ)**: mulai dari membangun arsitektur jaringan cloud (**VPC, 2 Subnet Public, Internet Gateway, Route Table, Security Group manual**), pembuatan database **DynamoDB**, penyimpanan berkas **S3 (Private)**, peluncuran **EC2 Instance**, hingga konfigurasi tema dinamis (**`STYLE=BLUE`** atau **`STYLE=GREEN`**).

---

## 🧭 Alur Kerja Aplikasi (Application Flow)

```
[Guru] ──1. Tambah Kelas──> [DynamoDB: tkj_tugas]
  │
  └───2. Tambah Siswa (Pilih Kelas)──> [DynamoDB: tkj_tugas]

[Siswa] ──3. Pilih Kelas & Nama Siswa──> Tampil otomatis
  │
  └───4. Upload Berkas Tugas (.PDF)──┬──> [Metadata] ──> [DynamoDB]
                                     └──> [File PDF]  ──> [AWS S3 Private]

[Guru] ──5. Rekap Tugas Masuk & Download PDF──> Streaming via Boto3 (Aman & Private)
```

---

## 📁 Struktur Folder Project

```
3-pengumpulan-tugas/
├── app.py                  # Backend Flask + Boto3 (Membaca STYLE, PORT & .env)
├── sample.env              # Template konfigurasi environment (STYLE=BLUE / GREEN)
├── requirements.txt        # Library: flask, boto3, python-dotenv, gunicorn
├── README.md               # Panduan lengkap step-by-step praktikum TKJ
├── templates/
│   └── index.html          # UI Portal Pengumpulan Tugas (Tab Siswa, Rekap Guru, Kelola)
└── static/
    ├── css/
    │   └── style.css       # Style CSS responsif (Mendukung Tema BLUE & GREEN)
    └── js/
        └── app.js          # Reaktif dropdown kelas -> siswa, dropzone PDF, fetch API
```

---

## 🌐 Langkah 1: Membuat Custom VPC di AWS

1. Buka **AWS Management Console** -> Cari dan pilih layanan **VPC**.
2. Pada menu sebelah kiri, klik **Your VPCs** -> Klik tombol **Create VPC**.
3. Pilih opsi **VPC only**.
4. Masukkan konfigurasi VPC:
   - **Name tag**: `vpc-simtugas-tkj`
   - **IPv4 CIDR block**: Masukkan secara manual -> `10.0.0.0/16`
5. Biarkan opsi lainnya default, lalu klik **Create VPC**.

---

## 🖧 Langkah 2: Membuat Dua Subnet Public & Enable Auto-assign Public IP

Kita akan membuat 2 subnet di Availability Zone (AZ) berbeda untuk standar arsitektur jaringan cloud.

### 1. Membuat Subnet 1
1. Pada menu sebelah kiri VPC, klik **Subnets** -> Klik tombol **Create subnet**.
2. **VPC ID**: Pilih `vpc-simtugas-tkj`.
3. Konfigurasi Subnet pertama:
   - **Subnet name**: `subnet-simtugas-public-1`
   - **Availability Zone**: Pilih AZ pertama (contoh: `us-east-1a`).
   - **IPv4 subnet CIDR block**: `10.0.1.0/24`
4. Klik **Create subnet**.

### 2. Membuat Subnet 2
1. Klik tombol **Create subnet** lagi.
2. **VPC ID**: Pilih `vpc-simtugas-tkj`.
3. Konfigurasi Subnet kedua:
   - **Subnet name**: `subnet-simtugas-public-2`
   - **Availability Zone**: Pilih AZ kedua yang berbeda (contoh: `us-east-1b`).
   - **IPv4 subnet CIDR block**: `10.0.2.0/24`
4. Klik **Create subnet**.

### 3. Mengaktifkan Auto-assign Public IP (PENTING!)
Agar setiap EC2 yang dipasang di subnet ini otomatis mendapatkan Alamat IP Publik:
1. Centang **`subnet-simtugas-public-1`**.
2. Klik tombol **Actions** di pojok kanan atas -> Pilih **Edit subnet settings**.
3. Pada bagian **Auto-assign IP settings**, centang:
   - ✅ **Enable auto-assign public IPv4 address**
4. Klik **Save**.
5. Lakukan langkah 1-4 yang sama untuk **`subnet-simtugas-public-2`**.

---

## 🌍 Langkah 3: Membuat Internet Gateway (IGW) & Attach ke VPC

1. Pada menu sebelah kiri VPC, klik **Internet gateways** -> Klik **Create internet gateway**.
2. **Name tag**: `igw-simtugas-tkj`.
3. Klik **Create internet gateway**.
4. Setelah dibuat, klik tombol **Actions** -> Pilih **Attach to VPC**.
5. Pilih VPC: `vpc-simtugas-tkj` -> Klik **Attach internet gateway**.

---

## 🛣️ Langkah 4: Membuat Route Table Public & Konfigurasi Routing

1. Pada menu sebelah kiri VPC, klik **Route tables** -> Klik **Create route table**.
2. Konfigurasi:
   - **Name**: `rtb-simtugas-public`
   - **VPC**: Pilih `vpc-simtugas-tkj`
3. Klik **Create route table**.

### 1. Menambahkan Route ke Internet Gateway
1. Klik tab **Routes** -> Klik tombol **Edit routes**.
2. Klik **Add route**:
   - **Destination**: `0.0.0.0/0`
   - **Target**: Pilih **Internet Gateway** -> Pilih `igw-simtugas-tkj`.
3. Klik **Save changes**.

### 2. Memasukkan (Asosiasi) Kedua Subnet ke Route Table
1. Klik tab **Subnet associations** -> Klik tombol **Edit subnet associations**.
2. Centang kedua subnet:
   - ✅ `subnet-simtugas-public-1`
   - ✅ `subnet-simtugas-public-2`
3. Klik **Save associations**.

---

## 🛡️ Langkah 5: Membuat Security Group Manual untuk EC2

1. Buka layanan **EC2** di AWS Console -> Pada menu kiri klik **Security Groups**.
2. Klik tombol **Create security group**.
3. Konfigurasi dasar:
   - **Security group name**: `simtugas-ec2-sg`
   - **Description**: `Security group akses web dan ssh aplikasi simtugas tkj`
   - **VPC**: Pilih VPC yang tadi dibuat (`vpc-simtugas-tkj`).
4. Pada bagian **Inbound rules**, klik **Add rule** untuk menambahkan 2 aturan berikut:
   - **Rule 1 (SSH)**:
     - **Type**: `SSH` | **Port**: `22` | **Source**: `Anywhere-IPv4` (`0.0.0.0/0`)
   - **Rule 2 (Aplikasi Flask)**:
     - **Type**: `Custom TCP` | **Port**: `5000` | **Source**: `Anywhere-IPv4` (`0.0.0.0/0`)
5. Klik **Create security group**.

---

## 🗄️ Langkah 6: Membuat Tabel di AWS DynamoDB

1. Buka layanan **Amazon DynamoDB** -> Klik tombol **Create table**.
2. Konfigurasi tabel:
   - **Table name**: `tkj_tugas`
   - **Partition key**: `id`
   - **Data type**: `String`
3. Biarkan opsi lainnya default (**Default settings**).
4. Klik **Create table** dan tunggu statusnya menjadi **Active**.

---

## 🪣 Langkah 7: Membuat Bucket di AWS S3 (100% Private)

1. Buka layanan **Amazon S3** -> Klik tombol **Create bucket**.
2. Konfigurasi bucket:
   - **Bucket name**: Masukkan nama unik global, contoh: `tkj-tugas-siswa-smk1` *(gunakan huruf kecil dan angka)*.
   - **AWS Region**: Pilih region yang sama dengan DynamoDB (contoh: `us-east-1`).
   - **Block Public Access settings for this bucket**: Biarkan **Block *all* public access** tetap **CENTANG AKTIF (ON)**. Aplikasi kita menggunakan Boto3 streaming dari server sehingga S3 tidak perlu dibuka ke publik.
3. Klik **Create bucket**.

---

## 🔑 Langkah 8: Mengambil Kredensial AWS

### Opsi A: Jika Menggunakan AWS Academy / Learner Lab
1. Buka dashboard **AWS Academy Learner Lab**.
2. Klik tombol **AWS Details** di sudut kanan atas.
3. Klik link **Show** di bagian **AWS CLI credentials**.
4. Salin ketiga nilai berikut:
   - `aws_access_key_id`
   - `aws_secret_access_key`
   - `aws_session_token`

### Opsi B: Jika Menggunakan IAM User Pribadi
1. Salin `AWS_ACCESS_KEY_ID` dan `AWS_SECRET_ACCESS_KEY`.
2. Kosongkan nilai `AWS_SESSION_TOKEN`.

---

## 🖥️ Langkah 9: Membuat & Meluncurkan EC2 Instance

Setelah VPC, Security Group, DynamoDB, dan S3 siap, sekarang kita luncurkan EC2:

1. Pada menu EC2, klik **Instances** -> Klik **Launch instances**.
2. Konfigurasi instance:
   - **Name**: `Server-SIMTUGAS-TKJ`
   - **Application and OS Images (AMI)**: **Ubuntu Server 22.04 LTS** atau **Ubuntu Server 24.04 LTS**.
   - **Instance type**: `t2.micro` atau `t3.micro` (Free tier eligible).
   - **Key pair (login)**: Pilih key pair yang sudah Anda miliki (atau buat baru jika belum punya).
3. **Network settings** (Klik tombol **Edit** di kanan):
   - **VPC**: Pilih `vpc-simtugas-tkj`
   - **Subnet**: Pilih `subnet-simtugas-public-1`
   - **Auto-assign public IP**: Pastikan statusnya **Enable**
   - **Firewall (security groups)**: Pilih **Select existing security group**
   - **Common security groups**: Centang **`simtugas-ec2-sg`** yang telah kita buat di Langkah 5.
4. Klik **Launch instance**.
5. Tunggu hingga status instance menjadi **Running**, lalu catat **Public IPv4 address**-nya.

---

## 🚀 Langkah 10: Deploy & Menjalankan Aplikasi di EC2

### 1. Connect ke EC2 Instance
Buka terminal lokal Anda atau gunakan tombol **Connect -> EC2 Instance Connect** dari AWS Console.

### 2. Update Sistem & Install Paket Pendukung
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
```

### 3. Clone Repository
```bash
git clone https://github.com/ArRosid/praktek-aws-tkj.git
cd praktek-aws-tkj/3-pengumpulan-tugas
```

### 4. Buat Virtual Environment & Install Library
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Konfigurasi File Environment (`.env`)
Salin file `sample.env` menjadi `.env`:
```bash
cp sample.env .env
nano .env
```

Sesuaikan isi file `.env`:
```ini
# Pilih Tema Tampilan: BLUE atau GREEN
STYLE=BLUE

# AWS Region
AWS_DEFAULT_REGION=us-east-1

# Nama Tabel DynamoDB
DYNAMODB_TABLE_NAME=tkj_tugas

# Nama Bucket S3 Anda
S3_BUCKET_NAME=tkj-tugas-siswa-smk1

# Kredensial AWS
AWS_ACCESS_KEY_ID=ASIAXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjE... (kosongkan jika bukan AWS Academy)

# Port Aplikasi
PORT=5000
```
> **Tip Tema (STYLE)**: Ubah `STYLE=GREEN` jika ingin tampilan portal bernuansa hijau segar (emerald), atau `STYLE=BLUE` untuk tema biru teknologi. Simpan dengan `Ctrl + O`, `Enter`, lalu keluar dengan `Ctrl + X`.

### 6. Jalankan Server Aplikasi
```bash
python3 app.py
```

Jika ingin aplikasi tetap berjalan saat terminal ditutup, gunakan perintah background:
```bash
nohup python3 app.py > app.log 2>&1 &
```

---

## 🧪 Langkah 11: Pengujian Alur Aplikasi (Testing)

Buka browser Anda dan akses alamat IP publik EC2:
```
http://<PUBLIC_IP_EC2>:5000
```

### Skenario Pengujian:
1. **Guru Menambahkan Kelas**:
   - Masuk ke tab **Kelola Kelas & Siswa (Guru)**.
   - Pada form **Tambah Data Kelas**, masukkan misal: `X TKJ 1` -> Klik **Tambah Kelas**.
   - Tambahkan lagi kelas: `XI TKJ 2`.
2. **Guru Menambahkan Siswa**:
   - Pada form **Tambah Data Siswa**, pilih kelas `X TKJ 1`.
   - Masukkan Nama Siswa: `Ahmad Pratama`, NIS: `10892` -> Klik **Tambah Siswa**.
   - Tambahkan beberapa siswa lainnya.
3. **Siswa Mengumpulkan Tugas**:
   - Buka tab **Kumpulkan Tugas (Siswa)**.
   - Pilih Kelas: `X TKJ 1`.
   - Pada pilihan siswa, pilih nama `Ahmad Pratama`.
   - Tuliskan Judul Tugas, contoh: `Laporan Praktikum Topologi Star & UTP`.
   - Unggah dokumen tugas berformat **.PDF**.
   - Klik **Kumpulkan Tugas Sekarang 🚀**.
4. **Verifikasi Penyimpanan**:
   - Buka AWS Console **DynamoDB** -> Periksa tabel `tkj_tugas` -> Item baru dengan `tipe = "tugas"` telah masuk.
   - Buka AWS Console **S3** -> Periksa bucket `tkj-tugas-siswa-...` -> Folder `tugas/` berisi file PDF yang terunggah.
5. **Guru Rekap & Melihat Tugas**:
   - Buka tab **Rekap Tugas Masuk (Guru)**.
   - Klik tombol **Buka** untuk melihat preview PDF langsung di browser, atau tombol **Unduh** untuk mengunduh dokumen siswa.
