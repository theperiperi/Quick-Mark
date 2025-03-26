# QuickMark: Attendance System with Dual Authentication

## Introduction

QuickMark is an attendance system designed to streamline the attendance tracking process using dual authentication methods: face recognition and QR codes. The system utilizes Tkinter for the frontend user interface and integrates with a database for efficient attendance maintenance.

## Features

- **Dual Authentication:**
  - Face Recognition: Utilizes facial recognition technology to verify and record attendance.
  - QR Codes: Generates and scans QR codes for an additional layer of authentication.

- **User-Friendly Interface:**
  - Built with Tkinter to provide a simple and intuitive frontend for users.

- **Database Integration:**
  - Stores attendance data in a database for easy maintenance and retrieval.

## Requirements

Ensure you have the following dependencies installed:

```bash
pip install face_recognition opencv-python pyzbar qrcode pillow
```

## Setup and Usage

### 1. Setting up Face Data

1. Create a directory named `classroom` in the root of the repository
2. Add student photos to this directory with the naming format: `student_name.jpg`
3. Run the face data generation script:
   ```bash
   python pickle_and_qr.py
   ```
4. Enter the number of students when prompted
5. For each student, enter their name exactly as it appears in their photo filename
6. The script will:
   - Generate QR codes for each student (saved in `qr_codes/` directory in the repository root)
   - Create a `face_data.pkl` file containing face encodings

### 2. Running the Application

1. Launch the application:
   ```bash
   python main.py
   ```
2. The system will:
   - Open your webcam
   - Scan for QR codes
   - Perform face recognition
   - Mark attendance when both QR code and face match
3. Press 'q' to exit the application

### 3. Viewing Attendance

- Attendance data is automatically stored in `attendance.db`
- Use the UI to view attendance records

## File Structure

- `face_data.pkl`: Stores face recognition data
- `attendance.db`: SQLite database for attendance records
- `qr_codes/`: Directory containing generated QR codes (in repository root)
- `classroom/`: Directory for student photos (in repository root)

## Database Schema

The database contains a table named `attendance` with the following structure:

```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

1. If face recognition fails:
   - Ensure photos are clear and well-lit
   - Check that face is clearly visible in the photo
   - Verify photo naming matches exactly

2. If QR codes don't scan:
   - Ensure good lighting
   - Hold the QR code steady
   - Check that the QR code is not damaged

## Contributions

Contributions are welcome! If you find any issues or want to enhance the functionality, please feel free to create a pull request.

## License

This project is licensed under the MIT License

---

Enjoy using QuickMark! If you have any questions or feedback, feel free to contact me!