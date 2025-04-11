import cv2
import os

# 🔹 Folder to store patient images
PATIENTS_FOLDER = "IOT_relational_Database/patient_photos"
# records = patient_db.MedicalRecords()

# ✅ Ensure the folder exists
if not os.path.exists(PATIENTS_FOLDER):
    os.makedirs(PATIENTS_FOLDER)


class PhotoComparator:
    def __init__(self):
        """Initialize the photo comparator."""
        self.patient_folder = PATIENTS_FOLDER
        
    def check_photo_exists(self, pid):
        """Check if a photo already exists for the given PID in the local folder."""
        photo_path = os.path.join(self.patient_folder, f"{pid}.jpg")
        return os.path.exists(photo_path), photo_path

    def capture_photo(self, pid):
        """Capture an image using the webcam and save it as PID.jpg."""
        print(f"📷 Capturing image for PID: {pid}...")
        cap = cv2.VideoCapture(0)  # Open the webcam

        if not cap.isOpened():
            print("⚠️ Error: Could not open webcam")
            return None

        ret, frame = cap.read()  # Capture a frame
        cap.release()  # Release the webcam

        if not ret:
            print("⚠️ Error: Failed to capture image")
            return None

        photo_path = os.path.join(self.patient_folder, f"{pid}.jpg")
        cv2.imwrite(photo_path, frame)  # Save the image
        print(f"✅ Image captured and saved: {photo_path}")
        return photo_path

    def process_photo(self, pid):
        """Check for an existing photo and capture one if not found."""
        exists, photo_path = self.check_photo_exists(pid)

        if exists:
            print(f"✅ Photo already exists for PID {pid}: {photo_path}")
            return

        print(f"⚠️ No existing photo found for PID: {pid}. Capturing a new one...")
        self.capture_photo(pid)


# 🔹 Example Usage
if __name__ == "__main__":
    comparator = PhotoComparator()
    patient_id = input("Enter Patient ID: ")
    comparator.process_photo(patient_id)
