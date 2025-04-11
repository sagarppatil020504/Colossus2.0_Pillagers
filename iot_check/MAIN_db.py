import queue
import connector_reco_db

# Global task queue (if used by worker_db, otherwise remove if not needed)
task_queue = queue.Queue()

def main():
    while True:
        print("Select Mode:")
        print("1. Monitor Condition (Face Recognition)")
        print("2. Staff Work (Patient Database Operations)")
        print("3. Exit")
        choice = input("Enter your choice : ").strip()

        if choice == "1":
            print("Press 'q' to exit")
            connector_reco_db.face_recognition()  # Ensure this is the correct class name in your module
            

        elif choice == "2":
            password = input("Enter password: ").strip()
            if password == "65":
                staff_con = connector_reco_db.MedicalRecordsConnector()
                staff_con.main()
            else:
                print("Wrong password")

        elif choice == "3":
            print("Exiting.")
            break  # ✅ This will now properly exit the loop

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
