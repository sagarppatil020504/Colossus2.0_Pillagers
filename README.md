THE CODE BACKEND DOES NOT RUN UNTIL THE JWT TOKEN OF FIREBASE IS SHARED FOR THAT PLS CONTACT ME

AI POWERED SMART PILL  DISPENSER

Case 1: Problem Statement 
Hospitals and clinics face severe overcrowding due to patients seeking basic medications, while public spaces like airports and railway stations lack access to essential medicines, leaving individuals without immediate relief.

Case 2: Problem Statement 
With over 400 million Indians suffering from chronic diseases like diabetes and hypertension, irregular medication adherence leads to worsening health conditions, preventable complications, and increased strain on healthcare systems.

Market Survey

1. Chronic Disease Burden in India:  
101 million diabetics and 315 million with hypertension (ICMR, WHO).  
50% of chronic disease patients miss medications regularly, leading to worsened health outcomes and preventable complications.  

2. Public Space Challenges:  
Airports, railway stations, and other high-traffic areas lack access to essential medications.  
Hospitals and clinics are overcrowded, with long wait times for patients seeking basic medicines.  

3. Existing Solutions:  
Hero Health: Focuses on home-use pill dispensing but lacks public space accessibility and doctor integration.  
ScriptCenter: Pharmacy kiosks for prescription pickups but no real-time prescription updates or AI capabilities.  

Research Gap

No solution combines public space accessibility, AI-powered dispensing, and real-time prescription altering.  
Current systems fail to address medication adherence at scale or provide secure, personalized access in high-traffic areas.  
A gap exists for a solution that bridges immediate medication access in public spaces with chronic disease management in healthcare settings.  

Our USP

Real-Time Prescription Updates by Doctors: Only system where physicians can remotely edit/update prescriptions that instantly sync to the dispenser (no competitors offer live MD-to-machine updates)

Emergency Video Call Button: Direct compliant video consultation integrated into the dispensing unit (absent in all major med-tech competitors)

Closed-Loop Healthcare Ecosystem: Combines facial-recognition dispensing + live adherence tracking + AI triage chatbot + doctor intervention tools (competitors offer isolated features)

AI Triage with Escalation: Chatbot handles basic queries but automatically flags emergencies to doctors (competitors use passive reminder bots)

Doctor-Privileged Access: Secure physician portal with exclusive rights to modify medications in real-time (standard systems require pharmacy re-orders)

Hardware Methodology  

Core Components  

1. Raspberry Pi 5  
   - Handles facial recognition and user authentication.  
   - Acts as the central processing unit for the system.  

2. ESP32 Microcontroller  
   - Manages motor control for precise pill dispensing.  
   - Communicates with Raspberry Pi via Bluetooth.  

3. 28BYJ-48 Stepper Motor  
   - Rotates pill containers to align with the dispensing mechanism.  
   - Ensures accurate selection of medication.  

System Workflow  

1. User Authentication  
   - Facial recognition via Raspberry Pi verifies the user.  

2. Pill Selection  
   - Stepper motor rotates pill containers to the correct position.  

3. Logging and Communication  
   - Sensors log dispensing events, and Bluetooth enables real-time communication between Raspberry Pi and ESP32.  

Why This Design?  

- Modular and Scalable Each component serves a specific purpose, making the system adaptable for future upgrades.  
- Precision and Reliability Combines stepper motors, servos, and sensors for accurate pill delivery.  
- Cost-Effective Uses affordable, off-the-shelf components like Raspberry Pi and ESP32.  

Software Methodology


Global Realtime Database:
Your system leverages a realtime database that is accessible from anywhere in the world. This ensures that all connected platforms—mobile app, website, and Pi application—have synchronized, up-to-date patient data.

Dual Login System:
The website offers a dual login mechanism where patients have their own portal to view personal records, while staff and doctors can log in to add, edit, and manage patient information.


Comprehensive Staff/Doctor Portal:
Staff and doctors can easily add new patient records, update medication details, and manage other patient-related data through the website, streamlining administrative tasks and improving patient care.

Multi-Platform Integration:
The application is designed to run independently on a Raspberry Pi module, offering the same functionalities as the website. This allows for flexible deployment in various environments.

Feature Consistency Across Platforms:
Both the website and the Pi-based application provide a full set of features for patient management, ensuring that no matter which platform is used, users experience consistent functionality and real-time data updates.

Scalability
Case 1: Smart Medication Kiosk -Versatile Deployment in Crowded Spaces

Locations:
Hospitals: Reduces overcrowding by dispensing basic medications outside main facilities.
Airports and Railway Stations: Provides immediate access to essential medications for travelers.
College Campuses: Ensures students have access to medications without visiting a clinic.

How It Works:

Users authenticate via facial recognition
The system dispenses general medications (e.g., painkillers, antacids) or prescription-based pills.
Real-time integration with healthcare systems allows doctors to update prescriptions remotely.

Scalability and Integration:
Can be integrated into pre-existing healthcare models (e.g., hospital networks, telemedicine platforms).

Impact:
Reduces dependency on pharmacies and clinics in high-traffic areas.
Provides 24/7 access to essential medications, improving public health outcomes.

Case  2: Application – Home-Based Pill Dispenser
Personalized Medication Management for Families

Use Case:
Families with elderly members or chronic disease patients often struggle with missed doses and incorrect timings.
This system ensures accurate dosage and timing according to the doctor’s prescription.

How It Works:
Doctors remotely update prescriptions in real-time via a connected platform.
The device dispenses pills at prescribed times and logs each dose for accountability.

Key Features:
Secure access: Only authorized users can operate the device.
Real-time updates: Doctors can adjust prescriptions as needed.

Impact:
Improves medication adherence for elderly and chronic disease patients.
Reduces the burden on caregivers and ensures better health outcomes.



