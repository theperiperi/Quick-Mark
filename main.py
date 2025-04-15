import cv2
import face_recognition
import pickle
import os
import numpy as np
import mediapipe as mp
import time
import tkinter as tk
from supabase import create_client, Client
from dotenv import load_dotenv
from ui import QuickMarkUI

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def preprocess_image(frame):
    """Preprocess frame for better face detection."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    contrast_frame = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    blurred_frame = cv2.GaussianBlur(contrast_frame, (3, 3), 0)
    resized_frame = cv2.resize(blurred_frame, (640, 480))
    return resized_frame, cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

class AttendanceSystem:
    def __init__(self):
        # Initialize Supabase tables
        self.init_supabase()
        # Create a unique session
        self.session_id = f"session_{int(time.time())}"
        self.create_session(self.session_id, "Auto-generated Session")
        
        # Load face data
        self.face_data = self.load_face_data()
        if not self.face_data:
            raise Exception("Failed to load face data")

        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks for reference (not used directly but kept for compatibility)
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]

        # Challenges for liveness detection
        self.required_actions = ["left", "right", "nod"]

        # Initialize variables for liveness detection as instance variables
        self.already_marked = set()
        self.current_person = None
        self.completed_actions = set()
        self.current_action = None
        self.action_start_time = None
        self.action_complete = False
        self.action_timeout = 60  # Overall timeout for all actions
        self.prev_landmarks = None
        self.movement_complete_time = None
        self.movement_complete_duration = 6.0  # Time for each gesture
        self.movement_buffer = []
        self.buffer_size = 5
        self.last_action_time = 0
        self.action_cooldown = 6.0  # Cooldown between gestures (6 seconds)
        self.attendance_just_marked = False  # Flag to stop instructions after marking
        self.last_detected_time = time.time()  # Initialize last detected time

    def init_supabase(self):
        """Ensure Supabase tables exist."""
        try:
            supabase.table('students').select('id').limit(1).execute()
            supabase.table('sessions').select('id').limit(1).execute()
            supabase.table('attendance').select('id').limit(1).execute()
        except Exception:
            print("Creating Supabase tables. Ensure you have these tables set up:")
            print("""
            CREATE TABLE students (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                image_path TEXT
            );
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                end_time TIMESTAMP WITH TIME ZONE
            );
            CREATE TABLE attendance (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES students(id),
                session_id TEXT REFERENCES sessions(id),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                confidence_score REAL
            );
            """)
            print("Please create these tables in your Supabase dashboard.")
            exit(1)

    def load_face_data(self):
        """Load face encodings from pickle file."""
        pickle_path = os.path.join('pickle_files', 'face_data.pkl')
        if not os.path.exists(pickle_path):
            print(f"Error: Face data file not found at {pickle_path}")
            return None
        with open(pickle_path, 'rb') as f:
            return pickle.load(f)

    def detect_head_movement(self, landmarks, prev_landmarks, threshold=0.01):
        """Detect specific head movements for liveness."""
        if prev_landmarks is None:
            return "none"
        
        stable_landmarks = [1, 152, 33, 133]  # Nose tip, chin, eye corners
        total_movement_x = 0
        total_movement_y = 0
        
        for landmark_idx in stable_landmarks:
            total_movement_x += landmarks[landmark_idx].x - prev_landmarks[landmark_idx].x
            total_movement_y += landmarks[landmark_idx].y - prev_landmarks[landmark_idx].y
        
        avg_movement_x = total_movement_x / len(stable_landmarks)
        avg_movement_y = total_movement_y / len(stable_landmarks)
        min_movement_threshold = 0.003
        
        if abs(avg_movement_x) > threshold and abs(avg_movement_x) > min_movement_threshold:
            return "right" if avg_movement_x > 0 else "left"
        elif abs(avg_movement_y) > threshold and abs(avg_movement_y) > min_movement_threshold:
            return "down" if avg_movement_y > 0 else "up"
        return "none"

    def check_depth(self, landmarks):
        """Check depth to detect flat images."""
        if not landmarks:
            return False
        z_coords = [landmark.z for landmark in landmarks]
        z_std = np.std(z_coords)
        return z_std > 0.005

    def create_session(self, session_id, session_name):
        """Create a session in Supabase."""
        try:
            supabase.table('sessions').insert({
                'id': session_id,
                'name': session_name
            }).execute()
        except Exception as e:
            print(f"Error creating session: {str(e)}")

    def mark_attendance(self, student_name, session_id, confidence_score):
        """Record attendance in Supabase."""
        try:
            student = supabase.table('students').select('id').eq('name', student_name).execute()
            if not student.data:
                supabase.table('students').insert({'name': student_name}).execute()
                student = supabase.table('students').select('id').eq('name', student_name).execute()
            
            student_id = student.data[0]['id']
            supabase.table('attendance').insert({
                'student_id': student_id,
                'session_id': session_id,
                'confidence_score': confidence_score
            }).execute()
            print(f"Attendance marked for {student_name} (Confidence: {confidence_score:.2f})")
        except Exception as e:
            print(f"Error marking attendance: {str(e)}")

    def run(self):
        """Run the attendance system with Tkinter UI."""
        # Initialize Tkinter
        root = tk.Tk()
        ui = QuickMarkUI(root, self.on_closing)

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            root.destroy()
            return
        self.running = True

        def update_frame():
            if not self.running:
                return

            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture frame from webcam.")
                self.running = False
                self.cap.release()
                root.destroy()
                return

            # Preprocess the frame
            preprocessed_frame, rgb_frame = preprocess_image(frame)

            # Reset variables if no person is detected for a while
            if self.current_person and face_recognition.face_locations(rgb_frame):
                self.last_detected_time = time.time()
            elif self.current_person and (time.time() - self.last_detected_time > 5):
                self.current_person = None
                self.completed_actions = set()
                self.current_action = None
                self.action_start_time = None
                self.movement_buffer = []
                self.last_action_time = 0
                self.attendance_just_marked = False

            # Liveness detection
            mesh_results = self.face_mesh.process(rgb_frame)
            head_movement = "none"
            instruction = "Please position your face"

            if mesh_results.multi_face_landmarks:
                landmarks = mesh_results.multi_face_landmarks[0].landmark
                if not self.check_depth(landmarks):
                    instruction = "Possible flat image detected"
                else:
                    if self.prev_landmarks:
                        head_movement = self.detect_head_movement(landmarks, self.prev_landmarks)
                        current_time = time.time()
                        if current_time - self.last_action_time >= self.action_cooldown:
                            if head_movement != "none":
                                self.movement_buffer.append(head_movement)
                                if len(self.movement_buffer) > self.buffer_size:
                                    self.movement_buffer.pop(0)

                            if self.movement_buffer and self.current_action:
                                if (self.current_action == "left" and "left" in self.movement_buffer) or \
                                   (self.current_action == "right" and "right" in self.movement_buffer) or \
                                   (self.current_action == "nod" and ("up" in self.movement_buffer or "down" in self.movement_buffer)):
                                    self.movement_complete_time = current_time
                                    self.action_complete = True

                            if self.movement_complete_time and (current_time - self.movement_complete_time) < self.movement_complete_duration:
                                self.action_complete = True
                            else:
                                self.movement_complete_time = None

                    self.prev_landmarks = landmarks

                    if self.action_complete and self.current_action:
                        self.completed_actions.add(self.current_action)
                        self.action_complete = False
                        self.current_action = None
                        self.movement_buffer = []
                        self.last_action_time = time.time()
                        print(f"Action completed. Total completed: {len(self.completed_actions)}/3")

                    # Only proceed with actions if attendance hasn't just been marked
                    if not self.attendance_just_marked:
                        if not self.current_action and len(self.completed_actions) < len(self.required_actions):
                            remaining_actions = [a for a in self.required_actions if a not in self.completed_actions]
                            if remaining_actions:
                                self.current_action = remaining_actions[0]
                                self.action_start_time = time.time()
                                print(f"New action: {self.current_action}")

                        if self.current_action and time.time() - self.action_start_time > self.action_timeout:
                            print(f"Action timeout: {self.current_action}")
                            self.current_action = None
                            self.action_start_time = None
                            self.movement_buffer = []

                        # Update instructions based on current action
                        if self.current_action:
                            time_since_action_start = time.time() - self.action_start_time
                            if time_since_action_start <= self.action_cooldown:
                                instruction = f"Turn head {self.current_action} (Time left: {max(0, self.action_cooldown - time_since_action_start):.1f}s)"
                            else:
                                instruction = f"Turn head {self.current_action}"
                        else:
                            instruction = "Performing liveness check..."
                    else:
                        instruction = "Attendance marked. Waiting for next person..."

            # Face recognition
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            name = "Unknown"
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(list(self.face_data.values()), face_encoding)
                face_distances = face_recognition.face_distance(list(self.face_data.values()), face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                    name = list(self.face_data.keys())[best_match_index]
                    confidence = 1.0 - face_distances[best_match_index]

                    if self.current_person is None or self.current_person == name:
                        self.current_person = name
                        if len(self.completed_actions) == len(self.required_actions):
                            if name not in self.already_marked:
                                self.mark_attendance(name, self.session_id, confidence)
                                self.already_marked.add(name)
                                self.attendance_just_marked = True  # Set flag to stop instructions
                            self.current_person = None
                            self.completed_actions = set()
                            self.current_action = None
                            self.action_start_time = None
                            self.movement_buffer = []
                            self.last_action_time = 0
                        elif name in self.already_marked:
                            name = f"{name} (Already Marked)"
                            self.attendance_just_marked = True  # Stop instructions if already marked
                        else:
                            name = f"{name} (Complete Actions)"

                # Draw rectangle and name on the frame
                cv2.rectangle(preprocessed_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(preprocessed_frame, name, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Update UI elements
            ui.update_frame(preprocessed_frame)
            ui.update_instructions(instruction)
            ui.update_name(name)
            ui.update_actions(len(self.completed_actions), len(self.required_actions))

            # Schedule the next frame update with a slightly longer delay to prevent freezing
            root.after(30, update_frame)

        # Start the frame update loop
        update_frame()
        # Run the Tkinter main loop
        ui.run()

    def on_closing(self):
        """Handle UI closing."""
        self.running = False
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()

if __name__ == "__main__":
    try:
        system = AttendanceSystem()
        system.run()
    except Exception as e:
        print(f"Error starting system: {str(e)}")