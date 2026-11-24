import os
import sys
import time
import socket
import json
import sqlite3
import threading
from datetime import datetime

# Check for Flask, provide a friendly message if missing
try:
    from flask import Flask, request, jsonify, render_template_string, redirect, url_for
except ImportError:
    print("Flask is required to run the Student Management System.")
    print("Please install requirements: pip install -r requirements.txt")
    print("Or run using Docker: docker-compose up --build")
    sys.exit(1)

# Check for PostgreSQL driver (optional, falls back to SQLite)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

app = Flask(__name__)
START_TIME = time.time()
REQUEST_COUNT = 0
HOSTNAME = socket.gethostname()
try:
    HOST_IP = socket.gethostbyname(HOSTNAME)
except Exception:
    HOST_IP = "127.0.0.1"

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "student_db")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres123")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

USE_POSTGRES = bool(DATABASE_URL or POSTGRES_HOST) and POSTGRES_AVAILABLE
SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "students.db")


def get_db_connection():
    """Establishes database connection based on environment (Postgres or SQLite fallback)."""
    if USE_POSTGRES:
        try:
            if DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
            else:
                conn = psycopg2.connect(
                    host=POSTGRES_HOST,
                    database=POSTGRES_DB,
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD,
                    port=POSTGRES_PORT,
                    connect_timeout=3
                )
            return conn, "PostgreSQL"
        except Exception as e:
            # Fall back to SQLite if PostgreSQL connection fails
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn, f"SQLite (Fallback - Postgres Error: {str(e)[:30]})"
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "SQLite"


def init_db():
    """Initializes tables and seeds initial data if empty."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    if "PostgreSQL" in db_type:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                department VARCHAR(100) NOT NULL,
                gpa NUMERIC(3, 2) NOT NULL,
                enrollment_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM students;")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_students = [
                ('STU101', 'Alex Johnson', 'alex.j@university.edu', 'Computer Science', 3.85, '2023-09-01'),
                ('STU102', 'Samantha Rivera', 's.rivera@university.edu', 'Information Technology', 3.92, '2023-09-01'),
                ('STU103', 'Liam Chen', 'liam.chen@university.edu', 'Data Science', 3.70, '2024-01-15'),
                ('STU104', 'Emily Davis', 'emily.d@university.edu', 'Cloud Computing', 3.98, '2023-09-01'),
                ('STU105', 'Marcus Taylor', 'm.taylor@university.edu', 'Cybersecurity', 3.65, '2024-01-15')
            ]
            for stu in sample_students:
                cursor.execute("""
                    INSERT INTO students (student_id, name, email, department, gpa, enrollment_date)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, stu)
            conn.commit()
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                gpa REAL NOT NULL,
                enrollment_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM students;")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_students = [
                ('STU101', 'Alex Johnson', 'alex.j@university.edu', 'Computer Science', 3.85, '2023-09-01'),
                ('STU102', 'Samantha Rivera', 's.rivera@university.edu', 'Information Technology', 3.92, '2023-09-01'),
                ('STU103', 'Liam Chen', 'liam.chen@university.edu', 'Data Science', 3.70, '2024-01-15'),
                ('STU104', 'Emily Davis', 'emily.d@university.edu', 'Cloud Computing', 3.98, '2023-09-01'),
                ('STU105', 'Marcus Taylor', 'm.taylor@university.edu', 'Cybersecurity', 3.65, '2024-01-15')
            ]
            for stu in sample_students:
                cursor.execute("""
                    INSERT INTO students (student_id, name, email, department, gpa, enrollment_date)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, stu)
            conn.commit()

    cursor.close()
    conn.close()


@app.before_request
def count_requests():
    global REQUEST_COUNT
    REQUEST_COUNT += 1


# ==========================================
# Frontend Dashboard (HTML UI)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud-Based Student Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            --cloud-card: #f8fafc;
        }
        body {
            background-color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        .navbar-brand {
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .cloud-badge {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 8px;
            padding: 6px 14px;
            font-size: 0.85rem;
        }
        .stat-card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        }
        .table-card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            overflow: hidden;
        }
        .table thead {
            background-color: #0f172a;
            color: #ffffff;
        }
        .badge-dept {
            font-size: 0.8rem;
            padding: 5px 10px;
            border-radius: 6px;
        }
    </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark py-3 shadow-sm">
    <div class="container-fluid px-4">
        <a class="navbar-brand d-flex align-items-center" href="/">
            <i class="bi bi-cloud-check-fill text-primary me-2 fs-3"></i>
            <span>Cloud Student Management System</span>
        </a>
        <div class="d-flex align-items-center gap-3">
            <div class="cloud-badge text-light">
                <i class="bi bi-hdd-network me-1 text-info"></i>
                <strong>Pod / Host:</strong> <span class="text-warning font-monospace">{{ hostname }}</span>
            </div>
            <div class="cloud-badge text-light">
                <i class="bi bi-database me-1 text-success"></i>
                <strong>DB:</strong> <span class="text-info">{{ db_type }}</span>
            </div>
            <a href="/health" target="_blank" class="btn btn-sm btn-outline-success">
                <i class="bi bi-heart-pulse-fill me-1"></i> Health Check
            </a>
            <a href="/metrics" target="_blank" class="btn btn-sm btn-outline-info">
                <i class="bi bi-bar-chart-fill me-1"></i> Metrics
            </a>
        </div>
    </div>
</nav>

<div class="container-fluid px-4 py-4">

    <!-- KPI Statistics -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card stat-card bg-white p-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="text-muted small text-uppercase fw-semibold">Total Students</div>
                        <h2 class="mb-0 fw-bold text-primary">{{ stats.total }}</h2>
                    </div>
                    <div class="bg-primary bg-opacity-10 p-3 rounded-circle text-primary fs-3">
                        <i class="bi bi-people-fill"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stat-card bg-white p-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="text-muted small text-uppercase fw-semibold">Departments</div>
                        <h2 class="mb-0 fw-bold text-success">{{ stats.departments }}</h2>
                    </div>
                    <div class="bg-success bg-opacity-10 p-3 rounded-circle text-success fs-3">
                        <i class="bi bi-building"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stat-card bg-white p-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="text-muted small text-uppercase fw-semibold">Average GPA</div>
                        <h2 class="mb-0 fw-bold text-warning">{{ "%.2f"|format(stats.avg_gpa) }}</h2>
                    </div>
                    <div class="bg-warning bg-opacity-10 p-3 rounded-circle text-warning fs-3">
                        <i class="bi bi-mortarboard-fill"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stat-card bg-white p-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="text-muted small text-uppercase fw-semibold">HPA CPU Stress Test</div>
                        <button class="btn btn-sm btn-danger mt-1" onclick="triggerLoad()">
                            <i class="bi bi-fire me-1"></i> Simulate High CPU
                        </button>
                    </div>
                    <div class="bg-danger bg-opacity-10 p-3 rounded-circle text-danger fs-3">
                        <i class="bi bi-cpu-fill"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Student Records Table & Management -->
    <div class="card table-card bg-white">
        <div class="card-header bg-white py-3 border-0 d-flex flex-wrap justify-content-between align-items-center gap-2">
            <h5 class="mb-0 fw-bold text-dark"><i class="bi bi-table me-2 text-primary"></i>Student Directory</h5>
            <div class="d-flex gap-2">
                <input type="text" id="searchInput" class="form-control form-control-sm" placeholder="Search by name, ID or dept..." onkeyup="filterTable()">
                <button class="btn btn-sm btn-primary d-flex align-items-center gap-1" data-bs-toggle="modal" data-bs-target="#addStudentModal">
                    <i class="bi bi-plus-circle"></i> Add Student
                </button>
            </div>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0" id="studentsTable">
                <thead>
                    <tr>
                        <th class="ps-3">Student ID</th>
                        <th>Full Name</th>
                        <th>Email Address</th>
                        <th>Department</th>
                        <th>GPA</th>
                        <th>Enrollment Date</th>
                        <th class="text-end pe-3">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td class="ps-3 fw-bold font-monospace text-primary">{{ student['student_id'] }}</td>
                        <td class="fw-semibold">{{ student['name'] }}</td>
                        <td class="text-muted small">{{ student['email'] }}</td>
                        <td>
                            <span class="badge bg-secondary badge-dept">{{ student['department'] }}</span>
                        </td>
                        <td>
                            <span class="badge {% if student['gpa'] >= 3.8 %}bg-success{% elif student['gpa'] >= 3.5 %}bg-info{% else %}bg-warning{% endif %}">
                                {{ "%.2f"|format(student['gpa']) }}
                            </span>
                        </td>
                        <td class="text-muted small">{{ student['enrollment_date'] }}</td>
                        <td class="text-end pe-3">
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteStudent('{{ student['student_id'] }}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="7" class="text-center py-4 text-muted">No student records found.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Cloud Architecture & HPA Info Footer -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="alert alert-primary d-flex align-items-center justify-content-between" role="alert">
                <div>
                    <i class="bi bi-info-circle-fill me-2 fs-5"></i>
                    <strong>Cloud Native Architecture Active:</strong> Kubernetes Deployment with 2+ Replicas, Horizontal Pod Autoscaler (HPA), Health Probes, and Failover Ready.
                </div>
                <span class="badge bg-dark font-monospace">Container IP: {{ host_ip }}</span>
            </div>
        </div>
    </div>

</div>

<!-- Add Student Modal -->
<div class="modal fade" id="addStudentModal" tabindex="-1" aria-labelledby="addStudentModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title" id="addStudentModalLabel"><i class="bi bi-person-plus-fill me-2"></i>Enroll New Student</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form id="addStudentForm" onsubmit="submitStudent(event)">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Student ID</label>
                        <input type="text" class="form-control" id="m_student_id" required placeholder="e.g. STU106">
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Full Name</label>
                        <input type="text" class="form-control" id="m_name" required placeholder="e.g. Jordan Smith">
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Email</label>
                        <input type="email" class="form-control" id="m_email" required placeholder="e.g. j.smith@university.edu">
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Department</label>
                        <select class="form-select" id="m_dept" required>
                            <option value="Computer Science">Computer Science</option>
                            <option value="Cloud Computing">Cloud Computing</option>
                            <option value="Data Science">Data Science</option>
                            <option value="Information Technology">Information Technology</option>
                            <option value="Cybersecurity">Cybersecurity</option>
                            <option value="Software Engineering">Software Engineering</option>
                        </select>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label fw-semibold">GPA</label>
                            <input type="number" step="0.01" min="0" max="4.0" class="form-control" id="m_gpa" required placeholder="3.85">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label fw-semibold">Enrollment Date</label>
                            <input type="date" class="form-control" id="m_date" required>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Enroll Student</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    document.getElementById('m_date').value = new Date().toISOString().split('T')[0];

    function filterTable() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        const rows = document.querySelectorAll('#studentsTable tbody tr');
        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    }

    async function submitStudent(e) {
        e.preventDefault();
        const data = {
            student_id: document.getElementById('m_student_id').value,
            name: document.getElementById('m_name').value,
            email: document.getElementById('m_email').value,
            department: document.getElementById('m_dept').value,
            gpa: parseFloat(document.getElementById('m_gpa').value),
            enrollment_date: document.getElementById('m_date').value
        };

        const res = await fetch('/api/students', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            window.location.reload();
        } else {
            const err = await res.json();
            alert('Error adding student: ' + (err.error || 'Unknown error'));
        }
    }

    async function deleteStudent(studentId) {
        if (!confirm(`Are you sure you want to delete student ${studentId}?`)) return;
        const res = await fetch(`/api/students/${studentId}`, { method: 'DELETE' });
        if (res.ok) {
            window.location.reload();
        } else {
            alert('Error deleting student.');
        }
    }

    async function triggerLoad() {
        alert('Simulating high CPU load for 10 seconds to trigger HPA autoscaling...');
        fetch('/api/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ duration: 10 })
        });
    }
</script>
</body>
</html>
"""


# ==========================================
# Web & API Endpoints
# ==========================================

@app.route("/")
def index():
    """Renders student directory dashboard."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    if "PostgreSQL" in db_type:
        cursor.execute("SELECT student_id, name, email, department, gpa, enrollment_date FROM students ORDER BY id DESC;")
        columns = [desc[0] for desc in cursor.description]
        students = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT department), AVG(gpa) FROM students;")
        row = cursor.fetchone()
        stats = {
            "total": row[0] or 0,
            "departments": row[1] or 0,
            "avg_gpa": float(row[2]) if row[2] else 0.0
        }
    else:
        cursor.execute("SELECT student_id, name, email, department, gpa, enrollment_date FROM students ORDER BY id DESC;")
        students = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT department), AVG(gpa) FROM students;")
        row = cursor.fetchone()
        stats = {
            "total": row[0] or 0,
            "departments": row[1] or 0,
            "avg_gpa": float(row[2]) if row[2] else 0.0
        }

    cursor.close()
    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        students=students,
        stats=stats,
        hostname=HOSTNAME,
        host_ip=HOST_IP,
        db_type=db_type
    )


@app.route("/api/students", methods=["GET"])
def api_get_students():
    """Returns all students in JSON."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if "PostgreSQL" in db_type:
        cursor.execute("SELECT student_id, name, email, department, gpa, enrollment_date FROM students ORDER BY id ASC;")
        cols = [desc[0] for desc in cursor.description]
        students = [dict(zip(cols, row)) for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT student_id, name, email, department, gpa, enrollment_date FROM students ORDER BY id ASC;")
        students = [dict(row) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return jsonify({"count": len(students), "students": students, "pod_host": HOSTNAME})


@app.route("/api/students", methods=["POST"])
def api_create_student():
    """Adds a new student."""
    data = request.get_json() or {}
    required = ["student_id", "name", "email", "department", "gpa", "enrollment_date"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    try:
        if "PostgreSQL" in db_type:
            cursor.execute("""
                INSERT INTO students (student_id, name, email, department, gpa, enrollment_date)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (data["student_id"], data["name"], data["email"], data["department"], data["gpa"], data["enrollment_date"]))
        else:
            cursor.execute("""
                INSERT INTO students (student_id, name, email, department, gpa, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (data["student_id"], data["name"], data["email"], data["department"], data["gpa"], data["enrollment_date"]))
        conn.commit()
        return jsonify({"message": "Student created successfully", "student_id": data["student_id"]}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@app.route("/api/students/<student_id>", methods=["GET"])
def api_get_student(student_id):
    """Retrieves a single student record."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if "PostgreSQL" in db_type:
        cursor.execute("SELECT student_id, name, email, department, gpa, enrollment_date FROM students WHERE student_id = %s;", (student_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({"error": "Student not found"}), 404
        cols = [desc[0] for desc in cursor.description]
        student = dict(zip(cols, row))
    else:
        cursor.execute("SELECT student_id, name, email, department, gpa, enrollment_date FROM students WHERE student_id = ?;", (student_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({"error": "Student not found"}), 404
        student = dict(row)

    cursor.close()
    conn.close()
    return jsonify(student)


@app.route("/api/students/<student_id>", methods=["DELETE"])
def api_delete_student(student_id):
    """Deletes a student record."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    try:
        if "PostgreSQL" in db_type:
            cursor.execute("DELETE FROM students WHERE student_id = %s;", (student_id,))
        else:
            cursor.execute("DELETE FROM students WHERE student_id = ?;", (student_id,))
        conn.commit()
        return jsonify({"message": f"Student {student_id} deleted successfully."})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# ==========================================
# Kubernetes Health & Autoscaling Probes
# ==========================================

@app.route("/health")
def health():
    """Liveness & Readiness probe for Kubernetes."""
    db_status = "connected"
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    is_healthy = "unhealthy" not in db_status
    status_code = 200 if is_healthy else 503

    return jsonify({
        "status": "UP" if is_healthy else "DOWN",
        "service": "Cloud-Based Student Management System",
        "pod_name": HOSTNAME,
        "pod_ip": HOST_IP,
        "database": db_status,
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), status_code


@app.route("/metrics")
def metrics():
    """Metrics endpoint for Kubernetes / Prometheus monitoring."""
    uptime = int(time.time() - START_TIME)
    return jsonify({
        "pod_name": HOSTNAME,
        "uptime_seconds": uptime,
        "total_requests": REQUEST_COUNT,
        "active_threads": threading.active_count(),
        "status": "HEALTHY"
    })


@app.route("/api/load", methods=["POST", "GET"])
def trigger_load():
    """
    Simulates high CPU load to trigger Kubernetes Horizontal Pod Autoscaler (HPA).
    Runs floating-point calculations in a background thread for N seconds.
    """
    duration = 10
    if request.is_json and request.json and "duration" in request.json:
        duration = min(int(request.json["duration"]), 60)
    elif "duration" in request.args:
        duration = min(int(request.args.get("duration", 10)), 60)

    def cpu_stress(sec):
        end_time = time.time() + sec
        while time.time() < end_time:
            _ = [x ** 2 for x in range(10000)]

    thread = threading.Thread(target=cpu_stress, args=(duration,))
    thread.daemon = True
    thread.start()

    return jsonify({
        "message": f"CPU load simulation triggered for {duration} seconds.",
        "pod_name": HOSTNAME,
        "target": "HPA scaling demonstration"
    })


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Cloud-Based Student Management System on port {port}...")
    print(f"Pod Hostname: {HOSTNAME} | IP: {HOST_IP}")
    app.run(host="0.0.0.0", port=port, debug=False)
