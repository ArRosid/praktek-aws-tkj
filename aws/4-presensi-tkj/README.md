# 📝 Hands-on Exam: Enterprise Cloud Infrastructure & Automated Deployment of SIMPRES TKJ
> **Practical Lab Assessment • AWS Cloud Computing & DevOps for Computer Network Engineering (TKJ)**  
> **Course / Subject:** Cloud Infrastructure, Network Architecture, Server Automation & Load Balancing  
> **Target Region:** AWS `us-east-1` (N. Virginia)  
> **Duration:** 120 - 150 Minutes

---

## 🎯 Exam Scenario & Objective

You are appointed as the **Cloud Infrastructure Architect** for SMK TKJ. The institution requires a scalable, fault-tolerant, and secure cloud deployment for **SIMPRES TKJ** (Online Student Attendance Management System). 

The application is written in Python (Flask) with the Boto3 SDK, interacting with:
1. **Amazon DynamoDB**: NoSQL database for managing classes, student identities, and daily attendance logs.
2. **Amazon S3**: Object storage for securely preserving attendance selfie photos and medical leave documents.

Your assignment is to design and provision the entire custom cloud networking layer (**Custom VPC with 3 Public Subnets across 3 Availability Zones**), establish database and storage resources, launch the server using an **automated EC2 User Data script** (without virtual environments and without systemd service units), and place the application behind an **AWS Application Load Balancer (ALB)** with a **Target Group**.

Manual SSH configuration is strictly prohibited for the final submission; the instance must bootstrap itself automatically.

---

## 🏗️ Target Infrastructure Architecture

```
                                  Internet Users / Students
                                              │
                                              ▼ HTTP Port 80
                                ┌───────────────────────────┐
                                │ Internet Gateway (IGW)    │
                                └─────────────┬─────────────┘
                                              │
                        ┌─────────────────────┴─────────────────────┐
                        │        Custom VPC: 10.0.0.0/16            │
                        │                                           │
                        │   ┌───────────────────────────────────┐   │
                        │   │  Application Load Balancer (ALB)  │   │
                        │   │  (Internet-facing, Port 80)       │   │
                        │   └─────┬───────────────┬─────────────┘   │
                        │         │               │                 │
    ┌─────────────────────────────┼───────────────┼─────────────────────────────┐
    │ Public Subnet A             │ Public Subnet B                 Public Subnet C
    │ (us-east-1a)                │ (us-east-1b)                    (us-east-1c)
    │ CIDR: 10.0.1.0/24           │ CIDR: 10.0.2.0/24               CIDR: 10.0.3.0/24
    │                             ▼                                 │
    │  ┌──────────────────────────────┐                             │
    │  │ Target Group (Port 5000)     │                             │
    │  │ └── EC2 Instance             │                             │
    │  │     ├── Bootstrapped via     │                             │
    │  │     │   User Data            │                             │
    │  │     ├── System Python 3      │                             │
    │  │     │   (No venv)            │                             │
    │  │     └── nohup Process        │                             │
    │  │              │               │                             │
    │  └──────────────┼───────────────┘                             │
    └─────────────────┼─────────────────────────────────────────────┘
                      │ IAM Role (LabInstanceProfile)
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
[ Amazon DynamoDB ]       [ Amazon S3 (Private) ]
Table: tkj_presensi       Bucket: tkj-presensi-siswa-<your-name>
(CRUD Metadata)           (Selfie Photos - 100% Private)
```

---

## 📋 Exam Tasks & Requirements

### Task 1: Provision Custom VPC & 3 Public Subnets
You must design a custom networking foundation. **Do NOT use the default VPC**.
- **Virtual Private Cloud (VPC)**:
  - Name: `vpc-simpres-tkj`
  - IPv4 CIDR Block: `10.0.0.0/16`
- **Subnet Configuration (Only Public Subnets, No Private Subnets)**:
  - Create exactly **3 Public Subnets** distributed across **3 Availability Zones** in the `us-east-1` region:
    1. **Public Subnet 1**: Name `subnet-simpres-public-a`, Availability Zone `us-east-1a`, IPv4 CIDR `10.0.1.0/24`.
    2. **Public Subnet 2**: Name `subnet-simpres-public-b`, Availability Zone `us-east-1b`, IPv4 CIDR `10.0.2.0/24`.
    3. **Public Subnet 3**: Name `subnet-simpres-public-c`, Availability Zone `us-east-1c`, IPv4 CIDR `10.0.3.0/24`.
  - **Auto-assign Public IPv4**: Enable **Auto-assign public IPv4 address** on all 3 subnets.
- **Internet Gateway & Routing**:
  - Create an Internet Gateway named `igw-simpres-tkj` and attach it to `vpc-simpres-tkj`.
  - Create a Route Table named `rt-simpres-public`.
  - Add a route: Destination `0.0.0.0/0` targeting `igw-simpres-tkj`.
  - Associate all 3 public subnets to `rt-simpres-public`.

---

### Task 2: Provision NoSQL Database (Amazon DynamoDB)
- Create an Amazon DynamoDB table with the name: `tkj_presensi`.
- **Partition Key**: `id` with data type **String (`S`)**.
- Table settings: Default settings (Free tier On-Demand or Provisioned capacity).
- Ensure the table reaches **Active** status.

---

### Task 3: Provision Private Object Storage (Amazon S3)
- Create an Amazon S3 bucket with a globally unique name: `tkj-presensi-siswa-<your-student-id>`.
- Region: `us-east-1`.
- **Security Constraint (Strict)**: Keep **Block *all* public access** fully **ENABLED (ON)**.
- You must **NOT** create public bucket policies or public ACLs. The Flask backend uses Boto3 server-side streaming to serve photos directly and securely to authenticated clients.

---

### Task 4: IAM Role Configuration for EC2
- The EC2 instance must interact with DynamoDB and S3 without hardcoded AWS Access Keys.
- If using **AWS Academy Learner Lab**: Select the pre-configured IAM role `LabInstanceProfile`.
- If using a standard AWS account: Attach an IAM Role with `AmazonDynamoDBFullAccess` and `AmazonS3FullAccess` policies.

---

### Task 5: Launch & Bootstrap EC2 via User Data
- Launch an EC2 instance (`Ubuntu 22.04 LTS` or `Ubuntu 24.04 LTS`, `t2.micro` or `t3.micro`).
- **Placement**: Place the instance inside `vpc-simpres-tkj`, within **Public Subnet 1 (`us-east-1a`)**.
- **Security Group (EC2)**:
  - Name: `simpres-ec2-sg`
  - Allow Port `22` (SSH) from `My IP` or `0.0.0.0/0`.
  - Allow Port `5000` (Custom TCP) for application access.
- **IAM Profile**: Select `LabInstanceProfile`.
- **User Data Script Requirements**:
  You must supply a Bash script (`#!/bin/bash`) in **Advanced details > User data** that autonomously executes:
  1. System package update and installation of prerequisites (`python3-pip`, `git`).
  2. Cloning of the repository into `/home/ubuntu/praktek-aws-tkj` (or appropriate project directory).
  3. Direct system-wide installation of Python dependencies from `requirements.txt` using `pip3` (with `--break-system-packages` on Ubuntu 24.04).
  4. Generating the production `.env` configuration file containing the correct AWS region, table name, bucket name, and application port.
  5. Starting the application directly in the background:
     ```bash
     nohup python3 /home/ubuntu/praktek-aws-tkj/4-presensi-tkj/app.py > /var/log/simpres.log 2>&1 &
     ```

---

### Task 6: Configure Target Group & Application Load Balancer
To achieve high availability and production-grade routing, expose the application through an AWS Application Load Balancer:

1. **Target Group**:
   - Target type: **Instances**.
   - Target group name: `tg-simpres-5000`.
   - Protocol: `HTTP`, Port: `5000`.
   - VPC: Select `vpc-simpres-tkj`.
   - **Health check settings (Critical Requirement)**:
     - Protocol: `HTTP`
     - Health check path: `/health`
     > [!WARNING]
     > **Do NOT leave the health check path at default (`/`)**. The root endpoint `/` returns **HTTP 202 Accepted**, which does not match the Target Group default expected code (`200`). If you do not configure `/health`, your target will fail health checks (**Unhealthy: [202]**) and the Load Balancer will not route traffic!
   - Register your EC2 instance on Port `5000` as a pending target.
2. **Security Group for Load Balancer**:
   - Name: `simpres-alb-sg`
   - Inbound Rule: Allow **HTTP (Port 80)** from `0.0.0.0/0` (Anywhere).
3. **Application Load Balancer (ALB)**:
   - Name: `alb-simpres-tkj`
   - Scheme: **Internet-facing**, IP address type: **IPv4**.
   - Network mapping:
     - VPC: `vpc-simpres-tkj`.
     - Mappings: Select **all 3 Public Subnets** across **`us-east-1a`**, **`us-east-1b`**, and **`us-east-1c`**.
   - Security groups: Attach `simpres-alb-sg`.
   - Listeners and routing:
     - Listener: Protocol `HTTP`, Port `80`.
     - Default action: Forward to Target Group `tg-simpres-5000`.
4. Verify that the target status in Target Group transitions from *Initial* to **Healthy**.

---

## 💡 Engineering Tips: Understanding `echo >` vs `echo >>` in Shell Scripts

When creating files via shell commands in automated scripts, pay close attention to the difference between the single redirection operator (`>`) and double redirection operator (`>>`):

### 1. Single Redirection Operator (`>`) — Overwrite / Create
The `>` operator redirects output to a file. If the file does not exist, it creates it. If the file already exists, it **completely erases (overwrites/truncates) any existing content** before writing:

```bash
# Write line 1 into test.txt
echo "First Line" > test.txt

# Overwrite test.txt with line 2
echo "Second Line" > test.txt

# Inspect the file content using cat:
cat test.txt
```
**Expected `cat` output:**
```text
Second Line
```
*(Notice that "First Line" was completely erased because `>` overwrites the file!)*

---

### 2. Double Redirection Operator (`>>`) — Append
The `>>` operator appends new data to the **end of an existing file**, preserving all lines that were written previously:

```bash
# Append line 3 and line 4 to test.txt
echo "Third Line" >> test.txt
echo "Fourth Line" >> test.txt

# Inspect the file content again using cat:
cat test.txt
```
**Expected `cat` output:**
```text
Second Line
Third Line
Fourth Line
```
*(Both lines were added at the bottom without deleting any existing content!)*

---

### 3. System-Wide Package Installation (No venv)
Since this exam prohibits virtual environments (`venv`), packages are installed directly into the global Python environment. On modern Ubuntu versions (such as Ubuntu 24.04 LTS), PEP 668 protects system packages. To install `requirements.txt` globally via User Data, append the `--break-system-packages` flag:
```bash
pip3 install -r /home/ubuntu/praktek-aws-tkj/4-presensi-tkj/requirements.txt --break-system-packages
```

---

## 📊 Assessment & Verification Checklist

| Component | Assessment & Delivery Criteria | Deliverable Status |
| :--- | :--- | :---: |
| **Custom VPC & 3 Public Subnets** | Custom VPC (`10.0.0.0/16`), 3 public subnets in AZ a, b, c with IGW and public route table. No private subnets. Auto-assign public IP enabled. | Required |
| **DynamoDB Configuration** | Table `tkj_presensi` created with Partition Key `id` (`String`). Status is Active. | Required |
| **S3 Private Storage** | S3 bucket created with **Block All Public Access enabled**. No public policies. | Required |
| **IAM Authorization** | EC2 role attached; application communicates with AWS SDK without static credentials. | Required |
| **Automated User Data** | EC2 bootstrapped in custom VPC via User Data without manual SSH commands, no venv, no systemd. | Required |
| **ALB & Target Group** | Application Load Balancer spanning the 3 public subnets, Port 80 listener forwarding to Target Group with custom `/health` check (Healthy). | Required |

---

## 🔍 Verification & Acceptance Testing

The evaluator will test your deployed infrastructure using the following checklist:

1. **Load Balancer Access**:
   - Copy the **DNS name** of your Application Load Balancer (e.g., `http://alb-simpres-tkj-123456789.us-east-1.elb.amazonaws.com`).
   - Open the URL in a browser on standard **HTTP Port 80** (no need to specify `:5000`).
   - The SIMPRES TKJ portal must load smoothly.
2. **Target Group Custom Health Check Verification**:
   - In AWS EC2 Console > **Target Groups** > `tg-simpres-5000` > **Health checks**, verify that the Health check path is `/health` (NOT default `/`).
   - The registered EC2 target status must be **Healthy**. (Targets configured with default `/` will fail with code `202`).
3. **Data Master Insertion**:
   - Open **Manage Classes & Students** tab.
   - Create class `12 TKJ 1`.
   - Register student `Alex Pratama` (NIS: `2026001`).
4. **Attendance Submission**:
   - Open **Record Attendance** tab.
   - Select `12 TKJ 1` and student `Alex Pratama`.
   - Choose status **Present**, capture a selfie or upload a photo, and submit.
5. **Storage & Database Verification**:
   - Verify that the photo appears in the **Attendance Logs** table and opens in full-resolution modal preview.
   - Verify that the S3 bucket contains the photo under `attendance/` folder and remains 100% private.
   - Verify in AWS DynamoDB Console that the attendance record exists.

---

**Good luck with your practical examination! Build robust, scalable, and automated cloud systems.**
