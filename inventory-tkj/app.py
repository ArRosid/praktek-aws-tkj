#!/usr/bin/env python3
"""
SIMBAR TKJ - Server Backend (Flask + Boto3)
Autentikasi AWS melalui Environment Variable (.env / sample.env).
S3 Bucket 100% Private (Block Public Access ON), foto distreaming via Boto3.
Port aplikasi dibaca dari environment variable 'PORT'.
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
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # Maks 10MB upload foto

# 2. Ambil Konfigurasi dari Environment Variable
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "tkj_inventory")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "tkj-inventory-photos-smk")

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

# Clients Boto3
dynamodb_resource = boto3.resource("dynamodb", **boto3_kwargs)
dynamodb_client = boto3.client("dynamodb", **boto3_kwargs)
s3_client = boto3.client("s3", **boto3_kwargs)
table = dynamodb_resource.Table(DYNAMODB_TABLE_NAME)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def decimal_to_native(obj):
    """Konversi tipe Decimal DynamoDB ke tipe standar Python (int/float/str)"""
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
    return render_template("index.html")


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.route("/api/config", methods=["GET"])
def get_config():
    """Mengembalikan status konfigurasi resource AWS"""
    has_keys = bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
    return jsonify({
        "success": True,
        "region": AWS_REGION,
        "dynamodb_table": DYNAMODB_TABLE_NAME,
        "s3_bucket": S3_BUCKET_NAME,
        "has_credentials": has_keys,
        "has_session_token": bool(AWS_SESSION_TOKEN)
    })


@app.route("/api/items", methods=["GET"])
def list_items():
    """Mengambil seluruh data inventaris dari DynamoDB"""
    try:
        response = table.scan()
        items = response.get("Items", [])
        cleaned_items = decimal_to_native(items)
        cleaned_items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jsonify({"success": True, "data": cleaned_items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/items/<item_id>", methods=["GET"])
def get_item(item_id):
    """Mengambil detail 1 barang"""
    try:
        response = table.get_item(Key={"id": item_id})
        item = response.get("Item")
        if not item:
            return jsonify({"success": False, "message": "Barang tidak ditemukan"}), 404
        return jsonify({"success": True, "data": decimal_to_native(item)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/items", methods=["POST"])
def create_item():
    """Menambah barang baru dan upload foto ke S3 via Boto3 (Private S3)"""
    try:
        nama_barang = request.form.get("nama_barang", "").strip()
        kategori = request.form.get("kategori", "Lainnya").strip()
        kode_barang = request.form.get("kode_barang", "").strip()
        lokasi = request.form.get("lokasi", "Lab TKJ 1").strip()
        kondisi = request.form.get("kondisi", "Baik").strip()
        jumlah = int(request.form.get("jumlah", 1))
        spesifikasi = request.form.get("spesifikasi", "").strip()
        keterangan = request.form.get("keterangan", "").strip()

        if not nama_barang:
            return jsonify({"success": False, "message": "Nama barang wajib diisi"}), 400

        item_id = "TKJ-" + uuid.uuid4().hex[:8].upper()
        now_iso = datetime.utcnow().isoformat() + "Z"
        
        # Upload foto ke S3 Private via Boto3
        s3_key = ""
        if "foto" in request.files:
            file = request.files["foto"]
            if file and file.filename != "" and allowed_file(file.filename):
                ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
                s3_key = f"photos/{item_id}.{ext}"
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET_NAME,
                    s3_key,
                    ExtraArgs={"ContentType": file.content_type}
                )

        new_item = {
            "id": item_id,
            "nama_barang": nama_barang,
            "kategori": kategori,
            "kode_barang": kode_barang if kode_barang else f"TKJ-{item_id[:8]}",
            "lokasi": lokasi,
            "kondisi": kondisi,
            "jumlah": jumlah,
            "spesifikasi": spesifikasi,
            "keterangan": keterangan,
            "s3_key": s3_key,
            "created_at": now_iso,
            "updated_at": now_iso
        }

        table.put_item(Item=new_item)
        return jsonify({
            "success": True,
            "message": "Barang berhasil disimpan ke DynamoDB & S3!",
            "data": decimal_to_native(new_item)
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    """Memperbarui informasi barang dan opsi ganti foto"""
    try:
        existing = table.get_item(Key={"id": item_id}).get("Item")
        if not existing:
            return jsonify({"success": False, "message": "Barang tidak ditemukan"}), 404

        nama_barang = request.form.get("nama_barang", existing.get("nama_barang")).strip()
        kategori = request.form.get("kategori", existing.get("kategori")).strip()
        kode_barang = request.form.get("kode_barang", existing.get("kode_barang")).strip()
        lokasi = request.form.get("lokasi", existing.get("lokasi")).strip()
        kondisi = request.form.get("kondisi", existing.get("kondisi")).strip()
        jumlah = int(request.form.get("jumlah", existing.get("jumlah", 1)))
        spesifikasi = request.form.get("spesifikasi", existing.get("spesifikasi", "")).strip()
        keterangan = request.form.get("keterangan", existing.get("keterangan", "")).strip()
        
        s3_key = existing.get("s3_key", "")
        
        # Upload foto baru ke S3 jika ada
        if "foto" in request.files:
            file = request.files["foto"]
            if file and file.filename != "" and allowed_file(file.filename):
                ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
                new_s3_key = f"photos/{item_id}.{ext}"
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET_NAME,
                    new_s3_key,
                    ExtraArgs={"ContentType": file.content_type}
                )
                s3_key = new_s3_key

        now_iso = datetime.utcnow().isoformat() + "Z"
        updated_item = {
            "id": item_id,
            "nama_barang": nama_barang,
            "kategori": kategori,
            "kode_barang": kode_barang,
            "lokasi": lokasi,
            "kondisi": kondisi,
            "jumlah": jumlah,
            "spesifikasi": spesifikasi,
            "keterangan": keterangan,
            "s3_key": s3_key,
            "created_at": existing.get("created_at", now_iso),
            "updated_at": now_iso
        }

        table.put_item(Item=updated_item)
        return jsonify({
            "success": True,
            "message": "Data barang berhasil diperbarui!",
            "data": decimal_to_native(updated_item)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Menghapus barang dari DynamoDB dan foto dari S3"""
    try:
        existing = table.get_item(Key={"id": item_id}).get("Item")
        if not existing:
            return jsonify({"success": False, "message": "Barang tidak ditemukan"}), 404

        s3_key = existing.get("s3_key")
        if s3_key:
            try:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            except Exception as s3_err:
                print(f"[Warning] Gagal menghapus file S3 {s3_key}: {s3_err}")

        table.delete_item(Key={"id": item_id})
        return jsonify({"success": True, "message": "Barang berhasil dihapus!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/items/<item_id>/photo", methods=["GET"])
def get_item_photo(item_id):
    """
    Streaming foto langsung dari S3 via Boto3.
    S3 Bucket tetap 100% PRIVATE (Block Public Access ON), tanpa bucket policy.
    """
    try:
        response = table.get_item(Key={"id": item_id})
        item = response.get("Item")
        if not item or not item.get("s3_key"):
            return jsonify({"error": "Foto tidak ditemukan"}), 404

        s3_key = item["s3_key"]
        s3_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        content_type = s3_obj.get("ContentType", "image/jpeg")
        body = s3_obj["Body"].read()

        return send_file(
            io.BytesIO(body),
            mimetype=content_type,
            as_attachment=False,
            max_age=3600
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return jsonify({"error": "Foto tidak ditemukan di S3"}), 404
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Baca PORT dari environment variable (default: 5000)
    port = int(os.getenv("PORT", 5000))
    print("==================================================")
    print("      SIMBAR TKJ - INVENTORY MANAGEMENT SERVER    ")
    print("==================================================")
    print(f"Region   : {AWS_REGION}")
    print(f"DynamoDB : {DYNAMODB_TABLE_NAME}")
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"Port     : {port}")
    print(f"URL      : http://0.0.0.0:{port}")
    print("==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
