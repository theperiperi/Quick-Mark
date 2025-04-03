import cv2
import qrcode
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
import face_recognition
import pickle
import sqlite3
import os
import random
import time
import numpy as np
import mediapipe as mp

class attend:
    def startprocess():
        # Establish a connection to the database (or create a new one if it doesn't exist)
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()

        # Create a table to store attendance data with the correct schema
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Load face recognition data from the file
        pickle_path = os.path.join('pickle_files', 'face_data.pkl')
        if not os.path.exists(pickle_path):
            print(f"Error: Pickle file not found at {pickle_path}")
            return

        with open(pickle_path, 'rb') as f:
            face_data = pickle.load(f)

        # Initialize MediaPipe Face Mesh
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        # Define eye landmarks indices for blink detection
        LEFT_EYE = [362, 385, 387, 263, 373, 380]
        RIGHT_EYE = [33, 160, 158, 133, 153, 144]

        # Challenge prompts for liveness detection
        CHALLENGES = [
            "Please blink your eyes",
            "Please turn your head slightly to the left",
            "Please turn your head slightly to the right",
            "Please nod your head up and down",
        ]

        # Function to calculate eye aspect ratio
        def eye_aspect_ratio(landmarks, eye_indices):
            points = []
            for i in eye_indices:
                points.append([landmarks[i].x, landmarks[i].y])
            
            # Compute the euclidean distances
            A = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
            B = np.linalg.norm(np.array(points[2]) - np.array(points[4]))
            C = np.linalg.norm(np.array(points[0]) - np.array(points[3]))
            
            # Calculate EAR
            ear = (A + B) / (2.0 * C)
            return ear

        # Function to detect head movement
        def detect_head_movement(landmarks, prev_landmarks, threshold=0.02):
            if prev_landmarks is None:
                return "none"
            
            # Calculate movement of nose tip (landmark 1)
            nose_movement_x = landmarks[1].x - prev_landmarks[1].x
            nose_movement_y = landmarks[1].y - prev_landmarks[1].y
            
            if abs(nose_movement_x) > threshold:
                if nose_movement_x > 0:
                    return "right"
                else:
                    return "left"
            elif abs(nose_movement_y) > threshold:
                if nose_movement_y > 0:
                    return "down"
                else:
                    return "up"
            return "none"

        # Function to check depth and detect flat images
        def check_depth(landmarks):
            if not landmarks:
                return False
                
            # A real face has natural depth variation among landmarks
            # Calculate standard deviation of z-coordinates
            z_coords = [landmark.z for landmark in landmarks]
            z_std = np.std(z_coords)
            
            # Threshold for detecting flat surfaces (like printed photos)
            # If std deviation is too low, it's likely a flat image
            return z_std > 0.005
        
        # Function to capture video from webcam, decode QR codes, perform face recognition, and mark attendance
        def mark_attendance():
            # Open the database connection outside the loop
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()

            cap = cv2.VideoCapture(0)
            already_marked = set()  # To prevent duplicate entries
            
            # Variables for challenge-response system
            current_challenge = None
            challenge_start_time = None
            challenge_complete = False
            challenge_timeout = 10  # seconds
            prev_landmarks = None
            blink_counter = 0
            blink_threshold = 0.25
            eye_closed = False
            
            while True:
                _, frame = cap.read()
                # Convert the image to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process the image with MediaPipe Face Mesh
                mesh_results = face_mesh.process(rgb_frame)
                
                # Variables for liveness detection
                depth_check_passed = False
                blink_detected = False
                head_movement = "none"
                
                # If face mesh landmarks are detected
                if mesh_results.multi_face_landmarks:
                    landmarks = mesh_results.multi_face_landmarks[0].landmark
                    
                    # Draw face mesh
                    mp_drawing.draw_landmarks(
                        frame,
                        mesh_results.multi_face_landmarks[0],
                        mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
                    )
                    
                    # Check depth to detect flat surfaces (printed photos)
                    depth_check_passed = check_depth(landmarks)
                    
                    # Calculate eye aspect ratio for blink detection
                    left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
                    right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
                    ear = (left_ear + right_ear) / 2.0
                    
                    # Detect blink
                    if ear < blink_threshold and not eye_closed:
                        eye_closed = True
                    elif ear >= blink_threshold and eye_closed:
                        eye_closed = False
                        blink_counter += 1
                        blink_detected = True
                    
                    # Detect head movement
                    if prev_landmarks:
                        head_movement = detect_head_movement(landmarks, prev_landmarks)
                    prev_landmarks = landmarks
                    
                    # Handle challenge-response system
                    if current_challenge is None:
                        current_challenge = random.choice(CHALLENGES)
                        challenge_start_time = time.time()
                        challenge_complete = False
                    elif not challenge_complete:
                        # Check if challenge is completed based on the type
                        if "blink" in current_challenge and blink_detected:
                            challenge_complete = True
                        elif "left" in current_challenge and head_movement == "left":
                            challenge_complete = True
                        elif "right" in current_challenge and head_movement == "right":
                            challenge_complete = True
                        elif "nod" in current_challenge and head_movement in ["up", "down"]:
                            challenge_complete = True
                        
                        # Check for timeout
                        if time.time() - challenge_start_time > challenge_timeout:
                            current_challenge = random.choice(CHALLENGES)
                            challenge_start_time = time.time()
                    
                    # Display the current challenge
                    cv2.putText(frame, current_challenge, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # Display liveness indicators
                    cv2.putText(frame, f"Depth Check: {'Passed' if depth_check_passed else 'Failed'}", (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if depth_check_passed else (0, 0, 255), 2)
                    cv2.putText(frame, f"Blinks: {blink_counter}", (10, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    cv2.putText(frame, f"Movement: {head_movement}", (10, 120), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                
                # Decode QR codes
                decoded_objects = decode(frame, symbols=[ZBarSymbol.QRCODE])
                
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8') if obj.data else None
                    if qr_data and qr_data not in already_marked and qr_data in face_data:
                        face_locations = face_recognition.face_locations(frame)
                        face_encodings = face_recognition.face_encodings(frame, face_locations)

                        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                            # Compare the face encoding with known face encodings
                            matches = face_recognition.compare_faces([face_data[qr_data]], face_encoding)
                            name = "Unknown"

                            if matches[0]:
                                # Only mark attendance if liveness checks pass
                                if depth_check_passed and challenge_complete:
                                    name = qr_data
                                    print(f"Attendance marked for: {name}")
                                    already_marked.add(qr_data)

                                    # Store attendance data in the database
                                    c.execute("INSERT INTO attendance (name) VALUES (?)", (name,))
                                    conn.commit()  # Commit the changes
                                else:
                                    name = f"{qr_data} (SPOOFING DETECTED)"
                                    print(f"Spoofing attempt detected for: {qr_data}")

                            # Draw a rectangle and label around the face
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

                cv2.imshow("Attendance System", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
                    break

            # Close the connection after the loop ends
            conn.close()

            cap.release()
            cv2.destroyAllWindows()

        # Call the mark_attendance function
        mark_attendance()

# Run the attendance system when the script is executed
if __name__ == "__main__":
    attend.startprocess()