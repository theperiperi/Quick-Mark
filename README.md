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

- **Anti-Spoofing Technology:**
  - Eye Blink Detection: Ensures the person is real by detecting natural eye blinking.
  - Head Movement Detection: Verifies liveness through random head movement challenges.
  - Depth Estimation: Uses MediaPipe to detect flat surfaces like printed photos.
  - Challenge-Response System: Randomized prompts requiring specific actions to verify presence.

## Requirements

Ensure you have the following dependencies installed:

```bash
pip install face_recognition opencv-python pyzbar qrcode pillow mediapipe numpy
```

Alternatively, install all requirements:
```bash
pip install -r requirements.txt
```

## Setup and Usage

### 1. Setting up Face Data

1. Run register_face.py to capture image of student
2. Run create_face_data.py:
3. Enter the name of student exactly as it appears in their photo filename
4. The script will:
   - Create image encodings using face_recognition module
   - Store it in `face_data.pkl` file 

### 2. Running the Application

1. Launch the application:
   ```bash
   python main.py
   ```
2. The system will:
   - Open your webcam
   - Present random liveness challenges (blink, turn head, etc.)
   - Analyze facial depth to detect spoofing attempts
   - Perform face recognition
   - Mark attendance only when all verification steps pass
3. Press 'q' to exit the application

### 3. Viewing Attendance

- Attendance data is automatically stored in `attendance.db`
- Use the UI to view attendance records

## File Structure

- `face_data.pkl`: Stores face recognition data
- `attendance.db`: SQLite database for attendance records
- `classroom/`: Directory for student photos (in repository root)

## Troubleshooting

1. If face recognition fails:
   - Ensure photos are clear and well-lit
   - Check that face is clearly visible in the photo
   - Verify photo naming matches exactly

2. If anti-spoofing checks fail:
   - Make sure there's sufficient lighting for depth detection
   - Follow the challenge instructions carefully
   - Ensure your face is clearly visible to the camera
   - Avoid quick movements that may interfere with tracking

## Contributions

Contributions are welcome! If you find any issues or want to enhance the functionality, please feel free to create a pull request.

## License

This project is licensed under the MIT License

---

Enjoy using QuickMark! If you have any questions or feedback, feel free to contact me!
