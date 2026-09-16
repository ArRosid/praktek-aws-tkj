#!/usr/bin/env python3
"""
SISTEM PENGUMPULAN TUGAS SISWA TKJ
AWS EC2 + DynamoDB (Metadata & Database) + S3 (Penyimpanan File PDF Private)
Konfigurasi Tema: STYLE=BLUE atau STYLE=GREEN di file .env
"""

import io
import os
import uuid
from datetime import datetime
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

# 1. Load Environment Variables dari file .env
load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # Maksimal 25MB upload file PDF

# 2. Ambil Konfigurasi dari Environment Variable
STYLE = os.getenv("STYLE", "BLUE").strip().upper()
if STYLE not in ["BLUE", "GREEN"]:
    STYLE = "BLUE"

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1").strip()
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "tkj_tugas").strip()
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "tkj-tugas-siswa-smk").strip()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

# 3. Inisialisasi Kredensial Boto3
boto3_kwargs = {
    "region_name": AWS_REGION
}

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    boto3_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID.strip()
    boto3_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY.strip()
    if AWS_SESSION_TOKEN and AWS_SESSION_TOKEN.strip():
        boto3_kwargs["aws_session_token"] = AWS_SESSION_TOKEN.strip()

# Inisialisasi Client & Resource Boto3
dynamodb_resource = boto3.resource("dynamodb", **boto3_kwargs)
dynamodb_client = boto3.client("dynamodb", **boto3_kwargs)
s3_client = boto3.client("s3", **boto3_kwargs)
table = dynamodb_resource.Table(DYNAMODB_TABLE_NAME)


def is_pdf(filename):
    """Memastikan file yang diupload berekstensi .pdf"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pdf"


def format_size(bytes_size):
    """Format ukuran file ke KB / MB"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def decimal_to_native(obj):
    """Konversi Decimal bawaan DynamoDB ke tipe standar Python"""
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


# ==============================================================================
# ROUTE FRONTEND
# ==============================================================================
@app.route("/")
def index():
    # Pass tema style (blue / green) ke template
    return render_template("index.html", style=STYLE.lower(), style_name=STYLE)


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.route("/api/config", methods=["GET"])
def get_config():
    """Mengembalikan status konfigurasi AWS dan tema saat ini"""
    try:
        session = boto3.Session(**boto3_kwargs)
        creds = session.get_credentials()
        has_credentials = creds is not None
        auth_method = "IAM Role / Instance Profile" if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) else "Static Keys (.env)"
    except Exception:
        has_credentials = False
        auth_method = "Unknown"

    return jsonify({
        "success": True,
        "style": STYLE.lower(),
        "style_name": STYLE,
        "region": AWS_REGION,
        "dynamodb_table": DYNAMODB_TABLE_NAME,
        "s3_bucket": S3_BUCKET_NAME,
        "has_credentials": has_credentials,
        "auth_method": auth_method
    })


# ------------------------------------------------------------------------------
# 1. KELOLA KELAS
# ------------------------------------------------------------------------------
@app.route("/api/kelas", methods=["GET"])
def list_kelas():
    """Mengambil semua data kelas dari DynamoDB"""
    try:
        response = table.scan()
        items = [item for item in response.get("Items", []) if item.get("tipe") == "kelas"]
        cleaned_items = decimal_to_native(items)
        cleaned_items.sort(key=lambda x: x.get("nama_kelas", ""))
        return jsonify({"success": True, "data": cleaned_items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/kelas", methods=["POST"])
def create_kelas():
    """Menambahkan data kelas baru"""
    try:
        nama_kelas = request.json.get("nama_kelas", "").strip()
        jurusan = request.json.get("jurusan", "Teknik Komputer & Jaringan").strip()

        if not nama_kelas:
            return jsonify({"success": False, "message": "Nama kelas wajib diisi!"}), 400

        kelas_id = "KELAS-" + uuid.uuid4().hex[:6].upper()
        now_iso = datetime.utcnow().isoformat() + "Z"

        new_kelas = {
            "id": kelas_id,
            "tipe": "kelas",
            "nama_kelas": nama_kelas,
            "jurusan": jurusan,
            "created_at": now_iso
        }

        table.put_item(Item=new_kelas)
        return jsonify({
            "success": True,
            "message": f"Kelas '{nama_kelas}' berhasil ditambahkan!",
            "data": decimal_to_native(new_kelas)
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/kelas/<kelas_id>", methods=["DELETE"])
def delete_kelas(kelas_id):
    """Menghapus data kelas dari DynamoDB"""
    try:
        table.delete_item(Key={"id": kelas_id})
        return jsonify({"success": True, "message": "Kelas berhasil dihapus!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------------------------------------------------------------------
# 2. KELOLA SISWA
# ------------------------------------------------------------------------------
@app.route("/api/siswa", methods=["GET"])
def list_siswa():
    """Mengambil data siswa (opsional filter ?kelas_id=...)"""
    try:
        kelas_id = request.args.get("kelas_id")
        response = table.scan()
        all_items = response.get("Items", [])

        siswa_items = [
            item for item in all_items 
            if item.get("tipe") == "siswa" and (not kelas_id or item.get("kelas_id") == kelas_id)
        ]
        cleaned_items = decimal_to_native(siswa_items)
        cleaned_items.sort(key=lambda x: x.get("nama_siswa", "").lower())
        return jsonify({"success": True, "data": cleaned_items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/siswa", methods=["POST"])
def create_siswa():
    """Menambahkan data siswa baru ke dalam kelas tertentu"""
    try:
        nama_siswa = request.json.get("nama_siswa", "").strip()
        kelas_id = request.json.get("kelas_id", "").strip()
        nis = request.json.get("nis", "").strip()

        if not nama_siswa or not kelas_id:
            return jsonify({"success": False, "message": "Nama siswa dan Kelas wajib dipilih!"}), 400

        # Ambil nama kelas dari DynamoDB untuk kemudahan display
        kelas_resp = table.get_item(Key={"id": kelas_id})
        kelas_item = kelas_resp.get("Item")
        nama_kelas = kelas_item.get("nama_kelas", "Unknown") if kelas_item else "Unknown"

        siswa_id = "SISWA-" + uuid.uuid4().hex[:6].upper()
        now_iso = datetime.utcnow().isoformat() + "Z"

        new_siswa = {
            "id": siswa_id,
            "tipe": "siswa",
            "nama_siswa": nama_siswa,
            "nis": nis if nis else "-",
            "kelas_id": kelas_id,
            "nama_kelas": nama_kelas,
            "created_at": now_iso
        }

        table.put_item(Item=new_siswa)
        return jsonify({
            "success": True,
            "message": f"Siswa '{nama_siswa}' berhasil ditambahkan ke kelas {nama_kelas}!",
            "data": decimal_to_native(new_siswa)
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/siswa/<siswa_id>", methods=["DELETE"])
def delete_siswa(siswa_id):
    """Menghapus data siswa dari DynamoDB"""
    try:
        table.delete_item(Key={"id": siswa_id})
        return jsonify({"success": True, "message": "Siswa berhasil dihapus!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------------------------------------------------------------------
# 3. PENGUMPULAN TUGAS (UPLOAD PDF S3 + SIMPAN METADATA DYNAMODB)
# ------------------------------------------------------------------------------
@app.route("/api/tugas", methods=["GET"])
def list_tugas():
    """Melihat daftar seluruh tugas yang sudah dikumpulkan siswa"""
    try:
        kelas_id = request.args.get("kelas_id")
        response = table.scan()
        all_items = response.get("Items", [])

        tugas_items = [
            item for item in all_items 
            if item.get("tipe") == "tugas" and (not kelas_id or item.get("kelas_id") == kelas_id)
        ]
        cleaned_items = decimal_to_native(tugas_items)
        cleaned_items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jsonify({"success": True, "data": cleaned_items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tugas", methods=["POST"])
def submit_tugas():
    """
    Siswa mengumpulkan tugas:
    - Metadata disimpan ke DynamoDB
    - File PDF diunggah ke S3 Private via Boto3
    """
    try:
        kelas_id = request.form.get("kelas_id", "").strip()
        siswa_id = request.form.get("siswa_id", "").strip()
        judul_tugas = request.form.get("judul_tugas", "").strip()
        catatan = request.form.get("catatan", "").strip()

        if not kelas_id or not siswa_id:
            return jsonify({"success": False, "message": "Pilih Kelas dan Nama Siswa terlebih dahulu!"}), 400

        if not judul_tugas:
            return jsonify({"success": False, "message": "Judul tugas wajib diisi!"}), 400

        if "file_tugas" not in request.files:
            return jsonify({"success": False, "message": "File PDF tugas wajib diunggah!"}), 400

        file = request.files["file_tugas"]
        if file.filename == "":
            return jsonify({"success": False, "message": "Silakan pilih file tugas!"}), 400

        if not is_pdf(file.filename):
            return jsonify({"success": False, "message": "Format file tidak valid! Wajib format PDF (.pdf)"}), 400

        # Ambil data siswa & kelas untuk info lengkap
        siswa_resp = table.get_item(Key={"id": siswa_id})
        siswa_item = siswa_resp.get("Item")
        nama_siswa = siswa_item.get("nama_siswa", "Siswa") if siswa_item else "Siswa"
        nama_kelas = siswa_item.get("nama_kelas", "Kelas") if siswa_item else "Kelas"

        tugas_id = "TUGAS-" + uuid.uuid4().hex[:8].upper()
        clean_filename = secure_filename(file.filename)
        s3_key = f"tugas/{tugas_id}_{clean_filename}"

        # Hitung ukuran file
        file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        file.seek(0)
        formatted_size = format_size(size_bytes)

        # Upload file PDF ke S3 Private via Boto3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": "application/pdf",
                "ContentDisposition": f'inline; filename="{clean_filename}"'
            }
        )

        now_iso = datetime.utcnow().isoformat() + "Z"
        new_tugas = {
            "id": tugas_id,
            "tipe": "tugas",
            "siswa_id": siswa_id,
            "nama_siswa": nama_siswa,
            "kelas_id": kelas_id,
            "nama_kelas": nama_kelas,
            "judul_tugas": judul_tugas,
            "catatan": catatan if catatan else "-",
            "file_name": clean_filename,
            "file_size": formatted_size,
            "s3_key": s3_key,
            "status": "Terkumpul",
            "created_at": now_iso
        }

        # Simpan metadata ke DynamoDB
        table.put_item(Item=new_tugas)

        return jsonify({
            "success": True,
            "message": f"Tugas berhasil dikumpulkan oleh {nama_siswa}!",
            "data": decimal_to_native(new_tugas)
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tugas/<tugas_id>/file", methods=["GET"])
def view_or_download_tugas(tugas_id):
    """
    Streaming file PDF tugas langsung dari S3 via Boto3.
    S3 Bucket tetap 100% PRIVATE (Block Public Access ON), tanpa perlu public policy.
    Bisa dibuka langsung (preview inline) di browser siswa atau guru!
    """
    try:
        response = table.get_item(Key={"id": tugas_id})
        tugas = response.get("Item")
        if not tugas or not tugas.get("s3_key"):
            return jsonify({"error": "File tugas tidak ditemukan di database"}), 404

        s3_key = tugas["s3_key"]
        file_name = tugas.get("file_name", "tugas.pdf")
        
        s3_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        body = s3_obj["Body"].read()

        # Opsi: download langsung atau preview di browser
        as_attachment = request.args.get("download", "false").lower() == "true"

        return send_file(
            io.BytesIO(body),
            mimetype="application/pdf",
            as_attachment=as_attachment,
            download_name=file_name
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return jsonify({"error": "File PDF tidak ditemukan di S3"}), 404
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tugas/<tugas_id>", methods=["DELETE"])
def delete_tugas(tugas_id):
    """Menghapus catatan tugas di DynamoDB dan file PDF di S3"""
    try:
        response = table.get_item(Key={"id": tugas_id})
        tugas = response.get("Item")
        if not tugas:
            return jsonify({"success": False, "message": "Tugas tidak ditemukan"}), 404

        s3_key = tugas.get("s3_key")
        if s3_key:
            try:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            except Exception as s3_err:
                print(f"[Warning] Gagal menghapus file S3 {s3_key}: {s3_err}")

        table.delete_item(Key={"id": tugas_id})
        return jsonify({"success": True, "message": "Tugas berhasil dihapus!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# MAIN RUNNER
# ==============================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("==================================================")
    print("  SIMTUGAS TKJ - SISTEM PENGUMPULAN TUGAS SISWA   ")
    print("==================================================")
    print(f"Tema (STYLE): {STYLE}")
    print(f"Region      : {AWS_REGION}")
    print(f"DynamoDB    : {DYNAMODB_TABLE_NAME}")
    print(f"S3 Bucket   : {S3_BUCKET_NAME}")
    print(f"Port        : {port}")
    print(f"URL         : http://0.0.0.0:{port}")
    print("==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
