from flask import Flask, render_template, request, session, redirect
import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = "student_management_secret_key"
def admin_required():
    if session.get("user_id") is None:
        return False

    return session.get("role") == "admin"


def faculty_required():
    if session.get("user_id") is None:
        return False

    return session.get("role") in ["admin", "faculty"]


def student_required():
    if session.get("user_id") is None:
        return False

    return session.get("role") == "student"


# ==========================================
# Supabase PostgreSQL Database Connection
# ==========================================

db = psycopg2.connect(
    os.getenv("DATABASE_URL")
)

print("Supabase PostgreSQL database connected successfully!")


# ==========================================
# Home / Login Page
# ==========================================

@app.route("/")
def home():
    return render_template("login.html")


# ==========================================
# Students Page
# ==========================================

@app.route("/students")
def students():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.close()

    return render_template(
        "students.html",
        students=students
    )
# ==========================================
# Faculty Page
# ==========================================

@app.route("/faculty")
def faculty():

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("SELECT * FROM faculty")

    faculty = cursor.fetchall()

    cursor.close()

    return render_template(
        "faculty.html",
        faculty=faculty
    )
# ==========================================
# Subject Management Page
# ==========================================

@app.route("/subjects")
def subjects():

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("SELECT * FROM subjects")

    subjects = cursor.fetchall()

    cursor.close()

    return render_template(
        "subjects.html",
        subjects=subjects
    )
@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    if request.method == "POST":

        subject_code = request.form["subject_code"]
        subject_name = request.form["subject_name"]
        department = request.form["department"]
        year = request.form["year"]
        semester = request.form["semester"]
        faculty_id = request.form["faculty_id"]

        query = """
            INSERT INTO subjects
            (subject_code, subject_name, department, year, semester, faculty_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            subject_code,
            subject_name,
            department,
            year,
            semester,
            faculty_id
        )

        cursor.execute(query, values)
        db.commit()
        cursor.close()

        return "Subject added successfully!"

    cursor.execute("SELECT id, faculty_id, name FROM faculty")
    faculty = cursor.fetchall()

    cursor.close()

    return render_template("add_subject.html", faculty=faculty)
@app.route("/edit_subject/<int:subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    if request.method == "POST":

        subject_code = request.form["subject_code"]
        subject_name = request.form["subject_name"]
        department = request.form["department"]
        year = request.form["year"]
        semester = request.form["semester"]
        faculty_id = request.form["faculty_id"]

        query = """
            UPDATE subjects
            SET subject_code = %s,
                subject_name = %s,
                department = %s,
                year = %s,
                semester = %s,
                faculty_id = %s
            WHERE id = %s
        """

        values = (
            subject_code,
            subject_name,
            department,
            year,
            semester,
            faculty_id,
            subject_id
        )

        cursor.execute(query, values)

        db.commit()
        cursor.close()

        return redirect("/subjects")

    cursor.execute("""
        SELECT *
        FROM subjects
        WHERE id = %s
    """, (subject_id,))

    subject = cursor.fetchone()

    cursor.execute("""
        SELECT id, faculty_id, name
        FROM faculty
    """)

    faculty = cursor.fetchall()

    cursor.close()

    return render_template(
        "edit_subject.html",
        subject=subject,
        faculty=faculty
    )
@app.route("/delete_subject/<int:subject_id>")
def delete_subject(subject_id):

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM subjects
        WHERE id = %s
    """, (subject_id,))

    db.commit()
    cursor.close()

    return redirect("/subjects")
# ==========================================
# Add Faculty
# ==========================================

@app.route("/add_faculty", methods=["GET", "POST"])
def add_faculty():

    if not admin_required():
        return "Access denied!"

    if request.method == "POST":

        faculty_id = request.form["faculty_id"]
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        designation = request.form["designation"]

        cursor = db.cursor()

        query = """
            INSERT INTO faculty
            (faculty_id, name, email, phone, department, designation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            faculty_id,
            name,
            email,
            phone,
            department,
            designation
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return "Faculty added successfully!"

    return render_template("add_faculty.html")
# ==========================================
# Edit Faculty
# ==========================================

@app.route("/edit_faculty/<int:faculty_id>", methods=["GET", "POST"])
def edit_faculty(faculty_id):

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    # Get existing faculty details
    cursor.execute(
        "SELECT * FROM faculty WHERE id = %s",
        (faculty_id,)
    )

    faculty = cursor.fetchone()

    # If faculty doesn't exist
    if faculty is None:
        cursor.close()
        return "Faculty not found!"

    # Update faculty
    if request.method == "POST":

        faculty_code = request.form["faculty_id"]
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        designation = request.form["designation"]

        query = """
            UPDATE faculty
            SET faculty_id = %s,
                name = %s,
                email = %s,
                phone = %s,
                department = %s,
                designation = %s
            WHERE id = %s
        """

        values = (
            faculty_code,
            name,
            email,
            phone,
            department,
            designation,
            faculty_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return "Faculty updated successfully!"

    cursor.close()

    return render_template(
        "edit_faculty.html",
        faculty=faculty
    )
# ==========================================
# Delete Faculty
# ==========================================

@app.route("/delete_faculty/<int:faculty_id>")
def delete_faculty(faculty_id):

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM faculty WHERE id = %s",
        (faculty_id,)
    )

    db.commit()

    cursor.close()

    return "Faculty deleted successfully!"


# ==========================================
# Add Student
# ==========================================

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
        
    if not admin_required():
        return "Access denied!"

    if request.method == "POST":

        student_id = request.form["student_id"]
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        year = request.form["year"]
        section = request.form["section"]

        cursor = db.cursor()

        query = """
            INSERT INTO students
            (student_id, name, email, phone, department, year, section)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            student_id,
            name,
            email,
            phone,
            department,
            year,
            section
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return "Student added successfully!"

    return render_template("add_student.html")
# ==========================================
# Edit Student
# ==========================================

@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    # Get existing student details
    cursor.execute(
        "SELECT * FROM students WHERE id = %s",
        (student_id,)
    )

    student = cursor.fetchone()

    # If student doesn't exist
    if student is None:
        cursor.close()
        return "Student not found!"

    # Update student
    if request.method == "POST":

        student_code = request.form["student_id"]
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        year = request.form["year"]
        section = request.form["section"]

        query = """
            UPDATE students
            SET student_id = %s,
                name = %s,
                email = %s,
                phone = %s,
                department = %s,
                year = %s,
                section = %s
            WHERE id = %s
        """

        values = (
            student_code,
            name,
            email,
            phone,
            department,
            year,
            section,
            student_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return "Student updated successfully!"

    cursor.close()

    return render_template(
        "edit_student.html",
        student=student
    )
# ==========================================
# Delete Student
# ==========================================

@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = %s",
        (student_id,)
    )

    db.commit()

    cursor.close()

    return "Student deleted successfully!"
@app.route("/attendance")
def attendance():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("""
        SELECT id, subject_code, subject_name
        FROM subjects
    """)
    subjects = cursor.fetchall()

    cursor.execute("""
        SELECT id, student_id, name
        FROM students
    """)
    students = cursor.fetchall()

    cursor.close()

    return render_template(
        "attendance.html",
        subjects=subjects,
        students=students
    )

# ==========================================
# Login
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    cursor = db.cursor()

    query = """
        SELECT * FROM users
        WHERE username = %s AND role = %s
    """

    cursor.execute(query, (username, role))

    user = cursor.fetchone()

    cursor.close()

    if user:

        if check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]

            if role == "admin":
                return redirect("/admin_dashboard")

            elif role == "faculty":
                return redirect("/faculty_dashboard")

            elif role == "student":
                return redirect("/student_dashboard")

    return "Invalid username, password, or role!"
@app.route("/save_attendance", methods=["POST"])
def save_attendance():

    if not faculty_required():
        return "Access denied!"

    subject_id = request.form["subject_id"]
    attendance_date = request.form["attendance_date"]

    cursor = db.cursor()

    cursor.execute("SELECT id FROM students")
    students = cursor.fetchall()

    try:

        for student in students:

            student_id = student[0]

            status = request.form[f"status_{student_id}"]

            query = """
                INSERT INTO attendance_records
                (student_id, subject_id, attendance_date, status)
                VALUES (%s, %s, %s, %s)
            """

            values = (
                student_id,
                subject_id,
                attendance_date,
                status
            )

            cursor.execute(query, values)

        db.commit()

    except psycopg2.Error as error:

        db.rollback()

        cursor.close()

        if error.errno == 1062:
            return """
                <h2 style="text-align:center;">
                    Attendance already exists for this subject and date!
                </h2>

                <p style="text-align:center;">
                    Please choose a different date.
                </p>

                <div style="text-align:center;">
                    <a href="/attendance">
                        <button>Back to Attendance</button>
                    </a>
                </div>
            """

        return "Database error occurred!"

    cursor.close()

    return "Attendance saved successfully!"
@app.route("/attendance_report")
def attendance_report():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    query = """
        SELECT
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name,
            COUNT(attendance_records.id) AS total_classes,
            COUNT(*) FILTER (
                WHERE attendance_records.status = 'Present'
            ) AS present_classes,
            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE attendance_records.status = 'Present'
                    )::numeric
                    / COUNT(attendance_records.id)
                ) * 100,
                2
            ) AS attendance_percentage
        FROM attendance_records
        JOIN students
            ON attendance_records.student_id = students.id
        JOIN subjects
            ON attendance_records.subject_id = subjects.id
        GROUP BY
            students.id,
            subjects.id,
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name
        ORDER BY
            students.student_id,
            subjects.subject_code
    """

    cursor.execute(query)
    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "attendance_report.html",
        records=records
    )
@app.route("/manage_attendance")
def manage_attendance():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    query = """
        SELECT
            attendance_records.id,
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name,
            attendance_records.attendance_date,
            attendance_records.status
        FROM attendance_records
        JOIN students
            ON attendance_records.student_id = students.id
        JOIN subjects
            ON attendance_records.subject_id = subjects.id
        ORDER BY attendance_records.attendance_date DESC
    """

    cursor.execute(query)

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "manage_attendance.html",
        records=records
    )
@app.route("/edit_attendance/<int:attendance_id>", methods=["GET", "POST"])
def edit_attendance(attendance_id):

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    if request.method == "POST":

        status = request.form["status"]

        cursor.execute("""
            UPDATE attendance_records
            SET status = %s
            WHERE id = %s
        """, (status, attendance_id))

        db.commit()

        cursor.close()

        return redirect("/manage_attendance")

    cursor.execute("""
        SELECT
            attendance_records.id,
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name,
            attendance_records.attendance_date,
            attendance_records.status
        FROM attendance_records
        JOIN students
            ON attendance_records.student_id = students.id
        JOIN subjects
            ON attendance_records.subject_id = subjects.id
        WHERE attendance_records.id = %s
    """, (attendance_id,))

    record = cursor.fetchone()

    cursor.close()

    if not record:
        return "Attendance record not found!"

    return render_template(
        "edit_attendance.html",
        record=record
    )
@app.route("/delete_attendance/<int:attendance_id>")
def delete_attendance(attendance_id):

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM attendance_records
        WHERE id = %s
    """, (attendance_id,))

    db.commit()

    cursor.close()

    return redirect("/manage_attendance")
@app.route("/marks")
def marks():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("""
        SELECT id, student_id, name
        FROM students
    """)
    students = cursor.fetchall()

    cursor.execute("""
        SELECT id, subject_code, subject_name
        FROM subjects
    """)
    subjects = cursor.fetchall()

    cursor.close()

    return render_template(
        "marks.html",
        students=students,
        subjects=subjects
    )
@app.route("/save_marks", methods=["POST"])
def save_marks():

    if not faculty_required():
        return "Access denied!"

    student_id = request.form["student_id"]
    subject_id = request.form["subject_id"]
    marks = request.form["marks"]
    exam_type = request.form["exam_type"]

    cursor = db.cursor()

    query = """
        INSERT INTO marks
        (student_id, subject_id, marks, exam_type)
        VALUES (%s, %s, %s, %s)
    """

    values = (
        student_id,
        subject_id,
        marks,
        exam_type
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return "Marks saved successfully!"
@app.route("/marks_report")
def marks_report():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    query = """
        SELECT
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name,
            marks.exam_type,
            marks.marks
        FROM marks
        JOIN students
            ON marks.student_id = students.id
        JOIN subjects
            ON marks.subject_id = subjects.id
        ORDER BY students.student_id
    """

    cursor.execute(query)

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "marks_report.html",
        records=records
    )
@app.route("/manage_marks")
def manage_marks():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    query = """
        SELECT
            marks.id,
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name,
            marks.exam_type,
            marks.marks
        FROM marks
        JOIN students
            ON marks.student_id = students.id
        JOIN subjects
            ON marks.subject_id = subjects.id
        ORDER BY students.student_id
    """

    cursor.execute(query)

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "manage_marks.html",
        records=records
    )
@app.route("/edit_marks/<int:mark_id>", methods=["GET", "POST"])
def edit_marks(mark_id):

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    if request.method == "POST":

        marks = request.form["marks"]

        cursor.execute("""
            UPDATE marks
            SET marks = %s
            WHERE id = %s
        """, (marks, mark_id))

        db.commit()

        cursor.close()

        return redirect("/manage_marks")

    cursor.execute("""
        SELECT
            marks.id,
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name,
            marks.exam_type,
            marks.marks
        FROM marks
        JOIN students
            ON marks.student_id = students.id
        JOIN subjects
            ON marks.subject_id = subjects.id
        WHERE marks.id = %s
    """, (mark_id,))

    record = cursor.fetchone()

    cursor.close()

    if not record:
        return "Marks record not found!"

    return render_template(
        "edit_marks.html",
        record=record
    )
@app.route("/delete_marks/<int:mark_id>")
def delete_marks(mark_id):

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM marks
        WHERE id = %s
    """, (mark_id,))

    db.commit()

    cursor.close()

    return redirect("/manage_marks")
@app.route("/admin_dashboard")
def admin_dashboard():

    if not admin_required():
        return "Access denied!"

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    faculty_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM subjects")
    subject_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance_records")
    attendance_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM marks")
    marks_count = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "admin_dashboard.html",
        student_count=student_count,
        faculty_count=faculty_count,
        subject_count=subject_count,
        attendance_count=attendance_count,
        marks_count=marks_count
    )
@app.route("/faculty_dashboard")
def faculty_dashboard():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    # Get faculty name
    cursor.execute("""
        SELECT name
        FROM faculty
        LIMIT 1
    """)

    faculty = cursor.fetchone()

    if not faculty:
        cursor.close()
        return "Faculty profile not found!"

    faculty_name = faculty[0]

    # Total students
    cursor.execute("""
        SELECT COUNT(*)
        FROM students
    """)
    student_count = cursor.fetchone()[0]

    # Total subjects
    cursor.execute("""
        SELECT COUNT(*)
        FROM subjects
    """)
    subject_count = cursor.fetchone()[0]

    # Total attendance records
    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance_records
    """)
    attendance_count = cursor.fetchone()[0]

    # Total marks records
    cursor.execute("""
        SELECT COUNT(*)
        FROM marks
    """)
    marks_count = cursor.fetchone()[0]

    # Low attendance cases
    cursor.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT
                students.id AS student_id,
                subjects.id AS subject_id
            FROM attendance_records
            JOIN students
                ON attendance_records.student_id = students.id
            JOIN subjects
                ON attendance_records.subject_id = subjects.id
            GROUP BY
                students.id,
                subjects.id
            HAVING
                (
                    COUNT(*) FILTER (
                        WHERE attendance_records.status = 'Present'
                    )::numeric
                    / COUNT(attendance_records.id)
                ) * 100 < 75
        ) AS low_attendance
    """)

    low_attendance_count = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "faculty_dashboard.html",
        faculty_name=faculty_name,
        student_count=student_count,
        subject_count=subject_count,
        attendance_count=attendance_count,
        marks_count=marks_count,
        low_attendance_count=low_attendance_count
    )
@app.route("/low_attendance")
def low_attendance():

    if not faculty_required():
        return "Access denied!"

    cursor = db.cursor()

    query = """
        SELECT
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name,
            COUNT(attendance_records.id) AS total_classes,
            COUNT(*) FILTER (
                WHERE attendance_records.status = 'Present'
            ) AS present_classes,
            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE attendance_records.status = 'Present'
                    )::numeric
                    / COUNT(attendance_records.id)
                ) * 100,
                2
            ) AS attendance_percentage
        FROM attendance_records
        JOIN students
            ON attendance_records.student_id = students.id
        JOIN subjects
            ON attendance_records.subject_id = subjects.id
        GROUP BY
            students.id,
            subjects.id,
            students.student_id,
            students.name,
            subjects.subject_code,
            subjects.subject_name
        HAVING
            (
                COUNT(*) FILTER (
                    WHERE attendance_records.status = 'Present'
                )::numeric
                / COUNT(attendance_records.id)
            ) * 100 < 75
        ORDER BY
            students.student_id,
            subjects.subject_code
    """

    cursor.execute(query)
    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "low_attendance.html",
        records=records
    )
@app.route("/student_attendance")
def student_attendance():

    if not student_required():
        return "Access denied!"

    user_id = session.get("user_id")

    cursor = db.cursor()

    cursor.execute("""
        SELECT id
        FROM students
        WHERE user_id = %s
    """, (user_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        return "Student profile not found!"

    student_id = student[0]

    cursor.execute("""
        SELECT
            subjects.subject_code,
            subjects.subject_name,
            COUNT(attendance_records.id) AS total_classes,
            COUNT(*) FILTER (
                WHERE attendance_records.status = 'Present'
            ) AS present_classes
        FROM attendance_records
        JOIN subjects
            ON attendance_records.subject_id = subjects.id
        WHERE attendance_records.student_id = %s
        GROUP BY
            subjects.id,
            subjects.subject_code,
            subjects.subject_name
        ORDER BY subjects.subject_code
    """, (student_id,))

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "student_attendance.html",
        records=records
    )
@app.route("/student_dashboard")
def student_dashboard():

    if not student_required():
        return "Access denied!"

    user_id = session.get("user_id")

    cursor = db.cursor()

    cursor.execute("""
        SELECT id, name, department, year
        FROM students
        WHERE user_id = %s
    """, (user_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        return "Student profile not found!"

    student_id = student[0]
    student_name = student[1]

    cursor.execute("""
        SELECT COUNT(*)
        FROM subjects
        WHERE UPPER(department) = UPPER(%s)
        AND year = %s
    """, (student[2], student[3]))

    subject_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance_records
        WHERE student_id = %s
    """, (student_id,))

    total_classes = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance_records
        WHERE student_id = %s
        AND status = 'Present'
    """, (student_id,))

    present_classes = cursor.fetchone()[0]

    if total_classes > 0:
        attendance_percentage = round(
            (present_classes / total_classes) * 100,
            2
        )
    else:
        attendance_percentage = 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM marks
        WHERE student_id = %s
    """, (student_id,))

    marks_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            subjects.subject_name,
            COUNT(attendance_records.id) AS total_classes,
            COUNT(*) FILTER (
                WHERE attendance_records.status = 'Present'
            ) AS present_classes
        FROM attendance_records
        JOIN subjects
            ON attendance_records.subject_id = subjects.id
        WHERE attendance_records.student_id = %s
        GROUP BY subjects.id, subjects.subject_name
        ORDER BY subjects.subject_name
    """, (student_id,))

    attendance_records = cursor.fetchall()

    attendance_labels = []
    attendance_percentages = []

    for record in attendance_records:

        subject_name = record[0]
        total = record[1]
        present = record[2]

        if total > 0:
            percentage = round((present / total) * 100, 2)
        else:
            percentage = 0

        attendance_labels.append(subject_name)
        attendance_percentages.append(percentage)

    cursor.close()

    return render_template(
        "student_dashboard.html",
        student_name=student_name,
        subject_count=subject_count,
        total_classes=total_classes,
        present_classes=present_classes,
        attendance_percentage=attendance_percentage,
        marks_count=marks_count,
        attendance_labels=attendance_labels,
        attendance_percentages=attendance_percentages
    )
@app.route("/student_performance")
def student_performance():

    if not student_required():
        return "Access denied!"

    user_id = session.get("user_id")

    cursor = db.cursor()

    cursor.execute("""
        SELECT id
        FROM students
        WHERE user_id = %s
    """, (user_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        return "Student profile not found!"

    student_id = student[0]

    cursor.execute("""
        SELECT
            subjects.subject_code,
            subjects.subject_name,
            marks.exam_type,
            marks.marks
        FROM marks
        JOIN subjects
            ON marks.subject_id = subjects.id
        WHERE marks.student_id = %s
        ORDER BY subjects.subject_code
    """, (student_id,))

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "student_performance.html",
        records=records
    )
@app.route("/student_low_attendance")
def student_low_attendance():

    if not student_required():
        return "Access denied!"

    user_id = session.get("user_id")

    cursor = db.cursor()

    cursor.execute("""
        SELECT id
        FROM students
        WHERE user_id = %s
    """, (user_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        return "Student profile not found!"

    student_id = student[0]

    cursor.execute("""
        SELECT
            subjects.subject_code,
            subjects.subject_name,
            COUNT(attendance_records.id) AS total_classes,
            COUNT(*) FILTER (
                WHERE attendance_records.status = 'Present'
            ) AS present_classes
        FROM attendance_records
        JOIN subjects
            ON attendance_records.subject_id = subjects.id
        WHERE attendance_records.student_id = %s
        GROUP BY
            subjects.id,
            subjects.subject_code,
            subjects.subject_name
        HAVING
            (
                COUNT(*) FILTER (
                    WHERE attendance_records.status = 'Present'
                )::numeric
                / COUNT(attendance_records.id)
            ) * 100 < 75
        ORDER BY subjects.subject_code
    """, (student_id,))

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "student_low_attendance.html",
        records=records
    )
@app.route("/student_subjects")
def student_subjects():

    if not student_required():
        return "Access denied!"

    user_id = session.get("user_id")

    cursor = db.cursor()

    cursor.execute("""
        SELECT department, year
        FROM students
        WHERE user_id = %s
    """, (user_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        return "Student profile not found!"

    department = student[0]
    year = student[1]

    cursor.execute("""
        SELECT
            subject_code,
            subject_name,
            department,
            year,
            semester
        FROM subjects
        WHERE UPPER(department) = UPPER(%s)
        AND year = %s
        ORDER BY subject_code
    """, (department, year))

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "student_subjects.html",
        records=records
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")
# ==========================================
# Run Flask Application
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)