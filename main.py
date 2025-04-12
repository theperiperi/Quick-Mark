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
        def detect_head_movement(landmarks, prev_landmarks, threshold=0.01):  # Lowered threshold
            if prev_landmarks is None:
                return "none"
            
            # Use multiple stable facial landmarks for more robust movement detection
            # Nose tip (1), chin (152), left eye corner (33), right eye corner (133)
            stable_landmarks = [1, 152, 33, 133]
            
            # Calculate average movement across multiple landmarks
            total_movement_x = 0
            total_movement_y = 0
            
            for landmark_idx in stable_landmarks:
                total_movement_x += landmarks[landmark_idx].x - prev_landmarks[landmark_idx].x
                total_movement_y += landmarks[landmark_idx].y - prev_landmarks[landmark_idx].y
            
            # Average the movements
            avg_movement_x = total_movement_x / len(stable_landmarks)
            avg_movement_y = total_movement_y / len(stable_landmarks)
            
            # Apply a minimum movement threshold to reduce false positives
            min_movement_threshold = 0.003  # Lowered minimum threshold
            
            # Detect horizontal movement
            if abs(avg_movement_x) > threshold and abs(avg_movement_x) > min_movement_threshold:
                if avg_movement_x > 0:
                    return "right"
                else:
                    return "left"
            # Detect vertical movement
            elif abs(avg_movement_y) > threshold and abs(avg_movement_y) > min_movement_threshold:
                if avg_movement_y > 0:
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
            current_person = None
            required_actions = ["left", "right", "nod"]  # Three required actions
            completed_actions = set()
            current_action = None
            action_start_time = None
            action_complete = False
            action_timeout = 10  # seconds
            prev_landmarks = None
            movement_complete_time = None
            movement_complete_duration = 2.0
            movement_buffer = []
            buffer_size = 5
            last_action_time = 0
            action_cooldown = 2.0  # seconds between actions
            
            while True:
                _, frame = cap.read()
                # Convert the image to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process the image with MediaPipe Face Mesh
                mesh_results = face_mesh.process(rgb_frame)
                
                # Variables for liveness detection
                head_movement = "none"
                
                # If face mesh landmarks are detected
                if mesh_results.multi_face_landmarks:
                    landmarks = mesh_results.multi_face_landmarks[0].landmark
                    
                    # Detect head movement
                    if prev_landmarks:
                        head_movement = detect_head_movement(landmarks, prev_landmarks)
                        
                        # Only process movement if enough time has passed since last action
                        current_time = time.time()
                        if current_time - last_action_time >= action_cooldown:
                            # Update movement buffer
                            if head_movement != "none":
                                movement_buffer.append(head_movement)
                                if len(movement_buffer) > buffer_size:
                                    movement_buffer.pop(0)
                            
                            # Check if any recent movement matches the current action
                            if movement_buffer and current_action:
                                if (current_action == "left" and "left" in movement_buffer) or \
                                   (current_action == "right" and "right" in movement_buffer) or \
                                   (current_action == "nod" and ("up" in movement_buffer or "down" in movement_buffer)):
                                    movement_complete_time = time.time()
                                    action_complete = True
                            
                            # Keep the movement state active for the duration
                            if movement_complete_time and (time.time() - movement_complete_time) < movement_complete_duration:
                                action_complete = True
                            else:
                                movement_complete_time = None
                                
                    prev_landmarks = landmarks
                    
                    # Handle action completion
                    if action_complete and current_action:
                        completed_actions.add(current_action)
                        action_complete = False
                        current_action = None
                        movement_buffer = []  # Clear buffer after action completion
                        last_action_time = time.time()  # Update last action time
                        print(f"Action completed. Total completed: {len(completed_actions)}/3")
                    
                    # Get next action if current one is complete or not set
                    if not current_action and len(completed_actions) < len(required_actions):
                        remaining_actions = [a for a in required_actions if a not in completed_actions]
                        if remaining_actions:
                            current_action = remaining_actions[0]
                            action_start_time = time.time()
                            print(f"New action: {current_action}")
                    
                    # Check for action timeout
                    if current_action and time.time() - action_start_time > action_timeout:
                        print(f"Action timeout: {current_action}")
                        current_action = None
                        action_start_time = None
                        movement_buffer = []
                    
                    # Display current status
                    if current_person:
                        cv2.putText(frame, f"Identified: {current_person}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Completed Actions: {len(completed_actions)}/3", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        if current_action:
                            cv2.putText(frame, f"Current Action: Turn head {current_action}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            # Show cooldown timer
                            time_left = max(0, action_cooldown - (time.time() - last_action_time))
                            if time_left > 0:
                                cv2.putText(frame, f"Next action in: {time_left:.1f}s", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    else:
                        cv2.putText(frame, "Please position your face for identification", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    cv2.putText(frame, f"Movement: {head_movement}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                    # Perform face recognition
                    face_locations = face_recognition.face_locations(rgb_frame)
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        # Compare with all known faces
                        matches = face_recognition.compare_faces(list(face_data.values()), face_encoding)
                        name = "Unknown"
                        face_distances = face_recognition.face_distance(list(face_data.values()), face_encoding)
                        best_match_index = np.argmin(face_distances)

                        if matches[best_match_index] and face_distances[best_match_index] < 0.6:  # More strict matching
                            name = list(face_data.keys())[best_match_index]
                            
                            # If we haven't identified a person yet or if it's the same person
                            if current_person is None or current_person == name:
                                current_person = name
                                
                                # If all actions are completed, mark attendance
                                if len(completed_actions) == len(required_actions) and name not in already_marked:
                                    print(f"Attendance marked for: {name}")
                                    already_marked.add(name)
                                    c.execute("INSERT INTO attendance (name) VALUES (?)", (name,))
                                    conn.commit()
                                    # Reset for next person
                                    current_person = None
                                    completed_actions = set()
                            elif name in already_marked:
                                name = f"{name} (Already Marked)"
                            else:
                                name = f"{name} (Complete Actions)"

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