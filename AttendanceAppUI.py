import tkinter as tk
from tkinter import messagebox
from minimain import attendance
from mininew import image_sample
from minisho import db_show
from minipickle import pickle

class AttendanceAppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System")

        self.generate_qr_button = tk.Button(root, text="Generate QR Codes", command=self.generate_qr_codes)
        self.generate_qr_button.pack(pady=10)

        self.mark_attendance_button = tk.Button(root, text="Mark Attendance", command=self.mark_attendance)
        self.mark_attendance_button.pack(pady=10)

        self.view_db_button = tk.Button(root, text="View Database", command=self.view_db)
        self.view_db_button.pack(pady=10)

        self.image_sample_button = tk.Button(root, text="Image Sample", command=self.image_sample)
        self.image_sample_button.pack(pady=10)

    def generate_qr_codes(self):
        attendees = ["John Doe", "Jane Smith", "Alice Johnson"]
        for attendee in attendees:
            attendance.generate_qr_code(attendee, f"{attendee.replace(' ', '_')}.png")
        messagebox.showinfo("Success", "QR Codes generated successfully.")

    def mark_attendance(self):
        try:
            attendance.mark_attendance()
            messagebox.showinfo("Success", "Attendance marked successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def view_db(self):
        try:
            db_show.view_db()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def image_sample(self):
        try:
            image_sample()
            messagebox.showinfo("Success", "Image data has been saved to pickle file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceAppUI(root)
    root.mainloop()

