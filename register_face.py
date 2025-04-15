import cv2
import os
import face_recognition
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def capture_face():
    """Capture a student's face and register it in Supabase."""
    # Create classroom directory
    os.makedirs('classroom', exist_ok=True)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    print("\nFace Registration Process")
    print("-----------------------")
    name = input("Enter your full name: ").strip()
    
    # Check if name already exists
    image_path = os.path.join("classroom", f"{name}.jpg")
    existing_student = supabase.table('students').select('id').eq('name', name).execute()
    if existing_student.data:
        print(f"\n{name} already exists in the system!")
        print("Please use a different name or update the existing record.")
        cap.release()
        return

    print("\nInstructions:")
    print("1. Face the camera directly")
    print("2. Ensure good lighting")
    print("3. Keep a neutral expression")
    print("\nPress 's' to capture your photo or 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error capturing frame")
            break
        
        cv2.imshow('Face Registration - Press "s" to capture', frame)
        
        key = cv2.waitKey(1)
        if key == ord('s'):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            if not face_locations:
                print("No face detected! Please try again.")
                continue
            
            cv2.imwrite(image_path, frame)
            print(f"\nPhoto saved successfully as {image_path}")
            
            # Add to Supabase
            try:
                supabase.table('students').insert({
                    'name': name,
                    'image_path': image_path
                }).execute()
                print(f"Student '{name}' added to database")
            except Exception as e:
                print(f"Error adding student to database: {str(e)}")
                os.remove(image_path)  # Clean up if database fails
            break
            
        elif key == ord('q'):
            print("\nRegistration cancelled")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_face()