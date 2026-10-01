#!/usr/bin/env python3
"""
SIMPRES TKJ - ONLINE STUDENT ATTENDANCE SYSTEM
AWS EC2 + DynamoDB (Master Data & Attendance Log) + S3 (Selfie Photos & Medical Records)
Supports Theme: STYLE=INDIGO, STYLE=EMERALD, or STYLE=BLUE
Requires: YOUR_NAME environment variable for evaluation
"""

import io
import mimetypes
import os
import uuid
from datetime import datetime
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

# 1. Load configuration from .env file
load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024  # Max 15MB file upload

# 2. Read Configuration from Environment Variables
STYLE = os.getenv("STYLE", "INDIGO").strip().upper()
if STYLE not in ["INDIGO", "EMERALD", "BLUE"]:
    STYLE = "INDIGO"

YOUR_NAME = os.getenv("YOUR_NAME", "").strip()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1").strip()
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "tkj_presensi").strip()
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "tkj-presensi-siswa-smk").strip()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

# 3. Setup Boto3 Client & Resource
boto3_kwargs = {"region_name": AWS_REGION}

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    boto3_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID.strip()
    boto3_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY.strip()
    if AWS_SESSION_TOKEN and AWS_SESSION_TOKEN.strip():
        boto3_kwargs["aws_session_token"] = AWS_SESSION_TOKEN.strip()

dynamodb_resource = boto3.resource("dynamodb", **boto3_kwargs)
dynamodb_client = boto3.client("dynamodb", **boto3_kwargs)
s3_client = boto3.client("s3", **boto3_kwargs)
table = dynamodb_resource.Table(DYNAMODB_TABLE_NAME)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def is_allowed_image(filename):
    """Validate allowed image extensions"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def format_size(bytes_size):
    """Format bytes to human-readable size (KB / MB)"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def decimal_to_native(obj):
    """Convert DynamoDB Decimal types to standard Python primitives"""
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


# ==============================================================================
# HEALTH CHECK & FRONTEND ROUTES
# ==============================================================================
@app.route("/health", methods=["GET"])
@app.route("/health/", methods=["GET"])
def custom_health_check():
    """
    Mandatory Custom Health Check Endpoint for AWS Application Load Balancer Target Group.
    Returns HTTP 200 OK.
    """
    return jsonify({
        "status": "healthy",
        "service": "simpres-tkj",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route("/")
def index():
    """
    Attendance Portal & Dashboard Page.
    Intentionally returns HTTP 202 Accepted instead of standard 200 OK.
    - Browsers render HTTP 202 seamlessly like 200.
    - AWS Target Group defaults to expecting HTTP 200, so default '/' health checks will FAIL (Unhealthy [202]).
    - Only configuring the custom '/health' endpoint will return HTTP 200 and pass the health check.
    """
    return render_template(
        "index.html",
        style=STYLE.lower(),
        style_name=STYLE,
        your_name=YOUR_NAME,
        has_your_name=bool(YOUR_NAME)
    ), 202


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns AWS configuration status, theme, and candidate identification"""
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
        "your_name": YOUR_NAME,
        "your_name_set": bool(YOUR_NAME),
        "region": AWS_REGION,
        "dynamodb_table": DYNAMODB_TABLE_NAME,
        "s3_bucket": S3_BUCKET_NAME,
        "has_credentials": has_credentials,
        "auth_method": auth_method
    })


# ------------------------------------------------------------------------------
# 1. CLASS MANAGEMENT
# ------------------------------------------------------------------------------
@app.route("/api/kelas", methods=["GET"])
def list_kelas():
    """Retrieve all classes from DynamoDB"""
    try:
        response = table.scan()
        items = [item for item in response.get("Items", []) if item.get("tipe") == "kelas"]
        cleaned = decimal_to_native(items)
        cleaned.sort(key=lambda x: x.get("nama_kelas", ""))
        return jsonify({"success": True, "data": cleaned})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/kelas", methods=["POST"])
def create_kelas():
    """Create a new class"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        nama_kelas = data.get("nama_kelas", "").strip()
        jurusan = data.get("jurusan", "Computer Network Engineering (TKJ)").strip()

        if not nama_kelas:
            return jsonify({"success": False, "message": "Class name is required!"}), 400

        kelas_id = "CLASS-" + uuid.uuid4().hex[:6].upper()
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
            "message": f"Class '{nama_kelas}' successfully created!",
            "data": decimal_to_native(new_kelas)
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/kelas/<kelas_id>", methods=["DELETE"])
def delete_kelas(kelas_id):
    """Delete class item from DynamoDB"""
    try:
        table.delete_item(Key={"id": kelas_id})
        return jsonify({"success": True, "message": "Class deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------------------------------------------------------------------
# 2. STUDENT MANAGEMENT
# ------------------------------------------------------------------------------
@app.route("/api/siswa", methods=["GET"])
def list_siswa():
    """Retrieve students with optional class filter"""
    try:
        kelas_id = request.args.get("kelas_id")
        response = table.scan()
        all_items = response.get("Items", [])

        siswa_items = [
            item for item in all_items
            if item.get("tipe") == "siswa" and (not kelas_id or item.get("kelas_id") == kelas_id)
        ]
        cleaned = decimal_to_native(siswa_items)
        cleaned.sort(key=lambda x: x.get("nama_siswa", "").lower())
        return jsonify({"success": True, "data": cleaned})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/siswa", methods=["POST"])
def create_siswa():
    """Create a new student record"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        nama_siswa = data.get("nama_siswa", "").strip()
        kelas_id = data.get("kelas_id", "").strip()
        nis = data.get("nis", "").strip()

        if not nama_siswa or not kelas_id:
            return jsonify({"success": False, "message": "Student name and class are required!"}), 400

        kelas_resp = table.get_item(Key={"id": kelas_id})
        kelas_item = kelas_resp.get("Item")
        nama_kelas = kelas_item.get("nama_kelas", "Unknown") if kelas_item else "Unknown"

        siswa_id = "STD-" + uuid.uuid4().hex[:6].upper()
        now_iso = datetime.utcnow().isoformat() + "Z"

        new_siswa = {
            "id": siswa_id,
            "tipe": "siswa",
            "nis": nis if nis else "-",
            "nama_siswa": nama_siswa,
            "kelas_id": kelas_id,
            "nama_kelas": nama_kelas,
            "created_at": now_iso
        }

        table.put_item(Item=new_siswa)
        return jsonify({
            "success": True,
            "message": f"Student '{nama_siswa}' successfully added!",
            "data": decimal_to_native(new_siswa)
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/siswa/<siswa_id>", methods=["DELETE"])
def delete_siswa(siswa_id):
    """Delete student item from DynamoDB"""
    try:
        table.delete_item(Key={"id": siswa_id})
        return jsonify({"success": True, "message": "Student deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------------------------------------------------------------------
# 3. ATTENDANCE SUBMISSION (S3 PHOTO UPLOAD + DYNAMODB LOGGING)
# ------------------------------------------------------------------------------
@app.route("/api/presensi", methods=["GET"])
def list_presensi():
    """Retrieve attendance records with optional filtering (date, class, status)"""
    try:
        kelas_id = request.args.get("kelas_id")
        tanggal = request.args.get("tanggal")
        status = request.args.get("status")

        response = table.scan()
        all_items = response.get("Items", [])

        presensi_items = [
            item for item in all_items
            if item.get("tipe") == "presensi"
            and (not kelas_id or item.get("kelas_id") == kelas_id)
            and (not tanggal or item.get("tanggal") == tanggal)
            and (not status or item.get("status") == status)
        ]

        cleaned = decimal_to_native(presensi_items)
        cleaned.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jsonify({"success": True, "data": cleaned})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/presensi", methods=["POST"])
def submit_presensi():
    """
    Submit student attendance:
    - Upload selfie / medical document to AWS S3 Private
    - Store attendance metadata into AWS DynamoDB
    """
    try:
        siswa_id = request.form.get("siswa_id", "").strip()
        kelas_id = request.form.get("kelas_id", "").strip()
        status = request.form.get("status", "Present").strip()
        keterangan = request.form.get("keterangan", "").strip()

        if not siswa_id or not kelas_id:
            return jsonify({"success": False, "message": "Please select a class and student!"}), 400

        if status not in ["Present", "Excused", "Sick", "Hadir", "Izin", "Sakit"]:
            return jsonify({"success": False, "message": "Invalid attendance status!"}), 400

        # Normalize status string
        if status == "Hadir":
            status = "Present"
        elif status == "Izin":
            status = "Excused"
        elif status == "Sakit":
            status = "Sick"

        # Check uploaded photo/document
        if "foto" not in request.files:
            return jsonify({"success": False, "message": "Attendance selfie or proof document is required!"}), 400

        file = request.files["foto"]
        if file.filename == "":
            return jsonify({"success": False, "message": "Please choose or capture a photo!"}), 400

        if not is_allowed_image(file.filename):
            return jsonify({"success": False, "message": "Unsupported file format! Please upload JPG, PNG, or WEBP."}), 400

        # Retrieve student details from DynamoDB
        siswa_resp = table.get_item(Key={"id": siswa_id})
        siswa_item = siswa_resp.get("Item")
        if not siswa_item:
            return jsonify({"success": False, "message": "Student record not found!"}), 404

        nama_siswa = siswa_item.get("nama_siswa", "Student")
        nama_kelas = siswa_item.get("nama_kelas", "Class")
        nis = siswa_item.get("nis", "-")

        presensi_id = "ATT-" + uuid.uuid4().hex[:8].upper()
        clean_filename = secure_filename(file.filename)
        extension = clean_filename.rsplit(".", 1)[1].lower() if "." in clean_filename else "jpg"
        s3_key = f"attendance/{presensi_id}_{uuid.uuid4().hex[:4]}.{extension}"

        # Calculate file size
        file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        file.seek(0)
        formatted_size = format_size(size_bytes)

        # Detect content type
        content_type = mimetypes.guess_type(clean_filename)[0] or "image/jpeg"

        # Upload photo to AWS S3 Private
        s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": content_type,
                "ContentDisposition": f'inline; filename="{clean_filename}"'
            }
        )

        now = datetime.now()
        tanggal_str = now.strftime("%Y-%m-%d")
        waktu_str = now.strftime("%H:%M:%S")
        now_iso = datetime.utcnow().isoformat() + "Z"

        new_presensi = {
            "id": presensi_id,
            "tipe": "presensi",
            "siswa_id": siswa_id,
            "nama_siswa": nama_siswa,
            "nis": nis,
            "kelas_id": kelas_id,
            "nama_kelas": nama_kelas,
            "status": status,
            "tanggal": tanggal_str,
            "waktu": waktu_str,
            "keterangan": keterangan if keterangan else ("Present at TKJ Computer Lab" if status == "Present" else "-"),
            "file_name": clean_filename,
            "file_size": formatted_size,
            "s3_key": s3_key,
            "candidate_name": YOUR_NAME if YOUR_NAME else "UNSET",
            "created_at": now_iso
        }

        # Save record in DynamoDB
        table.put_item(Item=new_presensi)

        return jsonify({
            "success": True,
            "message": f"Attendance recorded for {nama_siswa}!",
            "data": decimal_to_native(new_presensi)
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/presensi/<presensi_id>/foto", methods=["GET"])
def view_foto_presensi(presensi_id):
    """
    Stream attendance selfie/proof directly from AWS S3 Private via Boto3.
    S3 Bucket remains 100% PRIVATE without exposing public URLs.
    """
    try:
        response = table.get_item(Key={"id": presensi_id})
        presensi = response.get("Item")
        if not presensi or not presensi.get("s3_key"):
            return jsonify({"error": "Attendance record or photo not found"}), 404

        s3_key = presensi["s3_key"]
        file_name = presensi.get("file_name", "attendance.jpg")

        s3_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        body = s3_obj["Body"].read()
        content_type = s3_obj.get("ContentType", "image/jpeg")

        as_attachment = request.args.get("download", "false").lower() == "true"

        return send_file(
            io.BytesIO(body),
            mimetype=content_type,
            as_attachment=as_attachment,
            download_name=file_name
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return jsonify({"error": "Photo not found in S3 bucket"}), 404
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/presensi/<presensi_id>", methods=["DELETE"])
def delete_presensi(presensi_id):
    """Delete attendance record from DynamoDB and remove corresponding object from S3"""
    try:
        response = table.get_item(Key={"id": presensi_id})
        presensi = response.get("Item")
        if not presensi:
            return jsonify({"success": False, "message": "Attendance record not found!"}), 404

        s3_key = presensi.get("s3_key")
        if s3_key:
            try:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            except Exception as s3_err:
                print(f"[Warning] Failed to delete S3 file {s3_key}: {s3_err}")

        table.delete_item(Key={"id": presensi_id})
        return jsonify({"success": True, "message": "Attendance record deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Retrieve statistical counters for classes, students, and daily attendance"""
    try:
        response = table.scan()
        items = response.get("Items", [])

        now_date = datetime.now().strftime("%Y-%m-%d")

        total_kelas = sum(1 for i in items if i.get("tipe") == "kelas")
        total_siswa = sum(1 for i in items if i.get("tipe") == "siswa")

        presensi_today = [
            i for i in items
            if i.get("tipe") == "presensi" and i.get("tanggal") == now_date
        ]

        total_presensi_today = len(presensi_today)
        hadir_today = sum(1 for i in presensi_today if i.get("status") in ["Present", "Hadir"])
        izin_today = sum(1 for i in presensi_today if i.get("status") in ["Excused", "Izin"])
        sakit_today = sum(1 for i in presensi_today if i.get("status") in ["Sick", "Sakit"])

        return jsonify({
            "success": True,
            "data": {
                "today": now_date,
                "total_kelas": total_kelas,
                "total_siswa": total_siswa,
                "presensi_hari_ini": total_presensi_today,
                "hadir_hari_ini": hadir_today,
                "izin_hari_ini": izin_today,
                "sakit_hari_ini": sakit_today
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# MAIN RUNNER
# ==============================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("==================================================")
    print("   SIMPRES TKJ - ONLINE STUDENT ATTENDANCE SYSTEM ")
    print("   AWS EC2 + DynamoDB (Table) + S3 (Selfie Photos)")
    print("==================================================")
    print(f"Candidate (YOUR_NAME) : {YOUR_NAME if YOUR_NAME else '*** NOT SET (ACTION REQUIRED) ***'}")
    print(f"Theme (STYLE)         : {STYLE}")
    print(f"Region                : {AWS_REGION}")
    print(f"DynamoDB Table        : {DYNAMODB_TABLE_NAME}")
    print(f"S3 Bucket             : {S3_BUCKET_NAME}")
    print(f"Port                  : {port}")
    print(f"URL                   : http://0.0.0.0:{port}")
    print("==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
