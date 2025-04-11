import firebase_admin
from firebase_admin import credentials, db
from worker_db import add_task

# 🔹 Load Firebase Credentials (Ensure the path is correct)
cred = credentials.Certificate("firebase_json.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://vishwas-patra-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

class MedicineManager:
    @staticmethod
    def add_medicine(name, code_name):
        """ Adds a new medicine to Firebase """
        def task():
            ref = db.reference(f'/medicines/{code_name}')
            if ref.get() is None:
                ref.set({"med_code": code_name, "medicine": name})
                print(f"✅ Medicine '{name}' added successfully!")
            else:
                print("⚠️ Error: Medicine code must be unique!")
        
        add_task(task)

    @staticmethod
    def get_medicines():
        """ Fetches all medicines from Firebase """
        def task():
            ref = db.reference('/medicines')
            medicines = ref.get()
            if medicines:
                print("\n📋 List of Medicines:")
                for key, data in medicines.items():
                    print(f"🆔 {data['med_code']} | Name: {data['medicine']}")
            else:
                print("⚠️ No medicines found!")
        
        add_task(task)

    @staticmethod
    def update_medicine(code_name, new_name):
        """ Updates a medicine's name in Firebase """
        def task():
            ref = db.reference(f'/medicines/{code_name}')
            if ref.get():
                ref.update({"medicine": new_name})
                print(f"✅ Medicine '{code_name}' updated successfully!")
            else:
                print("⚠️ Error: Code name not found!")
        
        add_task(task)

    @staticmethod
    def delete_medicine(code_name):
        """ Deletes a medicine entry from Firebase """
        def task():
            ref = db.reference(f'/medicines/{code_name}')
            if ref.get():
                ref.delete()
                print(f"✅ Medicine '{code_name}' deleted successfully!")
            else:
                print("⚠️ Error: Code name not found!")
        
        add_task(task)
