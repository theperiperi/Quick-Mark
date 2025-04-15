import face_recognition
import pickle
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class FaceDataCreator:
    @staticmethod
    def create_face_data():
        """Generate face encodings and update Supabase."""
        os.makedirs('pickle_files', exist_ok=True)
        os.makedirs('classroom', exist_ok=True)

        face_data = {}
        num_students = int(input("Enter number of students: "))
        
        for i in range(num_students):
            name = input(f"Enter name of student {i+1}: ").strip()
            image_path = os.path.join("classroom", f"{name}.jpg")

            if not os.path.exists(image_path):
                print(f"Error: Image not found at {image_path}")
                print("Please add the image and try again")
                continue

            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if not encodings:
                    print(f"No faces found in {image_path}")
                    continue
                    
                face_data[name] = encodings[0]
                
                # Add or update student in Supabase
                existing_student = supabase.table('students').select('id').eq('name', name).execute()
                if not existing_student.data:
                    supabase.table('students').insert({
                        'name': name,
                        'image_path': image_path
                    }).execute()
                else:
                    supabase.table('students').update({
                        'image_path': image_path
                    }).eq('name', name).execute()
                
                print(f"Successfully added {name}")
            except Exception as e:
                print(f"Error processing {name}: {str(e)}")
                continue

        # Save face encodings
        pickle_path = os.path.join('pickle_files', 'face_data.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(face_data, f)
        
        print(f"\nFace data saved for {len(face_data)} students")
        print(f"Database updated with student records")

if __name__ == "__main__":
    FaceDataCreator.create_face_data()