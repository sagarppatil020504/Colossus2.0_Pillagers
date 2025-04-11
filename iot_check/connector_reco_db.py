import os
import cv2
import keyboard
import queue
import threading
import time
from datetime import datetime

import face_recog  
import patient_db  
import worker_db    
import firebase_setup

# 🔹 Initialize Firebase
firebase_setup.firebase().fire_main()

# Global task queue (Used for worker_db)
task_queue = queue.Queue()

# 🔹 Face Recognition Function
def face_recognition():
    fr = face_recog.FaceRecog()
    fr.main()
    return fr

# 🔹 Capture and Save Photo Function
def cap_photo(P_id, save_dir="IOT_relational_Database/patient_photos"):
    try:
        os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not access the camera.")
            return None

        print("📸 Press 's' to capture photo...")
        keyboard.wait("s")  # Wait until the user presses 's'
        ret, frame = cap.read()
        if ret:
            file_path = os.path.join(save_dir, f"{P_id}.jpg")
            cv2.imwrite(file_path, frame)
            print(f"✅ Photo saved successfully at {file_path}")
        else:
            print("❌ Error: Could not capture photo.")
            file_path = None

        cap.release()
        return file_path
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# 🔹 Database Worker Thread
def db_worker():
    while True:
        task = task_queue.get()
        if task is None:  # Stop condition
            print("🛑 Worker thread stopping...")
            break
        # Process the task...

# 🔹 Medical Records Connector Class
class MedicalRecordsConnector:
    def __init__(self):
        self.records = patient_db.MedicalRecords()
        self.running = True  # Flag to control loop

        # Start worker thread
        self.worker_thread = threading.Thread(target=db_worker, daemon=True)
        self.worker_thread.start()  

    def main(self):
        while self.running:
            print("\n=== 📁 Patient Database Operations ===")
            print("1️⃣ Add Patient")
            print("2️⃣ Get Patients")
            print("3️⃣ Update Patient")
            print("4️⃣ Delete Patient")
            print("5️⃣ Exit")
            option = input("Enter option (1-5): ").strip()

            if option == '1':
                self.add_patient()

            elif option == '2':
                self.records.get_patients()

            elif option == '3':
                self.update_patient()

            elif option == '4':
                self.delete_patient()

            elif option == '5':
                print("🚪 Exiting...")
                self.running = False  # Stop loop
                break

            else:
                print("⚠️ Invalid option. Please try again.")

        # Gracefully stop worker thread
        task_queue.put(None)
        self.worker_thread.join()

    def add_patient(self):
        pat_name = input("👤 Enter patient name: ").strip()
        add_photo = input("📷 Would you like to add a patient photo? (y/n): ").strip().lower()
        P_id = pat_name[:3] + datetime.now().strftime("%Y%m%d%H%M%S")
        print(f"🆔 Generated Patient ID: {P_id}")

        if add_photo == "y":
            print("📸 Capturing photo...")
            cap_photo(P_id)

        age = input("🔢 Enter age: ").strip()
        medical_cond = input("🩺 Enter medical condition: ").strip()
        Medicines = input("💊 Enter medicines (comma separated): ").strip().split(',')
        time_medicines = input("⏰ Enter time for medicines (comma separated): ").strip().split(',')
        Medicine_taken = input("✅ Is medicine taken? (yes/no): ").strip().lower() == "yes"

        # Add patient record
        self.records.add_patient(P_id, pat_name, age, medical_cond, Medicines, time_medicines, Medicine_taken, "")

    def update_patient(self):
        P_id = input("🆔 Enter patient ID to update: ").strip()
        print("🔄 Enter updated fields (leave blank to keep existing):")

        updated_data = {}
        pat_name = input("👤 New patient name: ").strip()
        if pat_name:
            updated_data["pat_name"] = pat_name

        age = input("🔢 New age: ").strip()
        if age:
            updated_data["age"] = age

        medical_cond = input("🩺 New medical condition: ").strip()
        if medical_cond:
            updated_data["medical_cond"] = medical_cond

        Medicines = input("💊 New medicines (comma separated): ").strip()
        if Medicines:
            updated_data["Medicines"] = [x.strip() for x in Medicines.split(',')]

        time_medicines = input("⏰ New time for medicines (comma separated): ").strip()
        if time_medicines:
            updated_data["time_medicines"] = [x.strip() for x in time_medicines.split(',')]

        Medicine_taken_str = input("✅ Is medicine taken? (yes/no, leave blank to ignore): ").strip().lower()
        if Medicine_taken_str:
            updated_data["Medicine_taken"] = Medicine_taken_str == "yes"

        self.records.update_patient(P_id, updated_data)

    def delete_patient(self):
        P_id = input("🗑️ Enter patient ID to delete: ").strip()
        self.records.delete_patient(P_id)

if __name__ == "__main__":
    MedicalRecordsConnector().main()
