import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date, datetime
import itertools

DB_NAME = 'registry.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Specialties (
            SpecialtyID INTEGER PRIMARY KEY AUTOINCREMENT,
            SpecialtyName TEXT NOT NULL,
            Description TEXT
        );

        CREATE TABLE IF NOT EXISTS Doctors (
            DoctorID INTEGER PRIMARY KEY AUTOINCREMENT,
            LastName TEXT NOT NULL,
            FirstName TEXT NOT NULL,
            MiddleName TEXT,
            SpecialtyID INTEGER NOT NULL,
            Cabinet TEXT,
            WorkPhone TEXT,
            IsActive INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (SpecialtyID) REFERENCES Specialties(SpecialtyID)
        );

        CREATE TABLE IF NOT EXISTS Patients (
            PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
            LastName TEXT NOT NULL,
            FirstName TEXT NOT NULL,
            MiddleName TEXT,
            DateOfBirth TEXT NOT NULL,
            Phone TEXT,
            Email TEXT,
            Address TEXT,
            CreatedAt TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT NOT NULL UNIQUE,
            PasswordHash TEXT NOT NULL,
            Role TEXT NOT NULL CHECK (Role IN ('Пациент','Врач','Администратор')),
            PatientID INTEGER,
            DoctorID INTEGER,
            IsActive INTEGER NOT NULL DEFAULT 1,
            LastLogin TEXT,
            FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
            FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
        );

        CREATE TABLE IF NOT EXISTS Appointments (
            AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            DoctorID INTEGER NOT NULL,
            PatientID INTEGER NOT NULL,
            AppointmentDate TEXT NOT NULL,
            AppointmentTime TEXT NOT NULL,
            Status TEXT NOT NULL DEFAULT 'Активна' CHECK (Status IN ('Активна','Отменена','Завершена','Неявка')),
            Complaint TEXT,
            DoctorNotes TEXT,
            CreatedAt TEXT NOT NULL DEFAULT (datetime('now')),
            UpdatedAt TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID),
            FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
        );
    ''')

    cursor.execute("SELECT COUNT(*) FROM Specialties")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Specialties (SpecialtyName, Description) VALUES (?,?)", ('Терапевт', 'Врач общей практики'))
        cursor.execute("INSERT INTO Specialties (SpecialtyName, Description) VALUES (?,?)", ('Хирург', 'Хирургическое лечение'))
        cursor.execute("INSERT INTO Specialties (SpecialtyName, Description) VALUES (?,?)", ('Педиатр', 'Детский врач'))
        cursor.execute("INSERT INTO Specialties (SpecialtyName, Description) VALUES (?,?)", ('Офтальмолог', 'Лечение заболеваний глаз'))

        cursor.execute("INSERT INTO Doctors (LastName, FirstName, MiddleName, SpecialtyID, Cabinet, WorkPhone) VALUES (?,?,?,?,?,?)",
                       ('Иванова', 'Мария', 'Петровна', 1, '101', '555-101'))
        cursor.execute("INSERT INTO Doctors (LastName, FirstName, MiddleName, SpecialtyID, Cabinet, WorkPhone) VALUES (?,?,?,?,?,?)",
                       ('Смирнов', 'Алексей', 'Иванович', 2, '205', '555-205'))
        cursor.execute("INSERT INTO Doctors (LastName, FirstName, MiddleName, SpecialtyID, Cabinet, WorkPhone) VALUES (?,?,?,?,?,?)",
                       ('Кузнецова', 'Елена', 'Сергеевна', 3, '310', '555-310'))

        cursor.execute("INSERT INTO Patients (LastName, FirstName, MiddleName, DateOfBirth, Phone, Email, Address) VALUES (?,?,?,?,?,?,?)",
                       ('Иванов', 'Сергей', 'Андреевич', '1985-05-12', '987-654-3210', 'sergey@mail.ru', 'ул. Мира, д.5, кв.12'))
        cursor.execute("INSERT INTO Patients (LastName, FirstName, MiddleName, DateOfBirth, Phone, Email, Address) VALUES (?,?,?,?,?,?,?)",
                       ('Павлова', 'Ольга', 'Николаевна', '1990-08-23', '987-111-2233', 'olga@yandex.ru', 'ул. Ленина, д.10, кв.45'))

        cursor.execute("INSERT INTO Users (Login, PasswordHash, Role, PatientID, DoctorID) VALUES (?,?,?,?,?)",
                       ('admin', 'hash_admin_123', 'Администратор', None, None))
        cursor.execute("INSERT INTO Users (Login, PasswordHash, Role, PatientID, DoctorID) VALUES (?,?,?,?,?)",
                       ('doctor1', 'hash_doctor1_123', 'Врач', None, 1))
        cursor.execute("INSERT INTO Users (Login, PasswordHash, Role, PatientID, DoctorID) VALUES (?,?,?,?,?)",
                       ('doctor2', 'hash_doctor2_123', 'Врач', None, 2))
        cursor.execute("INSERT INTO Users (Login, PasswordHash, Role, PatientID, DoctorID) VALUES (?,?,?,?,?)",
                       ('patient1', 'hash_patient1_123', 'Пациент', 1, None))
        cursor.execute("INSERT INTO Users (Login, PasswordHash, Role, PatientID, DoctorID) VALUES (?,?,?,?,?)",
                       ('patient2', 'hash_patient2_123', 'Пациент', 2, None))

        cursor.execute("INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime, Status, Complaint) VALUES (?,?,?,?,?,?)",
                       (1, 1, '2025-06-10', '09:00', 'Активна', 'Боль в горле, температура'))
        cursor.execute("INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime, Status, Complaint) VALUES (?,?,?,?,?,?)",
                       (2, 2, '2025-06-10', '10:30', 'Активна', 'Консультация перед операцией'))
        cursor.execute("INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime, Status, Complaint) VALUES (?,?,?,?,?,?)",
                       (1, 2, '2025-06-09', '14:00', 'Завершена', 'Головная боль'))
    conn.commit()
    conn.close()


class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Электронная регистратура – Вход")
        self.master.geometry("350x250")
        self.master.resizable(False, False)

        ttk.Label(master, text="Логин:").pack(pady=(20, 0))
        self.login_entry = ttk.Entry(master, width=30)
        self.login_entry.pack(pady=5)

        ttk.Label(master, text="Пароль:").pack()
        self.password_entry = ttk.Entry(master, width=30, show="*")
        self.password_entry.pack(pady=5)

        self.role_var = tk.StringVar(value="Пациент")
        ttk.Label(master, text="Роль:").pack()
        roles = ["Пациент", "Врач", "Администратор"]
        self.role_combo = ttk.Combobox(master, textvariable=self.role_var, values=roles, state="readonly")
        self.role_combo.pack(pady=5)

        ttk.Button(master, text="Войти", command=self.login).pack(pady=15)

    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT UserID, PatientID, DoctorID FROM Users WHERE Login = ? AND PasswordHash = ? AND Role = ? AND IsActive = 1",
                (login, 'hash_' + login + '_123', role)
            )
            row = cursor.fetchone()
            if row:
                self.master.destroy()
                if role == "Пациент":
                    PatientDashboard(row['PatientID'])
                elif role == "Врач":
                    DoctorDashboard(row['DoctorID'])
                else:
                    AdminDashboard()
            else:
                messagebox.showerror("Ошибка", "Неверные учётные данные.")
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))


class PatientDashboard:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.root = tk.Tk()
        self.root.title("Электронная регистратура – Пациент")
        self.root.geometry("800x600")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.booking_frame = ttk.Frame(notebook)
        notebook.add(self.booking_frame, text="Запись на приём")
        self._build_booking_ui()

        self.my_appointments_frame = ttk.Frame(notebook)
        notebook.add(self.my_appointments_frame, text="Мои записи")
        self._build_my_appointments_ui()

    def _build_booking_ui(self):
        filter_frame = ttk.LabelFrame(self.booking_frame, text="Поиск врача")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Специальность:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.spec_combo = ttk.Combobox(filter_frame, state="readonly")
        self.spec_combo.grid(row=0, column=1, padx=5, pady=5)
        self._load_specialties()

        ttk.Label(filter_frame, text="Врач:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.doctor_combo = ttk.Combobox(filter_frame, state="readonly")
        self.doctor_combo.grid(row=0, column=3, padx=5, pady=5)
        self.spec_combo.bind("<<ComboboxSelected>>", self._load_doctors)

        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.date_entry = ttk.Entry(filter_frame, width=15)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(filter_frame, text="Показать расписание", command=self._show_schedule).grid(row=1, column=2, columnspan=2, padx=5, pady=5)

        self.schedule_tree = ttk.Treeview(self.booking_frame, columns=("Врач", "Специальность", "Дата", "Время"), show="headings")
        self.schedule_tree.heading("Врач", text="Врач")
        self.schedule_tree.heading("Специальность", text="Специальность")
        self.schedule_tree.heading("Дата", text="Дата")
        self.schedule_tree.heading("Время", text="Время")
        self.schedule_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(self.booking_frame, text="Записаться", command=self._book_appointment).pack(pady=5)

    def _load_specialties(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SpecialtyID, SpecialtyName FROM Specialties")
        rows = cursor.fetchall()
        self.spec_combo['values'] = [f"{r['SpecialtyID']} - {r['SpecialtyName']}" for r in rows]

    def _load_doctors(self, event=None):
        spec_str = self.spec_combo.get()
        if not spec_str:
            return
        spec_id = int(spec_str.split(" - ")[0])
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DoctorID, LastName || ' ' || FirstName || ' ' || COALESCE(MiddleName,'') FROM Doctors WHERE SpecialtyID = ? AND IsActive = 1",
            (spec_id,)
        )
        rows = cursor.fetchall()
        self.doctor_combo['values'] = [f"{r[0]} - {r[1]}" for r in rows]

    def _show_schedule(self):
        for row in self.schedule_tree.get_children():
            self.schedule_tree.delete(row)

        doctor_str = self.doctor_combo.get()
        try_date = self.date_entry.get().strip()
        if not doctor_str or not try_date:
            return
        doctor_id = int(doctor_str.split(" - ")[0])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT AppointmentTime FROM Appointments WHERE DoctorID = ? AND AppointmentDate = ? AND Status = 'Активна'",
            (doctor_id, try_date)
        )
        busy = {row['AppointmentTime'][:5] for row in cursor.fetchall()}
        slots = [f"{h:02d}:{m:02d}" for h, m in itertools.product(range(8, 18), (0, 30))]
        free = [s for s in slots if s not in busy]
        doctor_name = doctor_str.split(" - ", 1)[1]
        spec_name = self.spec_combo.get().split(" - ", 1)[1]
        for s in free:
            self.schedule_tree.insert("", tk.END, values=(doctor_name, spec_name, try_date, s))

    def _book_appointment(self):
        sel = self.schedule_tree.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Выберите талон.")
            return
        vals = self.schedule_tree.item(sel[0])['values']
        doctor_name = vals[0]
        date_val = vals[2]
        time_val = vals[3]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DoctorID FROM Doctors WHERE LastName || ' ' || FirstName || ' ' || COALESCE(MiddleName,'') = ?",
            (doctor_name,)
        )
        doctor_id = cursor.fetchone()['DoctorID']

        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(
            "SELECT COUNT(*) FROM Appointments WHERE DoctorID = ? AND AppointmentDate = ? AND AppointmentTime = ? AND Status = 'Активна'",
            (doctor_id, date_val, time_val)
        )
        if cursor.fetchone()[0] > 0:
            cursor.execute("ROLLBACK")
            messagebox.showinfo("Информация", "Этот талон только что заняли.")
            return
        cursor.execute(
            "INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime, Status) VALUES (?,?,?,?,'Активна')",
            (doctor_id, self.patient_id, date_val, time_val)
        )
        cursor.execute("COMMIT")
        conn.commit()
        messagebox.showinfo("Успех", "Запись создана!")
        self._show_schedule()

    def _build_my_appointments_ui(self):
        self.my_tree = ttk.Treeview(self.my_appointments_frame, columns=("Врач", "Дата", "Время", "Статус"), show="headings")
        self.my_tree.heading("Врач", text="Врач")
        self.my_tree.heading("Дата", text="Дата")
        self.my_tree.heading("Время", text="Время")
        self.my_tree.heading("Статус", text="Статус")
        self.my_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(self.my_appointments_frame, text="Обновить", command=self._load_my_appointments).pack(pady=5)
        ttk.Button(self.my_appointments_frame, text="Отменить запись", command=self._cancel_appointment).pack(pady=5)

    def _load_my_appointments(self):
        for row in self.my_tree.get_children():
            self.my_tree.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT d.LastName || ' ' || d.FirstName || ' ' || COALESCE(d.MiddleName,''),
                      a.AppointmentDate, a.AppointmentTime, a.Status
               FROM Appointments a JOIN Doctors d ON a.DoctorID = d.DoctorID
               WHERE a.PatientID = ? ORDER BY a.AppointmentDate DESC, a.AppointmentTime""",
            (self.patient_id,)
        )
        for row in cursor.fetchall():
            self.my_tree.insert("", tk.END, values=row)

    def _cancel_appointment(self):
        sel = self.my_tree.selection()
        if not sel:
            return
        vals = self.my_tree.item(sel[0])['values']
        if vals[3] != "Активна":
            messagebox.showwarning("Предупреждение", "Можно отменить только активную запись.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Appointments SET Status = 'Отменена' WHERE PatientID = ? AND AppointmentDate = ? AND AppointmentTime = ? AND Status = 'Активна'",
            (self.patient_id, vals[1], vals[2])
        )
        conn.commit()
        messagebox.showinfo("Успех", "Запись отменена.")
        self._load_my_appointments()


class DoctorDashboard:
    def __init__(self, doctor_id):
        self.doctor_id = doctor_id
        self.root = tk.Tk()
        self.root.title("Электронная регистратура – Врач")
        self.root.geometry("700x500")

        ttk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").pack(pady=(20, 0))
        self.date_entry = ttk.Entry(self.root, width=15)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.pack(pady=5)

        ttk.Button(self.root, text="Показать записи", command=self._load_appointments).pack(pady=5)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Пациент", "Время", "Статус", "Жалоба"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Пациент", text="Пациент")
        self.tree.heading("Время", text="Время")
        self.tree.heading("Статус", text="Статус")
        self.tree.heading("Жалоба", text="Жалоба")
        self.tree.column("ID", width=0, stretch=False)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Явка", command=lambda: self._update_status("Завершена")).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Неявка", command=lambda: self._update_status("Неявка")).grid(row=0, column=1, padx=5)

    def _load_appointments(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT a.AppointmentID, p.LastName || ' ' || p.FirstName || ' ' || COALESCE(p.MiddleName,''), a.AppointmentTime, a.Status, a.Complaint "
            "FROM Appointments a JOIN Patients p ON a.PatientID = p.PatientID "
            "WHERE a.DoctorID = ? AND a.AppointmentDate = ? ORDER BY a.AppointmentTime",
            (self.doctor_id, self.date_entry.get())
        )
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    def _update_status(self, new_status):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Выберите запись.")
            return
        appt_id = self.tree.item(sel[0])['values'][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Appointments SET Status = ? WHERE AppointmentID = ?", (new_status, appt_id))
        conn.commit()
        messagebox.showinfo("Успех", f"Статус изменён на '{new_status}'")
        self._load_appointments()


class AdminDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Электронная регистратура – Администратор")
        self.root.geometry("500x300")
        ttk.Label(self.root, text="Функции администратора (заглушка)\nЗдесь можно добавить управление врачами, пациентами, расписанием и отчётами.").pack(expand=True)


if __name__ == "__main__":
    init_database()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
