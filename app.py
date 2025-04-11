# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from functools import wraps
import uuid
from datetime import datetime
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Firebase initialization
# If using environment variables (recommended for production)
# cred = credentials.Certificate(json.loads(os.environ.get('FIREBASE_CREDENTIALS')))

# For local development or testing, use a service account file
cred = credentials.Certificate('vishwas-patra-firebase-adminsdk-lbb9f-e67ac71793.json')
firebase_admin.initialize_app(cred)

FIREBASE_URL = "https://vishwas-patra-default-rtdb.asia-southeast1.firebasedatabase.app"

# Get Firestore client
db = firestore.client()

# Collection reference
patients_ref = db.collection('patients')

# Authentication middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in the headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        # In a real app, verify the token with Firebase Auth
        # For now, we'll use a simple check
        # TODO: Implement proper Firebase token verification
        try:
            # Verify token logic would go here
            # Example:
            # decoded_token = auth.verify_id_token(token)
            pass
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(*args, **kwargs)
    
    return decorated

# Helper function for standardized responses
def response_with_data(data, message="Success", status_code=200):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), status_code

def error_response(message, status_code=400):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code

# Routes
@app.route('/api/patients', methods=['GET'])
@token_required
def get_all_patients():
    try:
        # Optional query parameters
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Get all patients with pagination
        patients = []
        query = patients_ref.limit(limit).offset(offset)
        
        # Handle optional filters
        if 'name' in request.args:
            query = query.where('name', '>=', request.args.get('name'))
            query = query.where('name', '<=', request.args.get('name') + '\uf8ff')
        
        docs = query.stream()
        
        for doc in docs:
            patient_data = doc.to_dict()
            patient_data['P_id'] = doc.id
            patients.append(patient_data)
            
        return response_with_data(patients, f"Successfully retrieved {len(patients)} patients")
    except Exception as e:
        return error_response(f"Failed to fetch api call patients: {str(e)}", 500)

@app.route(f'/api/patients/<P_id>', methods=['GET'])
@token_required
def get_patient(patient_id):
    try:
        doc = patients_ref.document(patient_id).get()
        
        if not doc.exists:
            return error_response("Patient not found", 404)
            
        patient_data = doc.to_dict()
        patient_data['id'] = doc.id
        
        return response_with_data(patient_data, "Patient retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to fetch patient: {str(e)}", 500)

@app.route('/api/patients', methods=['POST'])
@token_required
def create_patient():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Add created timestamp
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        
        # Create new patient with auto ID
        new_patient_ref = patients_ref.document()
        new_patient_ref.set(data)
        
        # Return the created patient data with ID
        result = data.copy()
        result['id'] = new_patient_ref.id
        
        return response_with_data(result, "Patient created successfully", 201)
    except Exception as e:
        return error_response(f"Failed to create patient: {str(e)}", 500)

@app.route('/api/patients/<P_id>', methods=['PUT'])
@token_required
def update_patient(patient_id):
    try:
        # Check if patient exists
        patient_doc = patients_ref.document(patient_id).get()
        if not patient_doc.exists:
            return error_response("Patient not found", 404)
        
        # Get JSON data from request
        data = request.get_json()
        
        # Add updated timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        # Update patient
        patients_ref.document(patient_id).update(data)
        
        # Get updated patient data
        updated_doc = patients_ref.document(patient_id).get()
        updated_data = updated_doc.to_dict()
        updated_data['id'] = patient_id
        
        return response_with_data(updated_data, "Patient updated successfully")
    except Exception as e:
        return error_response(f"Failed to update patient: {str(e)}", 500)

@app.route('/api/patients/<P_id>', methods=['DELETE'])
@token_required
def delete_patient(patient_id):
    try:
        # Check if patient exists
        patient_doc = patients_ref.document(patient_id).get()
        if not patient_doc.exists:
            return error_response("Patient not found", 404)
        
        # Delete patient
        patients_ref.document(patient_id).delete()
        
        return response_with_data({"id": patient_id}, "Patient deleted successfully")
    except Exception as e:
        return error_response(f"Failed to delete patient: {str(e)}", 500)

# Additional endpoints for patient-related operations
@app.route(f'/api/patients/<patient_id>/medical-records', methods=['GET'])
@token_required
def get_patient_medical_records(patient_id):
    try:
        # Check if patient exists
        patient_doc = patients_ref.document(patient_id).get()
        if not patient_doc.exists:
            return error_response("Patient not found", 404)
        
        # Get medical records subcollection
        records = []
        records_ref = patients_ref.document(patient_id).collection('medical_records')
        docs = records_ref.order_by('date', direction='desc').stream()
        
        for doc in docs:
            record_data = doc.to_dict()
            record_data['id'] = doc.id
            records.append(record_data)
            
        return response_with_data(records, "Medical records retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to fetch medical records: {str(e)}", 500)

@app.route('/api/patients/<patient_id>/medical-records', methods=['POST'])
@token_required
def add_patient_medical_record(patient_id):
    try:
        # Check if patient exists
        patient_doc = patients_ref.document(patient_id).get()
        if not patient_doc.exists:
            return error_response("Patient not found", 404)
        
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'diagnosis', 'doctor']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Add created timestamp
        data['created_at'] = datetime.now().isoformat()
        
        # Create new medical record
        records_ref = patients_ref.document(patient_id).collection('medical_records')
        new_record_ref = records_ref.document()
        new_record_ref.set(data)
        
        # Return the created record data with ID
        result = data.copy()
        result['id'] = new_record_ref.id
        
        return response_with_data(result, "Medical record added successfully", 201)
    except Exception as e:
        return error_response(f"Failed to add medical record: {str(e)}", 500)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return error_response("Endpoint not found", 404)

@app.errorhandler(405)
def method_not_allowed(e):
    return error_response("Method not allowed", 405)

@app.errorhandler(500)
def server_error(e):
    return error_response(f"Internal server error: {str(e)}", 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))