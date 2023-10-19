import face_recognition
import pickle
import os

# Replace "john.jpg", "jane.jpg", and "alice.jpg" with the actual filenames on your desktop
    
john_image_path = "john.jpg"
jane_image_path = "jane.jpg"
# Load and encode face images for individuals
john_image = face_recognition.load_image_file(john_image_path)
john_face_encoding = face_recognition.face_encodings(john_image)[0]

jane_image = face_recognition.load_image_file(jane_image_path)
jane_face_encoding = face_recognition.face_encodings(jane_image)[0]

# Create a dictionary with face encodings
face_data = {
    "John Doe": john_face_encoding,
    "Jane Smith": jane_face_encoding
}

# Save the face data to a file using pickle
with open('face_data.pkl', 'wb') as f:
    pickle.dump(face_data, f)
