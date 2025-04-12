import express from "express";
import cors from "cors";
import fetch from "node-fetch";

// Express instance for patients
const patientsApp = express();
patientsApp.use(cors());

const FIREBASE_PATIENTS_URL = "https://vishwas-patra-default-rtdb.asia-southeast1.firebasedatabase.app/patients.json";

patientsApp.get("/patients", async (req, res) => {
    try {
        const response = await fetch(FIREBASE_PATIENTS_URL);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error("Error fetching patients data:", error);
        res.status(500).json({ error: "Error fetching patients data" });
    }
});

// Express instance for staff login
const staffApp = express();
staffApp.use(cors());

const FIREBASE_STAFF_URL = "https://vishwas-patra-default-rtdb.asia-southeast1.firebasedatabase.app/staff_login.json";

staffApp.get("/staff_login", async (req, res) => {
    try {
        const response = await fetch(FIREBASE_STAFF_URL);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error("Error fetching staff data:", error);
        res.status(500).json({ error: "Error fetching staff data" });
    }
});

const PATIENTS_PORT = 5000;
const STAFF_PORT = 5001;

patientsApp.listen(PATIENTS_PORT, () => console.log(`Patients proxy server running on http://localhost:${PATIENTS_PORT}/patients`));
staffApp.listen(STAFF_PORT, () => console.log(`Staff proxy server running on http://localhost:${STAFF_PORT}/staff_login`));
