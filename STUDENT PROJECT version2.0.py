import os
import sqlite3

print(" 1.Wanted to add student dails \n " \
"2.Wanted to serach detials \n " \
"3.Wanted to add atendence \n " \
"4.Wanted to change fees of students \n " 
"5.Wanted to change student's details \n" 
"6.Display all details \n" 
"7.Exit" )

conn = sqlite3.connect("student.db")
cur = conn.cursor()
print("Database location:", os.path.abspath("student.db"))

'''print(os.path.abspath("student.db"))
cur.execute("""
CREATE TABLE IF NOT EXISTS student (
    ID INTEGER PRIMARY KEY,
    Name TEXT,
    Class TEXT,
    fees REAL,
    attendence INTEGER
)
""")'''
# Student's database
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    semester INTEGER
)
""")

# Atendance database
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),

    FOREIGN KEY (student_id)
    REFERENCES students(student_id)
)
""")

# Payment's database
cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    payment_date TEXT NOT NULL,
    payment_mode TEXT,

    FOREIGN KEY (student_id)
    REFERENCES students(student_id)
)
""")

# Mark's database
cur.execute("""
CREATE TABLE IF NOT EXISTS marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    internal_marks REAL CHECK(internal_marks >= 0 AND internal_marks <= 30),
    external_marks REAL CHECK(external_marks >= 0 AND external_marks <= 70),

    FOREIGN KEY (student_id)
    REFERENCES students(student_id)
)
""")

conn.commit()

print("Database created successfully.")

while True:
     
    choice=int(input("Enter your choice 1-7:"))

    if choice==1:

        id=int(input("Enter student id:"))
        c=input("Enter name:")
        n=input("Enter the class_name:")
        e=input("Enter email:")
        p=int(input("Enter the phone no.:"))
        s=int(input("Enter the semester:"))

        cur.execute("INSERT INTO students (student_id, name , class_name , email , phone ,semester) VALUES(?,?,?,?,?,?)",(id,c,n,e,p,s))

        print("Data Added sucessfully")
        conn.commit()

#elif choice==2:
            
 #           search_id =int(input("Enter student's ID:"))
#           cur.execute("SELECT * from students where ID=?" , (search_id,))

 #           student = cur.fetchone()

  #          if student:
   #             print ("The data is:",student[:])

    #        else:
     #           print("wrong student searching!!!!!")'''

    elif choice == 2:

        search_id = int(input("Enter student's ID who's you want to know all the information: "))

        # -------------------------------------------------
        # 1. GET BASIC STUDENT DETAILS
        # -------------------------------------------------

        cur.execute("""
            SELECT student_id, name, class_name, email, phone, semester
            FROM students
            WHERE student_id = ?
        """, (search_id,))

        student = cur.fetchone()

        if student is None:
            print("\nStudent not found!")
            continue

        student_id = student[0]
        name = student[1]
        class_name = student[2]
        email = student[3]
        phone = student[4]
        semester = student[5]


        # -------------------------------------------------
        # 2. GET ATTENDANCE DETAILS
        # -------------------------------------------------

        cur.execute("""
            SELECT
                COUNT(*) AS total_classes,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_classes,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent_classes
            FROM attendance
            WHERE student_id = ?
        """, (search_id,))

        attendance = cur.fetchone()

        total_classes = attendance[0] or 0
        present_classes = attendance[1] or 0
        absent_classes = attendance[2] or 0

        if total_classes > 0:
            attendance_percentage = (present_classes / total_classes) * 100
        else:
            attendance_percentage = 0


        # -------------------------------------------------
        # 3. GET MARKS
        # -------------------------------------------------

        cur.execute("""
            SELECT subject, internal_marks, external_marks
            FROM marks
            WHERE student_id = ?
        """, (search_id,))

        marks = cur.fetchall()


        # -------------------------------------------------
        # 4. GET FEES / PAYMENT DETAILS
        # -------------------------------------------------

        cur.execute("""
            SELECT
                SUM(amount),
                COUNT(*),
                MAX(payment_date)
            FROM payments
            WHERE student_id = ?
        """, (search_id,))

        fees = cur.fetchone()

        total_paid = fees[0] or 0
        number_of_payments = fees[1] or 0
        last_payment = fees[2] if fees[2] else "No payment"


        # -------------------------------------------------
        # 5. DISPLAY COMPLETE STUDENT PROFILE
        # -------------------------------------------------

        print("\n")
        print("========== STUDENT PROFILE ==========")

        print(f"\nStudent ID : {student_id}")
        print(f"Name       : {name}")
        print(f"Class      : {class_name}")
        print(f"Email      : {email}")
        print(f"Phone      : {phone}")
        print(f"Semester   : {semester}")

        print("\n------------- ATTENDANCE ------------")

        print(f"Total Classes : {total_classes}")
        print(f"Present       : {present_classes}")
        print(f"Absent        : {absent_classes}")
        print(f"Attendance    : {attendance_percentage:.2f}%")

        print("\n------------- MARKS -----------------")

        if marks:
            for mark in marks:

                subject = mark[0]
                internal = mark[1] or 0
                external = mark[2] or 0

                total_marks = internal + external

                print(f"{subject:<15}: {total_marks:g}")

            else:
                print("No marks available.")

            print("\n------------- FEES ------------------")

            print(f"Total Paid   : ₹{total_paid:,.2f}")
            print(f"Payments     : {number_of_payments}")
            print(f"Last Payment : {last_payment}")

            print("\n=====================================")

    elif choice==3:

        search_id = int(input("Enter student's ID: "))

        # Check whether student exists
        cur.execute("""
            SELECT name
            FROM students
            WHERE student_id = ?
        """, (search_id,))

        student = cur.fetchone()

        if student is None:
            print("Student not found!")
            continue

        print(f"\nStudent: {student[0]}")

        # Enter attendance date
        attendance_date = input("Enter date (YYYY-MM-DD): ")

        # Enter attendance status
        attendance = input(
            "Was the student present today? (yes/no): ").strip().lower()

        if attendance == "yes":
            status = "Present"

        elif attendance == "no":
            status = "Absent"

        else:
            print("Invalid input! Enter only yes or no.")
            continue

        # Check if attendance is already recorded for this date
        cur.execute("""
            SELECT attendance_id
            FROM attendance
            WHERE student_id = ? AND attendance_date = ?""", (search_id, attendance_date))

        record = cur.fetchone()

        if record:
            print("Attendance for this date has already been recorded.")
            continue

        # Insert new attendance record
        cur.execute("""
            INSERT INTO attendance
            (student_id, attendance_date, status)
            VALUES (?, ?, ?)
        """, (search_id, attendance_date, status))

        conn.commit()

        print(f"Attendance marked as {status} successfully.")

    elif choice == 4:
    
            search_id = int(input("Enter student's ID: "))
    
            cur.execute("""SELECT name FROM students WHERE student_id = ?""", (search_id,))
            student = cur.fetchone()
    
            if student is None:
                print("Student not found!")
                continue
    
            print(f"\nStudent: {student[0]}")
    
            amount = float(input("Enter amount paid: ₹"))
    
            if amount <= 0:
                print("Payment amount must be greater than 0.")
                continue
    
            payment_date = input("Enter payment date (YYYY-MM-DD): ")
    
            payment_mode = input(
                "Enter payment mode (Cash/UPI/Card): "
            ).strip()
    
            if payment_mode.lower() not in ("cash", "upi", "card"):
                print("Invalid payment mode!")
                continue
    
            payment_mode = payment_mode.upper()
    
            cur.execute("""INSERT INTO payments (student_id, amount, payment_date, payment_mode) VALUES (?, ?, ?, ?)""", (search_id, amount, payment_date, payment_mode))
    
            conn.commit()
    
            print("\nPayment recorded successfully.")
    

    elif choice==5:
         
         search_id=int(input("Enter the id of the student:"))

         cur.execute("SELECT * FROM students WHERE ID=?", (search_id,))
         student = cur.fetchone()
        
         if student is None:
            print(f"Student with ID {search_id} does not exist.")
         else:
            print(f"Current details: Name={student[1]}, Class={student[2]}, Fees={student[3]}, Attendance={student[4]}")
            print("\nWhat detail do you want to change?")
            print("1. Name\n2. Class\n3. Fees\n4. Attendance")
            
            sub_choice = int(input("Enter sub-choice (1-4): "))
            
            if sub_choice == 1:
                new_name = input("Enter new name: ")
                cur.execute("UPDATE students SET Name=? WHERE ID=?", (new_name, search_id))
                print("Name updated successfully.")

            elif sub_choice == 2:
                new_class = input("Enter new class: ")
                cur.execute("UPDATE students SET Class=? WHERE ID=?", (new_class, search_id))
                print("Class updated successfully.")

            elif sub_choice == 3:
                new_fees = float(input("Enter new overall fees: "))
                cur.execute("UPDATE students SET fees=? WHERE ID=?", (new_fees, search_id))
                print("Fees updated successfully.")

            elif sub_choice == 4:
                new_attendance = int(input("Enter new attendance count: "))
                cur.execute("UPDATE students SET attendence=? WHERE ID=?", (new_attendance, search_id))
                print("Attendance updated successfully.")

            else:
                print("Invalid choice.")
            conn.commit()

    elif choice == 6:
         
        cur.execute("SELECT * FROM students")

        for row in cur.fetchall():
            print(row)

    elif choice==7:
        print("Thanks for the interaction")
        break

    else:
         print("Wrong iinput please enter the in between 1-7!!")

conn.commit()
conn.close()

print("Program ended successfully")
