import firebase_admin
from firebase_admin import credentials, db
from worker_db import task_queue  # Assuming task_queue is defined in worker_db
from photo_comparator import PhotoComparator
import queue
import ard_connect

# ✅ Prevent multiple initializations
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_json.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://vishwas-patra-default-rtdb.asia-southeast1.firebasedatabase.app/",
        "storageBucket": "vishwas-patra.appspot.com"
    })

class MedicalRecords:
    def __init__(self):
        self.ref = db.reference('/patients')  # Firebase Path
        self.add_task = queue.Queue()  # Initialize a separate queue if needed

    # 🔹 CREATE (Add Patient Record) without photo URL in the record
    def add_patient(self, P_id, pat_name, age, medical_cond, Medicines, time_medicines, Medicine_taken, photo_path):
        def task():
            print(f"🆔 Patient ID: {P_id}, Photo Path: {photo_path}")
            # Use PhotoComparator to process the photo (e.g., capture or verify photo exists)
            # The photo comparator will handle capturing/updating the local photo for the patient,
            # but we will not store its URL in the patient record.
            pc = PhotoComparator()
            pc.process_photo(P_id)  # Process the photo in the local folder

            patient_ref = self.ref.child(P_id)
            if patient_ref.get() is None:  # Ensure unique P_id
                # Create patient record without the "photo" field
                patient_ref.set({
                    "P_id": P_id,
                    "pat_name": pat_name,
                    "age": age,
                    "medical_cond": medical_cond,
                    "Medicines": Medicines,
                    "time_medicines": time_medicines,
                    "Medicine_taken": Medicine_taken,
                })
                print(f"✅ Patient '{pat_name}' added successfully!")
            else:
                print("⚠️ Error: Patient ID must be unique!")
        task_queue.put(task)

    # 🔹 READ (Fetch Patient Records)
    def get_patients(self):
        def task():
            patients = self.ref.get()
            if patients:
                print("\n📋 List of Patients:")
                for key, data in patients.items():
                    print(f"🆔 {data['P_id']} | Name: {data['pat_name']} | Condition: {data['medical_cond']},Medicines:{data['Medicines']},time_medicines:{data['time_medicines']},Medicine_taken:{data['Medicine_taken']}")
            else:
                print("⚠️ No patients found!")
        task_queue.put(task)
        
    # Patient data retrieval function
    def get_patients_withPid(self, P_id):
        result_queue = queue.Queue()

        def task():
            patients = self.ref.get()
            if patients:
                for key, data in patients.items():
                    if data.get('P_id') == P_id:
                        result_queue.put(data)  # Store result in the queue
                        return
            result_queue.put(None)  # No patient found

        task_queue.put(task)
        result = result_queue.get()  # Wait for the task to complete

        if result:
            print("\n📋 Patient Details:")
            print(f"🆔 Patient ID: {result['P_id']}")
            print(f"👤 Name: {result['pat_name']}")
            print(f"🔢 Age: {result.get('age', 'N/A')}")
            print(f"🩺 Condition: {result['medical_cond']}")
            print(f"💊 Medicines: {', '.join(result.get('Medicines', []))}")
            print(f"⏰ Medicine Time: {', '.join(result.get('time_medicines', []))}")
            print(f"✅ Medicine Taken: {'Yes' if result.get('Medicine_taken', False) else 'No'}")

            print("📡 trying to Send info to microcontroller...")
            
            check_con =ard_connect.is_serial_connected()
            if check_con == True:
                print("✅ Arduino connected")
                ard_connect.send_patient_data(
                    result['P_id'], result['pat_name'], result.get('age', 'N/A'),
                    result['medical_cond'], result.get('Medicines', []),
                    result.get('time_medicines', []), result.get('Medicine_taken', False)
                )
            else:
                print("❌ Error: Arduino (COM4) not connected. Please check the connection.")
        else:
            print("⚠️ No patient found with the given ID.")


    # 🔹 UPDATE (Modify Patient Data)
    def update_patient(self, P_id, updated_data):
        def task():
            patient_ref = self.ref.child(P_id)
            if patient_ref.get():
                patient_ref.update(updated_data)
                print(f"✅ Patient '{P_id}' updated successfully!")
            else:
                print("⚠️ Error: Patient ID not found!")
        task_queue.put(task)

    # 🔹 DELETE (Remove a Patient Record)
    def delete_patient(self, P_id):
        def task():
            patient_ref = self.ref.child(P_id)
            if patient_ref.get():
                patient_ref.delete()
                print(f"✅ Patient '{P_id}' deleted successfully!")
            else:
                print("⚠️ Error: Patient ID not found!")
        task_queue.put(task)

# ------------------------ Example Usage ------------------------

# if __name__ == "__main__":
#     # Assume task_queue is processed by worker_db.db_worker() in a separate thread.
#     # This connector code simply adds tasks to the queue.
#     records = MedicalRecords()

#     # Example: Adding a new patient
#     records.get_patients_withPid("sag20250318181345")
    