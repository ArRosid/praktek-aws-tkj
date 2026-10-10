# Python Troubleshooting Exam Set (Selection 2028)

**Total Questions:** 13 Questions | **Total Time:** 75 Minutes | **Total Score:** 100 Points  

### General Instructions:
1. **Automated Marking System:** Grading will be performed automatically by a marking script that strictly compares standard output (`stdout`). Do not alter the expected print labels or formatting.
2. **File Creation:** For each question, create a separate Python file named exactly as specified (`question_01.py` through `question_13.py`).
3. **Copy & Fix:** Copy the provided code snippet into your target file, fix the bug so the program runs without errors, and ensure the terminal output matches the **Expected Output** exactly.
4. **Final Submission:** When finished, compress all 13 Python files into a single `.zip` file named `python_exam_<Your_Full_Name>.zip` and submit it via the designated **Google Form**.

---

### Questions Summary Table

| No | Target File | Topic & Focus | Difficulty | Est. Time | Points |
|:---:|:---|:---|:---:|:---:|:---:|
| 1 | `question_01.py` | Data Types & Arithmetic Conversion | Easy | 3 Mins | 5 |
| 2 | `question_02.py` | Conditional Logic Inversion | Easy | 3 Mins | 5 |
| 3 | `question_03.py` | Infinite Loop Control Flow | Easy | 4 Mins | 5 |
| 4 | `question_04.py` | 1D List Indexing & Range Boundary | Easy | 4 Mins | 5 |
| 5 | `question_05.py` | 2D List (Matrix) Element Access | Medium | 5 Mins | 7 |
| 6 | `question_06.py` | Nested List Iteration & Indexing | Medium | 5 Mins | 7 |
| 7 | `question_07.py` | Nested Dictionary Chained Access | Medium | 5 Mins | 7 |
| 8 | `question_08.py` | Dictionary containing a List | Medium | 5 Mins | 7 |
| 9 | `question_09.py` | List containing Dictionaries | Medium | 5 Mins | 7 |
| 10 | `question_10.py` | Iterating List of Nested Dictionaries | Medium–Hard | 6 Mins | 10 |
| 11 | `question_11.py` | Dictionary Unpacking & Counter Logic | Medium–Hard | 6 Mins | 10 |
| 12 | `question_12.py` | Safe Nested Dict Access & Fallbacks (`.get()`) | Medium–Hard | 6 Mins | 10 |
| 13 | `question_13.py` | Multi-Level Traversal (Dict -> Dict -> List -> Dict) | Hard | 8 Mins | 15 |
| **Total** | | **13 Questions** | | **70 Mins** | **100 Pts** |

---

## Level 1: Foundations & Flow Control (Questions 01 – 04)

### Question 01 — Data Types & Arithmetic Conversion
- **Target File:** `question_01.py`  
- **Difficulty:** Easy  
- **Points:** 5 Points  

**Code Snippet:**
```python
price = "15000"
quantity = "3"

total = price * quantity

print("Total payment:", total)
```

**Issue:** `price` and `quantity` are strings. Multiplying them causes a `TypeError` instead of performing arithmetic multiplication.

**Candidate Tasks:**
1. Create a new file named `question_01.py` and copy the code snippet above into it.
2. Fix the code so it performs numeric multiplication.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Total payment: 45000
```

---

### Question 02 — Conditional Logic Inversion
- **Target File:** `question_02.py`  
- **Difficulty:** Easy  
- **Points:** 5 Points  

**Code Snippet:**
```python
score = 80

if score >= 75:
    print("Status: Failed")
else:
    print("Status: Passed")
```

**Issue:** The branching logic is inverted; an exam score of 80 is wrongly marked as `Failed`.

**Candidate Tasks:**
1. Create a new file named `question_02.py` and copy the code snippet above into it.
2. Fix the conditional logic so that scores `>= 75` produce `Status: Passed`.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Status: Passed
```

---

### Question 03 — Infinite Loop Control Flow
- **Target File:** `question_03.py`  
- **Difficulty:** Easy  
- **Points:** 5 Points  

**Code Snippet:**
```python
number = 1

while number <= 5:
    print(number)
```

**Issue:** The variable `number` is never incremented, creating an infinite loop that repeatedly prints `1`.

**Candidate Tasks:**
1. Create a new file named `question_03.py` and copy the code snippet above into it.
2. Fix the loop so that it increments and prints numbers from 1 to 5, then terminates.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
1
2
3
4
5
```

---

### Question 04 — 1D List Indexing & Range Boundary
- **Target File:** `question_04.py`  
- **Difficulty:** Easy  
- **Points:** 5 Points  

**Code Snippet:**
```python
devices = ["Router", "Switch", "Server"]

def show_devices():
    for i in range(1, len(devices)):
        print(devices[i])

show_devices()
```

**Issue:** The loop begins at index `1`, causing the first item (`"Router"`) to be skipped.

**Candidate Tasks:**
1. Create a new file named `question_04.py` and copy the code snippet above into it.
2. Fix the index range so that all three devices are printed.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Router
Switch
Server
```

---

## Level 2: Nested Data Structures Access (Questions 05 – 09)

### Question 05 — 2D List (Matrix) Element Access
- **Target File:** `question_05.py`  
- **Difficulty:** Medium  
- **Points:** 7 Points  

**Code Snippet:**
```python
# Server rack layout: 3 rows, 3 columns
rack = [
    ["Server-A1", "Server-A2", "Server-A3"],
    ["Server-B1", "Server-B2", "Server-B3"],
    ["Server-C1", "Server-C2", "Server-C3"]
]

# Intended: Access Server-B3 (Row index 1, Column index 2)
target_server = rack[1, 2]

print("Target Server:", target_server)
```

**Issue:** The syntax `rack[1, 2]` causes a `TypeError: list indices must be integers or slices, not tuple`.

**Candidate Tasks:**
1. Create a new file named `question_05.py` and copy the code snippet above into it.
2. Correct the 2D list indexing syntax to access `Server-B3`.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Target Server: Server-B3
```

---

### Question 06 — Nested List Iteration & Indexing
- **Target File:** `question_06.py`  
- **Difficulty:** Medium  
- **Points:** 7 Points  

**Code Snippet:**
```python
# Subnet IP ranges: [Primary IP, Secondary IP]
subnets = [
    ["192.168.1.1", "192.168.1.2"],
    ["10.0.0.1", "10.0.0.2"],
    ["172.16.0.1", "172.16.0.2"]
]

# Intended: Print the Primary IP (the first item in each sub-list)
for net in subnets:
    print("Primary IP:", net[1])
```

**Issue:** The loop accesses index `1` instead of index `0`, printing secondary IPs instead of primary IPs.

**Candidate Tasks:**
1. Create a new file named `question_06.py` and copy the code snippet above into it.
2. Fix the index access so that the first element of each inner list is printed.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Primary IP: 192.168.1.1
Primary IP: 10.0.0.1
Primary IP: 172.16.0.1
```

---

### Question 07 — Nested Dictionary Chained Access
- **Target File:** `question_07.py`  
- **Difficulty:** Medium  
- **Points:** 7 Points  

**Code Snippet:**
```python
server = {
    "hostname": "web-srv-01",
    "specs": {
        "cpu": "8 Cores",
        "ram": "16 GB",
        "storage": "500 GB SSD"
    }
}

# Intended: Retrieve the RAM capacity ("16 GB")
ram_info = server["ram"]

print("Server RAM:", ram_info)
```

**Issue:** Accessing `server["ram"]` raises a `KeyError: 'ram'` because `"ram"` is nested inside the `"specs"` dictionary.

**Candidate Tasks:**
1. Create a new file named `question_07.py` and copy the code snippet above into it.
2. Fix the nested dictionary access path to correctly obtain the RAM specification.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Server RAM: 16 GB
```

---

### Question 08 — Dictionary containing a List
- **Target File:** `question_08.py`  
- **Difficulty:** Medium  
- **Points:** 7 Points  

**Code Snippet:**
```python
router = {
    "name": "Core-Router",
    "allowed_ports": [22, 80, 443, 8080]
}

# Intended: Access the SSL port 443 (the 3rd element in allowed_ports)
ssl_port = router["allowed_ports"]["443"]

print("SSL Port:", ssl_port)
```

**Issue:** Using a string key `["443"]` on a list causes a `TypeError: list indices must be integers or slices, not str`.

**Candidate Tasks:**
1. Create a new file named `question_08.py` and copy the code snippet above into it.
2. Fix the expression to correctly access port `443` from the list inside the dictionary.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
SSL Port: 443
```

---

### Question 09 — List containing Dictionaries
- **Target File:** `question_09.py`  
- **Difficulty:** Medium  
- **Points:** 7 Points  

**Code Snippet:**
```python
vms = [
    {"name": "Web-Server", "ip": "192.168.1.10", "status": "running"},
    {"name": "Database", "ip": "192.168.1.20", "status": "stopped"},
    {"name": "Backup", "ip": "192.168.1.30", "status": "running"}
]

# Intended: Retrieve the IP address of the Database server (the 2nd item in the list)
db_ip = vms["Database"]["ip"]

print("Database IP:", db_ip)
```

**Issue:** Accessing `vms["Database"]` causes a `TypeError: list indices must be integers or slices, not str` because `vms` is a list, not a dictionary.

**Candidate Tasks:**
1. Create a new file named `question_09.py` and copy the code snippet above into it.
2. Fix the syntax to select the second dictionary by its list index and then access its `"ip"` key.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Database IP: 192.168.1.20
```

---

## Level 3: Iteration & Safe Dictionary Lookups (Questions 10 – 12)

### Question 10 — Iterating List of Nested Dictionaries
- **Target File:** `question_10.py`  
- **Difficulty:** Medium–Hard  
- **Points:** 10 Points  

**Code Snippet:**
```python
devices = [
    {"hostname": "Router-HQ", "details": {"vendor": "Cisco", "os": "IOS-XE"}},
    {"hostname": "Switch-Floor1", "details": {"vendor": "Juniper", "os": "Junos"}},
    {"hostname": "AP-Lobby", "details": {"vendor": "MikroTik", "os": "RouterOS"}}
]

for dev in devices:
    # Intended output: "<hostname> runs on <os>"
    os_name = dev["os"]
    print(f"{dev['hostname']} runs on {os_name}")
```

**Issue:** Accessing `dev["os"]` raises a `KeyError: 'os'` because `"os"` is located inside the nested `"details"` dictionary.

**Candidate Tasks:**
1. Create a new file named `question_10.py` and copy the code snippet above into it.
2. Fix the dictionary lookup inside the loop to properly extract `"os"` from `"details"`.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Router-HQ runs on IOS-XE
Switch-Floor1 runs on Junos
AP-Lobby runs on RouterOS
```

---

### Question 11 — Dictionary Unpacking & Counter Logic
- **Target File:** `question_11.py`  
- **Difficulty:** Medium–Hard  
- **Points:** 10 Points  

**Code Snippet:**
```python
devices = {
    "Router": "Active",
    "Switch": "Inactive",
    "Server": "Active",
    "Access Point": "Inactive"
}

active = 0
inactive = 0

for name, status in devices:
    if status == "Active":
        inactive += 1
    else:
        active += 1

total = len(devices)
percentage = (active / total) * 100

print("Active devices:", active)
print("Inactive devices:", inactive)
print(f"Active percentage: {percentage:.1f}%")
```

**Issue:** Iterating `for name, status in devices:` raises `ValueError: not enough values to unpack (expected 2, got 1)`, and the accumulation logic for `active` and `inactive` is inverted.

**Candidate Tasks:**
1. Create a new file named `question_11.py` and copy the code snippet above into it.
2. Fix the dictionary iteration using `.items()` so both keys and values are unpacked properly.
3. Correct the counter accumulation so active devices are added to `active` and inactive devices to `inactive`.
4. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Active devices: 2
Inactive devices: 2
Active percentage: 50.0%
```

---

### Question 12 — Safe Nested Dict Access & Fallbacks (`.get()`)
- **Target File:** `question_12.py`  
- **Difficulty:** Medium–Hard  
- **Points:** 10 Points  

**Code Snippet:**
```python
server_config = {
    "hostname": "srv-app-01",
    "ip_address": "192.168.10.25",
    "services": {
        "ssh": 22,
        "http": 80
    }
}

# Retrieve server configurations and ports
print("Hostname   :", server_config["hostname"])
print("Port SSH   :", server_config["services"]["ssh"])
print("Port HTTPS :", server_config["services"]["https"])
print("Gateway    :", server_config["gateway"])
```

**Issue:** Accessing non-existent keys `"https"` and `"gateway"` crashes the program with a `KeyError: 'https'`.

**Candidate Tasks:**
1. Create a new file named `question_12.py` and copy the code snippet above into it.
2. Modify how keys are accessed using `.get()` so the script handles missing keys gracefully.
3. Provide a fallback default value of `443` if the `https` port is absent, and `"192.168.10.1"` if `gateway` is missing.
4. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Hostname   : srv-app-01
Port SSH   : 22
Port HTTPS : 443
Gateway    : 192.168.10.1
```

---

## Level 4: Complex Multi-Level Traversal (Question 13)

### Question 13 — Multi-Level Traversal (Dict -> Dict -> List -> Dict)
- **Target File:** `question_13.py`  
- **Difficulty:** Hard  
- **Points:** 15 Points  

**Code Snippet:**
```python
network_config = {
    "datacenter": "DC-Jakarta",
    "network": {
        "vlans": [
            {"id": 10, "name": "Management"},
            {"id": 20, "name": "Production"},
            {"id": 30, "name": "Guest"}
        ]
    }
}

# Intended: Retrieve the name of VLAN 20 ("Production", at index 1 of the vlans list)
vlan_name = network_config["network"]["vlans"]["Production"]

print("Target VLAN:", vlan_name)
```

**Issue:** Attempting to access `vlans["Production"]` causes a `TypeError` because `"vlans"` is a list of dictionaries, not a dictionary.

**Candidate Tasks:**
1. Create a new file named `question_13.py` and copy the code snippet above into it.
2. Correctly navigate the multi-tier data structure: access the `"network"` dict, then the `"vlans"` list at index `1`, then retrieve the `"name"` key.
3. Ensure the program produces the exact expected output below.

**Expected Output:**
```text
Target VLAN: Production
```

---

## Submission Guidelines

Before the test time ends:
1. Ensure you have all 13 Python files ready in your working folder:
   - `question_01.py`
   - `question_02.py`
   - `question_03.py`
   - `question_04.py`
   - `question_05.py`
   - `question_06.py`
   - `question_07.py`
   - `question_08.py`
   - `question_09.py`
   - `question_10.py`
   - `question_11.py`
   - `question_12.py`
   - `question_13.py`
2. Compress all 13 files into a single `.zip` file using the naming format:  
   `python_exam_<Your_Full_Name>.zip`
3. Upload and submit the `.zip` file via the designated **Google Form link** before the exam deadline.
