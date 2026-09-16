# ⚖️ Panduan Setup Application Load Balancer (ALB) - SIMTUGAS TKJ

Panduan ini menjelaskan cara mengonfigurasi **AWS Application Load Balancer (ALB)** di atas arsitektur yang sudah kita buat sebelumnya.

---

## 🎯 Skenario Praktikum (Blue/Green Deployment)

Asumsi arsitektur saat ini:
Kita telah memiliki **2 EC2 Instance** yang berjalan di VPC `vpc-simtugas-tkj`:
1. **Server 1 (Tema BLUE)**: Berada di `subnet-simtugas-public-1`, berjalan di port 5000 dengan konfigurasi `.env` `STYLE=BLUE`.
2. **Server 2 (Tema GREEN)**: Berada di `subnet-simtugas-public-2`, berjalan di port 5000 dengan konfigurasi `.env` `STYLE=GREEN`.
3. **Database & Storage Terpusat**: Kedua server terhubung ke tabel DynamoDB (`tkj_tugas`) dan S3 bucket private yang sama.

Load Balancer akan bertindak sebagai pintu gerbang utama (*Single Point of Entry*) di **Port 80**, mendistribusikan lalu lintas secara bergantian (*Round Robin*) ke Server Blue dan Server Green.

```
                         Internet (Pengguna)
                                 │
                          [Port 80 (HTTP)]
                                 ▼
                   ┌───────────────────────────┐
                   │ Application Load Balancer │
                   │    (alb-simtugas-tkj)     │
                   └─────────────┬─────────────┘
                                 │ Forward via Target Group (Port 5000)
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [Server 1 - BLUE]               [Server 2 - GREEN]
      Subnet Public 1 (Port 5000)     Subnet Public 2 (Port 5000)
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                     [DynamoDB] & [S3 Private]
```

---

## 🛠️ Langkah 1: Membuat Security Group untuk Load Balancer

Load Balancer memerlukan Security Group tersendiri untuk menerima koneksi HTTP standar (Port 80) dari publik internet.

1. Buka AWS Management Console -> Layanan **EC2**.
2. Pada menu sebelah kiri, klik **Security Groups** -> Klik tombol **Create security group**.
3. Isi konfigurasi:
   - **Security group name**: `simtugas-alb-sg`
   - **Description**: `Security group publik untuk Application Load Balancer SIMTUGAS`
   - **VPC**: Pilih VPC yang sudah dibuat (`vpc-simtugas-tkj`).
4. Pada bagian **Inbound rules**, klik **Add rule**:
   - **Type**: `HTTP`
   - **Protocol**: `TCP`
   - **Port range**: `80`
   - **Source**: `Anywhere-IPv4` (`0.0.0.0/0`)
5. Pada bagian **Outbound rules**, biarkan default (**All traffic** ke `0.0.0.0/0`).
6. Klik **Create security group**.

> 💡 **Tips Best Practice (Opsional)**: Pada Security Group EC2 (`simtugas-ec2-sg`), Anda dapat mengubah rule Port 5000 agar sourcenya diarahkan ke Security Group `simtugas-alb-sg` (bukan `0.0.0.0/0`), sehingga instance EC2 hanya dapat diakses melalui Load Balancer.

---

## 🎯 Langkah 2: Membuat Target Group

Target Group berfungsi mendaftarkan server EC2 tujuan yang akan menerima beban lalu lintas dari Load Balancer, serta melakukan *Health Check* otomatis.

1. Pada menu sebelah kiri EC2, di bagian **Load Balancing**, klik **Target Groups**.
2. Klik tombol **Create target group**.
3. **Basic configuration**:
   - **Choose a target type**: Pilih **Instances**.
   - **Target group name**: `tg-simtugas-app`
   - **Protocol**: `HTTP`
   - **Port**: `5000` *(karena aplikasi Flask kita berjalan di port 5000)*
   - **IP address type**: `IPv4`
   - **VPC**: Pilih `vpc-simtugas-tkj`.
   - **Protocol version**: `HTTP1`.
4. **Health checks**:
   - Biarkan pengaturan default dari AWS:
     - **Health check protocol**: `HTTP`
     - **Health check path**: `/` *(default AWS)*
   - Opsi *Advanced health check settings* tidak perlu diubah (biarkan default).
5. Klik **Next**.
6. **Register targets**:
   - Pada tabel **Available instances**, centang kedua EC2 instance Anda:
     - ✅ `Server-SIMTUGAS-BLUE`
     - ✅ `Server-SIMTUGAS-GREEN`
   - **Ports for the selected instances**: pastikan tertulis `5000`.
   - Klik tombol **Include as pending below**.
   - Pastikan kedua instance sudah muncul di tabel **Review targets**.
7. Klik **Create target group**.

---

## ⚖️ Langkah 3: Membuat Application Load Balancer (ALB)

1. Pada menu sebelah kiri EC2, klik **Load Balancers**.
2. Klik tombol **Create load balancer**.
3. Pada kartu **Application Load Balancer**, klik tombol **Create**.
4. **Basic configuration**:
   - **Load balancer name**: `alb-simtugas-tkj`
   - **Scheme**: Pilih **Internet-facing**
   - **IP address type**: `IPv4`
5. **Network mapping**:
   - **VPC**: Pilih `vpc-simtugas-tkj`.
   - **Mappings** (Pilih kedua subnet public yang telah kita buat):
     - Availability Zone 1: Centang subnet `subnet-simtugas-public-1`.
     - Availability Zone 2: Centang subnet `subnet-simtugas-public-2`.
6. **Security groups**:
   - Hapus pilihan *default security group*.
   - Pilih Security Group yang tadi dibuat: **`simtugas-alb-sg`**.
7. **Listeners and routing**:
   - **Listener**: Protocol `HTTP` | Port `80`.
   - **Default action**: Pilih **Forward to** -> Pilih Target Group **`tg-simtugas-app`**.
8. Gulir ke bawah dan klik tombol **Create load balancer**.

---

## 🧪 Langkah 4: Pengujian & Verifikasi Load Balancing

1. **Tunggu Status Active**:
   - Pada halaman **Load Balancers**, tunggu hingga kolom **State** berubah dari *Provisioning* menjadi **Active** (memerlukan waktu sekitar 1-2 menit).
2. **Periksa Health Check**:
   - Buka menu **Target Groups** -> Klik `tg-simtugas-app` -> Buka tab **Targets**.
   - Pastikan kedua instance menunjukkan status **Healthy** (hijau).
3. **Uji di Browser**:
   - Kembali ke halaman **Load Balancers**, klik `alb-simtugas-tkj`.
   - Salin nilai **DNS name**, contoh:
     ```
     alb-simtugas-tkj-123456789.us-east-1.elb.amazonaws.com
     ```
   - Buka tab baru di browser Anda dan masukkan DNS name tersebut (cukup gunakan port 80 default, tanpa menuliskan `:5000`):
     ```
     http://alb-simtugas-tkj-123456789.us-east-1.elb.amazonaws.com
     ```
4. **Bukti Pembagian Beban (Round Robin)**:
   - Tekan tombol **Refresh (F5)** beberapa kali di browser:
     - Anda akan melihat tema aplikasi berganti antara **BIRU (BLUE)** dan **HIJAU (GREEN)**!
     - Badge di header juga akan berganti antara `TEMA: BLUE` dan `TEMA: GREEN`.
5. **Uji Konsistensi Data Terpusat**:
   - Tambahkan tugas di halaman saat tema sedang Biru.
   - Lakukan refresh hingga masuk ke halaman tema Hijau.
   - Buka tab **Rekap Tugas Masuk**: data tugas yang tadi diunggah tetap muncul lengkap, membuktikan kedua server tersinkronisasi ke database **DynamoDB** dan **S3** yang sama!
