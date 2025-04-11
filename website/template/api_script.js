document.addEventListener("DOMContentLoaded", function () {
    const apiUrl = "http://localhost:5000/patients"; // Replace with your API endpoint

    const patName = document.getElementById("patName");
    const patId = document.getElementById("patId");
    const patAge = document.getElementById("patAge");
    const medCondition = document.getElementById("medCondition");
    const medicinesTaken = document.getElementById("medicinesTaken");
    const timeMedicines = document.getElementById("medicineTimings");
    const medicines = document.getElementById("medicinesToTake");

    const loadingIndicator = document.getElementById("loadingIndicator");
    const patientDetails = document.getElementById("patientDetails");
    const errorMessage = document.getElementById("errorMessage");

    // Retrieve P_id from localStorage
    let patientId = localStorage.getItem("P_id");

    
    if (!patientId || patientId === "null" || patientId === "undefined") {
        console.log("Stored patientId:", patientId, typeof patientId); // Debugging step
        alert("No Patient ID found. Please log in first.");
        window.location.href = "dual_login.html"; // Redirect to login
        return;
    }

    // Ensure patientId is a string
    patientId = patientId.toString().trim();

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            console.log("Fetched Data:", data);

            loadingIndicator.style.display = "none";

            // If data is an array, find the patient
            let patient;
            if (Array.isArray(data)) {
                patient = data.find(p => p.P_id === patientId);
            } else if (typeof data === "object" && data !== null) {
                patient = data[patientId]; // Assumes data is an object with keys as IDs
            }

            if (patient) {
                console.log("Matched Patient Data:", patient);
                patientDetails.style.display = "block";

                // Populate patient details
                patName.textContent = patient.pat_name;
                patId.textContent = patient.P_id;
                patAge.textContent = patient.age;
                medCondition.textContent = patient.medical_cond;
                medicinesTaken.textContent = patient.Medicine_taken ? "Yes" : "No";
                timeMedicines.textContent = patient.time_medicines || "Not Available";
                medicines.textContent = patient.Medicines ? patient.Medicines.join(", ") : "No Medicines";
            } else {
                errorMessage.style.display = "block";
                errorMessage.textContent = "Error: Patient ID not found.";
            }
        })
        .catch(error => {
            loadingIndicator.style.display = "none";
            errorMessage.style.display = "block";
            errorMessage.textContent = "Error fetching patient data. Please try again later.";
            console.error("Fetch error:", error);
        });
});
