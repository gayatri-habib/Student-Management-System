"""
========================================
  Student Management System
  Built with Python | OOP | File Handling
  Author: Data Analyst Portfolio Project
========================================
Features:
  - Add, View, Update, Delete Students
  - Search by Name, ID, or Grade
  - Grade & GPA Calculator
  - Data Persistence using JSON
  - Input Validation & Error Handling
  - Summary Statistics Report
"""

import json
import os
import sys
from datetime import datetime


# ─────────────────────────────────────────
#  Student Class (OOP)
# ─────────────────────────────────────────

class Student:
    """Represents a single student record."""

    def _init_(self, student_id, name, age, grade, email, marks):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.email = email
        self.marks = marks  # dict: {"Math": 85, "Science": 90, ...}
        self.gpa = self.calculate_gpa()
        self.enrolled_on = datetime.now().strftime("%Y-%m-%d")

    def calculate_gpa(self):
        """Calculate GPA based on average marks (4.0 scale)."""
        if not self.marks:
            return 0.0
        avg = sum(self.marks.values()) / len(self.marks)
        if avg >= 90:   return 4.0
        elif avg >= 80: return 3.0
        elif avg >= 70: return 2.0
        elif avg >= 60: return 1.0
        else:           return 0.0

    def get_average(self):
        if not self.marks:
            return 0.0
        return round(sum(self.marks.values()) / len(self.marks), 2)

    def to_dict(self):
        """Convert student object to dictionary for JSON storage."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "grade": self.grade,
            "email": self.email,
            "marks": self.marks,
            "gpa": self.gpa,
            "enrolled_on": self.enrolled_on
        }

    @classmethod
    def from_dict(cls, data):
        """Create Student object from dictionary (loaded from JSON)."""
        obj = cls(
            data["student_id"],
            data["name"],
            data["age"],
            data["grade"],
            data["email"],
            data["marks"]
        )
        obj.gpa = data.get("gpa", obj.gpa)
        obj.enrolled_on = data.get("enrolled_on", obj.enrolled_on)
        return obj

    def display(self):
        """Print formatted student details."""
        print("\n" + "─" * 45)
        print(f"  🎓 Student ID   : {self.student_id}")
        print(f"  📛 Name         : {self.name}")
        print(f"  🎂 Age          : {self.age}")
        print(f"  📚 Grade        : {self.grade}")
        print(f"  📧 Email        : {self.email}")
        print(f"  📅 Enrolled On  : {self.enrolled_on}")
        print(f"  📊 Subjects & Marks:")
        for subject, mark in self.marks.items():
            print(f"       {subject:<15}: {mark}")
        print(f"  📈 Average      : {self.get_average()}%")
        print(f"  ⭐ GPA          : {self.gpa}")
        print("─" * 45)


# ─────────────────────────────────────────
#  StudentManagementSystem Class
# ─────────────────────────────────────────

class StudentManagementSystem:
    """Core system for managing student records."""

    FILE_PATH = "students_data.json"

    def _init_(self):
        self.students = {}  # {student_id: Student}
        self.load_data()

    # ── File Handling (Persistence) ──────

    def load_data(self):
        """Load student records from JSON file."""
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r") as f:
                    raw = json.load(f)
                    self.students = {
                        sid: Student.from_dict(data)
                        for sid, data in raw.items()
                    }
                print(f"✅ Loaded {len(self.students)} student(s) from file.")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️  Could not load data: {e}. Starting fresh.")
                self.students = {}
        else:
            print("📂 No existing data found. Starting fresh.")

    def save_data(self):
        """Save all student records to JSON file."""
        with open(self.FILE_PATH, "w") as f:
            json.dump(
                {sid: s.to_dict() for sid, s in self.students.items()},
                f,
                indent=4
            )
        print("💾 Data saved successfully.")

    # ── Input Validation ─────────────────

    def validate_email(self, email):
        return "@" in email and "." in email.split("@")[-1]

    def validate_marks(self, mark):
        try:
            m = float(mark)
            return 0 <= m <= 100
        except ValueError:
            return False

    def generate_id(self):
        """Auto-generate a unique student ID."""
        existing = [int(k.replace("STU", "")) for k in self.students if k.startswith("STU")]
        next_num = max(existing, default=0) + 1
        return f"STU{next_num:04d}"

    # ── CRUD Operations ──────────────────

    def add_student(self):
        """Add a new student record with input validation."""
        print("\n" + "═" * 45)
        print("  ➕  ADD NEW STUDENT")
        print("═" * 45)

        student_id = self.generate_id()
        print(f"  Auto-generated Student ID: {student_id}")

        name = input("  Enter Full Name       : ").strip()
        if not name:
            print("❌ Name cannot be empty.")
            return

        try:
            age = int(input("  Enter Age             : "))
            if not (5 <= age <= 100):
                print("❌ Age must be between 5 and 100.")
                return
        except ValueError:
            print("❌ Invalid age. Enter a number.")
            return

        grade = input("  Enter Grade (e.g. 10A): ").strip().upper()
        email = input("  Enter Email           : ").strip()
        if not self.validate_email(email):
            print("❌ Invalid email format.")
            return

        # Collect marks for subjects
        subjects = ["Math", "Science", "English", "History", "Computer"]
        marks = {}
        print("\n  Enter marks (0–100) for each subject:")
        for subj in subjects:
            while True:
                m = input(f"    {subj:<12}: ")
                if self.validate_marks(m):
                    marks[subj] = float(m)
                    break
                print(f"    ⚠️  Invalid. Enter a value between 0 and 100.")

        student = Student(student_id, name, age, grade, email, marks)
        self.students[student_id] = student
        self.save_data()

        print(f"\n✅ Student '{name}' added successfully! ID: {student_id}")
        student.display()

    def view_all_students(self):
        """Display all student records in a table."""
        if not self.students:
            print("\n⚠️  No students found.")
            return

        print("\n" + "═" * 75)
        print(f"  📋  ALL STUDENTS  (Total: {len(self.students)})")
        print("═" * 75)
        print(f"  {'ID':<10} {'Name':<20} {'Age':<5} {'Grade':<8} {'Avg %':<8} {'GPA'}")
        print("─" * 75)
        for s in self.students.values():
            print(f"  {s.student_id:<10} {s.name:<20} {s.age:<5} {s.grade:<8} {s.get_average():<8} {s.gpa}")
        print("═" * 75)

    def search_student(self):
        """Search students by ID, name, or grade."""
        print("\n  Search by: 1) ID   2) Name   3) Grade")
        choice = input("  Enter choice: ").strip()

        results = []

        if choice == "1":
            sid = input("  Enter Student ID: ").strip().upper()
            if sid in self.students:
                results = [self.students[sid]]
            else:
                print(f"❌ No student found with ID: {sid}")
                return

        elif choice == "2":
            name = input("  Enter Name (partial ok): ").strip().lower()
            results = [s for s in self.students.values() if name in s.name.lower()]

        elif choice == "3":
            grade = input("  Enter Grade: ").strip().upper()
            results = [s for s in self.students.values() if s.grade == grade]

        else:
            print("❌ Invalid choice.")
            return

        if results:
            print(f"\n  ✅ Found {len(results)} result(s):")
            for s in results:
                s.display()
        else:
            print("⚠️  No matching students found.")

    def update_student(self):
        """Update an existing student's details."""
        sid = input("\n  Enter Student ID to update: ").strip().upper()
        if sid not in self.students:
            print(f"❌ Student ID '{sid}' not found.")
            return

        s = self.students[sid]
        print(f"\n  Updating: {s.name}")
        print("  Press ENTER to keep the current value.\n")

        new_name = input(f"  Name [{s.name}]: ").strip()
        if new_name: s.name = new_name

        new_age = input(f"  Age [{s.age}]: ").strip()
        if new_age:
            try:
                s.age = int(new_age)
            except ValueError:
                print("⚠️  Invalid age, keeping original.")

        new_grade = input(f"  Grade [{s.grade}]: ").strip().upper()
        if new_grade: s.grade = new_grade

        new_email = input(f"  Email [{s.email}]: ").strip()
        if new_email:
            if self.validate_email(new_email):
                s.email = new_email
            else:
                print("⚠️  Invalid email, keeping original.")

        print("\n  Update marks? (y/n): ", end="")
        if input().strip().lower() == "y":
            for subj in s.marks:
                while True:
                    m = input(f"    {subj} [{s.marks[subj]}]: ").strip()
                    if not m:
                        break
                    if self.validate_marks(m):
                        s.marks[subj] = float(m)
                        break
                    print("    ⚠️  Enter 0–100.")
            s.gpa = s.calculate_gpa()

        self.save_data()
        print(f"\n✅ Student '{s.name}' updated successfully!")
        s.display()

    def delete_student(self):
        """Delete a student record by ID."""
        sid = input("\n  Enter Student ID to delete: ").strip().upper()
        if sid not in self.students:
            print(f"❌ Student ID '{sid}' not found.")
            return

        name = self.students[sid].name
        confirm = input(f"  ⚠️  Delete '{name}'? This cannot be undone. (yes/no): ").strip().lower()
        if confirm == "yes":
            del self.students[sid]
            self.save_data()
            print(f"✅ Student '{name}' deleted successfully.")
        else:
            print("❎ Deletion cancelled.")

    # ── Reports & Statistics ─────────────

    def summary_report(self):
        """Display summary statistics of all students."""
        if not self.students:
            print("\n⚠️  No student data available.")
            return

        all_avgs = [s.get_average() for s in self.students.values()]
        all_gpas = [s.gpa for s in self.students.values()]

        top_student = max(self.students.values(), key=lambda s: s.get_average())
        low_student = min(self.students.values(), key=lambda s: s.get_average())

        grade_counts = {}
        for s in self.students.values():
            grade_counts[s.grade] = grade_counts.get(s.grade, 0) + 1

        print("\n" + "═" * 45)
        print("  📊  SUMMARY REPORT")
        print("═" * 45)
        print(f"  Total Students    : {len(self.students)}")
        print(f"  Average Score     : {round(sum(all_avgs)/len(all_avgs), 2)}%")
        print(f"  Average GPA       : {round(sum(all_gpas)/len(all_gpas), 2)}")
        print(f"  Highest Scorer    : {top_student.name} ({top_student.get_average()}%)")
        print(f"  Lowest Scorer     : {low_student.name} ({low_student.get_average()}%)")
        print(f"\n  Students by Grade:")
        for grade, count in sorted(grade_counts.items()):
            print(f"    Grade {grade:<6}: {count} student(s)")

        # Pass/Fail breakdown
        passed = sum(1 for a in all_avgs if a >= 60)
        failed = len(all_avgs) - passed
        print(f"\n  Pass (≥60%)  : {passed}")
        print(f"  Fail (<60%)  : {failed}")
        print("═" * 45)


# ─────────────────────────────────────────
#  Main Menu
# ─────────────────────────────────────────

def display_menu():
    print("\n" + "═" * 45)
    print("   🎓  STUDENT MANAGEMENT SYSTEM")
    print("═" * 45)
    print("   1. ➕  Add New Student")
    print("   2. 📋  View All Students")
    print("   3. 🔍  Search Student")
    print("   4. ✏️   Update Student")
    print("   5. 🗑️   Delete Student")
    print("   6. 📊  Summary Report")
    print("   7. 🚪  Exit")
    print("═" * 45)


def main():
    print("\n" + "═" * 45)
    print("  Welcome to Student Management System")
    print("  Python | OOP | JSON | CLI")
    print("═" * 45)

    sms = StudentManagementSystem()

    while True:
        display_menu()
        choice = input("  Enter your choice (1–7): ").strip()

        if choice == "1":
            sms.add_student()
        elif choice == "2":
            sms.view_all_students()
        elif choice == "3":
            sms.search_student()
        elif choice == "4":
            sms.update_student()
        elif choice == "5":
            sms.delete_student()
        elif choice == "6":
            sms.summary_report()
        elif choice == "7":
            print("\n  👋 Thank you for using Student Management System. Goodbye!\n")
            sys.exit(0)
        else:
            print("  ❌ Invalid choice. Please enter 1–7.")


if __name__ == "__main__":
    main()