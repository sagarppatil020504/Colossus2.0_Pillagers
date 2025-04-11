import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import queue
import patient_db
import connector_reco_db
import firebase_setup
import ttkbootstrap as tb
from ttkbootstrap import Style
from ttkbootstrap.widgets import Separator

# Initialize Firebase
firebase_setup.firebase().fire_main()

# Global Task Queue
task_queue = queue.Queue()

def process_tasks():
    while not task_queue.empty():
        task = task_queue.get()
        task()
    root.after(100, process_tasks)

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Face Recognition System")
        self.root.geometry("900x650")
        self.style = Style(theme="superhero")
        
        self.running = False
        self.capture = None

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Navigation Bar
        self.navbar = ttk.Frame(self.main_frame, width=200, padding=10, relief="ridge")
        self.navbar.pack(side="left", fill="y")
        
        ttk.Label(self.navbar, text="MENU", font=("Arial", 14, "bold"), anchor="center").pack(pady=10)
        Separator(self.navbar, bootstyle="info").pack(fill="x", pady=5)
        
        self.create_nav_buttons()
        
        # Content Frame
        self.content_frame = ttk.Frame(self.main_frame, padding=20)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Load Home Screen
        self.load_home_screen()

    def create_nav_buttons(self):
        ttk.Button(self.navbar, text="Home", bootstyle="primary-link", command=self.load_home_screen).pack(fill="x", pady=5)
        ttk.Button(self.navbar, text="Monitor Condition", bootstyle="primary-link", command=self.start_face_recognition).pack(fill="x", pady=5)
        ttk.Button(self.navbar, text="Patient Database", bootstyle="primary-link", command=self.manage_patients).pack(fill="x", pady=5)
        ttk.Button(self.navbar, text="Exit", bootstyle="danger-link", command=self.root.quit).pack(fill="x", pady=5)

    def load_home_screen(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Medical Face Recognition System", font=("Arial", 20, "bold")).pack(pady=20)
        ttk.Label(self.content_frame, text="Welcome! Select an option from the menu.", font=("Arial", 12)).pack()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def start_face_recognition(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Face Recognition in Progress...", font=("Arial", 14, "bold")).pack(pady=10)
        connector_reco_db.face_recognition()
        self.video_frame = tk.Label(self.content_frame, borderwidth=3, relief="solid")
        self.video_frame.pack()

        self.running = True
        self.capture = cv2.VideoCapture(0)
        self.show_video()

    def show_video(self):
        if not self.running:
            return
        
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (500, 350))
            img = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.video_frame.img = img
            self.video_frame.config(image=img)
        
        self.root.after(10, self.show_video)

    def manage_patients(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Patient Database Management", font=("Arial", 16, "bold")).pack(pady=10)
        
        frame = ttk.Frame(self.content_frame, padding=10)
        frame.pack()

        ttk.Button(frame, text="Add Patient", bootstyle="info", command=self.add_patient).pack(pady=5)
        ttk.Button(frame, text="Get Patients", bootstyle="info", command=self.get_patients).pack(pady=5)
        ttk.Button(frame, text="Update Patient", bootstyle="info", command=self.update_patient).pack(pady=5)
        ttk.Button(frame, text="Delete Patient", bootstyle="info", command=self.delete_patient).pack(pady=5)

    def add_patient(self):
        form_frame = ttk.Frame(self.add_tab, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Patient Name
        ttk.Label(form_frame, text="👤 Patient Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.pat_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.pat_name_var, width=40).grid(row=0, column=1, sticky="w", pady=5)
        
        # Photo option
        ttk.Label(form_frame, text="📷 Add Patient Photo:").grid(row=1, column=0, sticky="w", pady=5)
        self.add_photo_var = tk.BooleanVar()
        ttk.Checkbutton(form_frame, variable=self.add_photo_var).grid(row=1, column=1, sticky="w", pady=5)
        
        # Photo preview
        self.photo_frame = ttk.LabelFrame(form_frame, text="Photo Preview")
        self.photo_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)
        self.photo_label = ttk.Label(self.photo_frame, text="No photo captured")
        self.photo_label.pack(padx=10, pady=10)
        
        # Capture photo button
        self.capture_btn = ttk.Button(form_frame, text="📸 Capture Photo", command=self.capture_photo)
        self.capture_btn.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Age
        ttk.Label(form_frame, text="🔢 Age:").grid(row=4, column=0, sticky="w", pady=5)
        self.age_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.age_var, width=10).grid(row=4, column=1, sticky="w", pady=5)
        
        # Medical Condition
        ttk.Label(form_frame, text="🩺 Medical Condition:").grid(row=5, column=0, sticky="w", pady=5)
        self.medical_cond_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.medical_cond_var, width=40).grid(row=5, column=1, sticky="w", pady=5)
        
        # Medicines
        ttk.Label(form_frame, text="💊 Medicines (comma separated):").grid(row=6, column=0, sticky="w", pady=5)
        self.medicines_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.medicines_var, width=40).grid(row=6, column=1, sticky="w", pady=5)
        
        # Time for medicines
        ttk.Label(form_frame, text="⏰ Medicine Times (comma separated):").grid(row=7, column=0, sticky="w", pady=5)
        self.time_medicines_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.time_medicines_var, width=40).grid(row=7, column=1, sticky="w", pady=5)
        
        # Medicine taken
        ttk.Label(form_frame, text="✅ Medicine Taken:").grid(row=8, column=0, sticky="w", pady=5)
        self.medicine_taken_var = tk.BooleanVar()
        ttk.Checkbutton(form_frame, variable=self.medicine_taken_var).grid(row=8, column=1, sticky="w", pady=5)
        
        # Submit button
        submit_btn = ttk.Button(form_frame, text="Add Patient", command=self.add_patient)
        submit_btn.grid(row=9, column=0, columnspan=2, pady=20)

    def get_patients(self):
        """Setup the View Patients tab"""
    # Create a frame for the patient list
    def setup_view_tab(self):
        """Setup the View Patients tab"""
        # Create a frame for the patient list
        view_frame = ttk.Frame(self.view_tab, padding="20")
        view_frame.pack(fill="both", expand=True)
        
        # Header
        ttk.Label(view_frame, text="📋 Patient List", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        
        # Create a refresh button
        refresh_btn = ttk.Button(view_frame, text="🔄 Refresh List", command=self.get_patients)
        refresh_btn.grid(row=0, column=1, sticky="e", pady=10)
        
        # Create a frame for the treeview
        tree_frame = ttk.Frame(view_frame)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Configure columns for the treeview
        columns = ("p_id", "name", "condition", "medicines", "time_medicines", "medicine_taken")
        
        # Create the treeview
        self.patients_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.patients_tree.yview)
        
        # Set column headings
        self.patients_tree.heading("p_id", text="🆔 Patient ID")
        self.patients_tree.heading("name", text="👤 Name")
        self.patients_tree.heading("condition", text="🩺 Condition")
        self.patients_tree.heading("medicines", text="💊 Medicines")
        self.patients_tree.heading("time_medicines", text="⏰ Medicine Times")
        self.patients_tree.heading("medicine_taken", text="✅ Taken")
        
        # Set column widths
        self.patients_tree.column("p_id", width=150)
        self.patients_tree.column("name", width=150)
        self.patients_tree.column("condition", width=150)
        self.patients_tree.column("medicines", width=150)
        self.patients_tree.column("time_medicines", width=150)
        self.patients_tree.column("medicine_taken", width=80)
        
        # Pack the treeview
        self.patients_tree.pack(side="left", fill="both", expand=True)
        
        # Status label (for showing messages)
        self.status_label = ttk.Label(view_frame, text="")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)
        
        # Configure grid weights to make the treeview expandable
        view_frame.columnconfigure(0, weight=1)
        view_frame.columnconfigure(1, weight=1)
        view_frame.rowconfigure(1, weight=1)
        
        # Load patients initially
        self.get_patients()

    def get_patients(self):
        """Fetch and display all patients in the treeview"""
        # Clear existing items
        for item in self.patients_tree.get_children():
            self.patients_tree.delete(item)
        
        def update_ui(patients):
            if patients:
                # Add patients to treeview
                for key, data in patients.items():
                    # Format medicines and times as comma-separated strings
                    medicines_str = ", ".join(data.get('Medicines', []))
                    times_str = ", ".join(data.get('time_medicines', []))
                    
                    # Format medicine_taken as Yes/No
                    medicine_taken_str = "Yes" if data.get('Medicine_taken', False) else "No"
                    
                    # Insert into treeview
                    self.patients_tree.insert(
                        "", "end", 
                        values=(
                            data.get('P_id', ''),
                            data.get('pat_name', ''),
                            data.get('medical_cond', ''),
                            medicines_str,
                            times_str,
                            medicine_taken_str
                        )
                    )
                
                # Update status
                self.status_label.config(text=f"Showing {len(patients)} patients")
            else:
                # Show "no patients" message
                self.status_label.config(text="⚠️ No patients found!")
        
        # Get the data (using threading to avoid freezing the UI)
        def fetch_data():
            try:
                # This assumes self.ref.get() returns the patient data
                patients = self.ref.get()
                
                # Schedule UI update on the main thread
                self.root.after(0, lambda: update_ui(patients))
            except Exception as e:
                # Show error in UI
                self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
        
            # Create a new thread for data fetching
            import threading
            thread = threading.Thread(target=fetch_data)
            thread.daemon = True
            thread.start()

            # Add this to the __init__ method of your PatientManagementApp class
            def __init__(self, root, records, ref):
                self.root = root
                self.records = records
                self.ref = ref  # Database reference
                self.root.title("Patient Management System")
                self.root.geometry("900x600")
                
                # Create notebook for tabs
                self.notebook = ttk.Notebook(root)
                self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Create tabs
                self.add_tab = ttk.Frame(self.notebook)
                self.update_tab = ttk.Frame(self.notebook)
                self.delete_tab = ttk.Frame(self.notebook)
                self.view_tab = ttk.Frame(self.notebook)  # Add view tab
                
                self.notebook.add(self.add_tab, text="Add Patient")
                self.notebook.add(self.update_tab, text="Update Patient")
                self.notebook.add(self.delete_tab, text="Delete Patient")
                self.notebook.add(self.view_tab, text="View Patients")  # Add to notebook
                
                # Setup each tab
                self.setup_add_tab()
                self.setup_update_tab()
                self.setup_delete_tab()
                self.setup_view_tab() 
            
    def update_patient(self):
         # Create a frame for form elements with some padding
        form_frame = ttk.Frame(self.update_tab, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Patient ID
        ttk.Label(form_frame, text="🆔 Patient ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.update_pid_var = tk.StringVar()
        pid_entry = ttk.Entry(form_frame, textvariable=self.update_pid_var, width=40)
        pid_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # Find button
        find_btn = ttk.Button(form_frame, text="Find Patient", command=self.find_patient)
        find_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Divider
        ttk.Separator(form_frame, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Update fields
        ttk.Label(form_frame, text="🔄 Enter updated fields (leave blank to keep existing):").grid(row=2, column=0, columnspan=3, sticky="w", pady=5)
        
        # Patient Name
        ttk.Label(form_frame, text="👤 New Patient Name:").grid(row=3, column=0, sticky="w", pady=5)
        self.update_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.update_name_var, width=40).grid(row=3, column=1, sticky="w", pady=5)
        
        # Age
        ttk.Label(form_frame, text="🔢 New Age:").grid(row=4, column=0, sticky="w", pady=5)
        self.update_age_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.update_age_var, width=10).grid(row=4, column=1, sticky="w", pady=5)
        
        # Medical Condition
        ttk.Label(form_frame, text="🩺 New Medical Condition:").grid(row=5, column=0, sticky="w", pady=5)
        self.update_medical_cond_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.update_medical_cond_var, width=40).grid(row=5, column=1, sticky="w", pady=5)
        
        # Medicines
        ttk.Label(form_frame, text="💊 New Medicines (comma separated):").grid(row=6, column=0, sticky="w", pady=5)
        self.update_medicines_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.update_medicines_var, width=40).grid(row=6, column=1, sticky="w", pady=5)
        
        # Time for medicines
        ttk.Label(form_frame, text="⏰ New Medicine Times (comma separated):").grid(row=7, column=0, sticky="w", pady=5)
        self.update_time_medicines_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.update_time_medicines_var, width=40).grid(row=7, column=1, sticky="w", pady=5)
        
        # Medicine taken
        ttk.Label(form_frame, text="✅ Medicine Taken:").grid(row=8, column=0, sticky="w", pady=5)
        self.update_medicine_taken_var = tk.StringVar()
        medicine_taken_combo = ttk.Combobox(form_frame, textvariable=self.update_medicine_taken_var, width=10)
        medicine_taken_combo['values'] = ('', 'yes', 'no')
        medicine_taken_combo.grid(row=8, column=1, sticky="w", pady=5)
        
        # Update button
        update_btn = ttk.Button(form_frame, text="Update Patient", command=self.update_patient)
        update_btn.grid(row=9, column=0, columnspan=3, pady=20)
        
    def delete_patient(self):
        # Create a frame for form elements with some padding
        form_frame = ttk.Frame(self.delete_tab, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Patient ID
        ttk.Label(form_frame, text="🗑️ Patient ID to delete:").grid(row=0, column=0, sticky="w", pady=5)
        self.delete_pid_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.delete_pid_var, width=40).grid(row=0, column=1, sticky="w", pady=5)
        
        # Patient info display
        self.patient_info_frame = ttk.LabelFrame(form_frame, text="Patient Information")
        self.patient_info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        self.patient_info_label = ttk.Label(self.patient_info_frame, text="Enter a patient ID and click 'Find Patient'")
        self.patient_info_label.pack(padx=10, pady=10)
        
        # Find button
        find_btn = ttk.Button(form_frame, text="Find Patient", command=self.find_patient_to_delete)
        find_btn.grid(row=2, column=0, pady=5)
        
        # Delete button
        delete_btn = ttk.Button(form_frame, text="Delete Patient", command=self.delete_patient)
        delete_btn.grid(row=2, column=1, pady=5)
    
if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = MedicalApp(root)
    root.after(100, process_tasks)
    root.mainloop()
