// api-client.js - Import this in your patient website frontend

class PatientAPI {
    constructor(baseURL = 'http://localhost:5000/api', authToken = null) {
      this.baseURL = baseURL;
      this.authToken = authToken;
    }
  
    setAuthToken(token) {
      this.authToken = token;
    }
  
    async request(endpoint, method = 'GET', data = null) {
      const url = `${this.baseURL}${endpoint}`;
      
      const headers = {
        'Content-Type': 'application/json',
      };
      
      if (this.authToken) {
        headers['Authorization'] = `Bearer ${this.authToken}`;
      }
      
      const options = {
        method,
        headers,
        credentials: 'include',
      };
      
      if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
      }
      
      try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
          throw new Error(result.message || 'API request failed');
        }
        
        return result;
      } catch (error) {
        console.error('API request error:', error);
        throw error;
      }
    }
    
    // Patient CRUD operations
    async getAllPatients(queryParams = {}) {
      let queryString = '';
      
      if (Object.keys(queryParams).length > 0) {
        queryString = '?' + new URLSearchParams(queryParams).toString();
      }
      
      return this.request(`/patients${queryString}`);
    }
    
    async getPatient(patientId) {
      return this.request(`/patients/${patientId}`);
    }
    
    async createPatient(patientData) {
      return this.request('/patients', 'POST', patientData);
    }
    
    async updatePatient(patientId, patientData) {
      return this.request(`/patients/${patientId}`, 'PUT', patientData);
    }
    
    async deletePatient(patientId) {
      return this.request(`/patients/${patientId}`, 'DELETE');
    }
    
    // Medical records operations
    async getPatientMedicalRecords(patientId) {
      return this.request(`/patients/${patientId}/medical-records`);
    }
    
    async addPatientMedicalRecord(patientId, recordData) {
      return this.request(`/patients/${patientId}/medical-records`, 'POST', recordData);
    }
  }
  
  // Example usage in your patient website
  
  // Initialize API client
  const api = new PatientAPI('AIzaSyDxl02vves6dluwcqKGuKNq9f9Sgkszbb8');
  
  // Set auth token after user login
  api.setAuthToken('user-auth-token');
  
  // Get all patients
  async function loadPatients() {
    try {
      const result = await api.getAllPatients({ limit: 20 });
      console.log('Patients:', result.data);
      return result.data;
    } catch (error) {
      console.error('Failed to load patients:', error);
    }
  }
  
  // Create a new patient
  async function createNewPatient(patientData) {
    try {
      const result = await api.createPatient({
        name: 'John Doe',
        email: 'john@example.com',
        phone: '555-123-4567',
        address: '123 Main St',
        dateOfBirth: '1980-01-01'
      });
      console.log('Created patient:', result.data);
      return result.data;
    } catch (error) {
      console.error('Failed to create patient:', error);
    }
  }
  
  export default PatientAPI;