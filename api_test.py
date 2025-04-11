# app.py - Main Flask application
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# Sample data for medicine vending machines
VENDING_MACHINES = [
    {"id": 1, "name": "City Hospital Vending", "lat": 40.7128, "lng": -74.0060, "address": "123 Hospital Way", "available_meds": ["Pain relievers", "Cold medicine", "First aid supplies"]},
    {"id": 2, "name": "Central Station Pharmacy", "lat": 40.7500, "lng": -73.9967, "address": "456 Main Street", "available_meds": ["Allergy medication", "Vitamins", "Bandages"]},
    {"id": 3, "name": "University Health Center", "lat": 40.7282, "lng": -73.9942, "address": "789 Campus Drive", "available_meds": ["Pain relievers", "Fever reducers", "Cough drops"]},
    {"id": 4, "name": "Downtown Medical Plaza", "lat": 40.7589, "lng": -73.9851, "address": "101 Medical Plaza", "available_meds": ["Antacids", "Sleep aids", "Eye drops"]},
    {"id": 5, "name": "Neighborhood Pharmacy", "lat": 40.7300, "lng": -74.0200, "address": "202 Local Avenue", "available_meds": ["Pain relievers", "Digestive aids", "Skin care"]}
]

# ----- API Routes -----
@app.route('/api/vending-machines', methods=['GET'])
def get_vending_machines():
    return jsonify(VENDING_MACHINES)

# ----- Web Routes -----
@app.route('/')
def index():
    return render_template('index.html')

# Create necessary directories and files
def setup_files():
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Create static directory and its subdirectories
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    
    # Create index.html
    with open('templates/index.html', 'w') as f:
        f.write('''

        ''')
    
    # Create JavaScript file
    with open('static/js/map.js', 'w') as f:
        f.write('''
// Initialize the map
const map = L.map('map').setView([40.7128, -74.0060], 13);

// Add tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
}).addTo(map);

// Store all markers for search functionality
let allMarkers = [];
let vendingMachines = [];

// Fetch vending machine data from API
async function fetchVendingMachines() {
    try {
        const response = await fetch('/api/vending-machines');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        vendingMachines = await response.json();
        displayVendingMachines(vendingMachines);
        updateMachineCount(vendingMachines.length);
        
        // Center map based on all locations
        centerMap(vendingMachines);
    } catch (error) {
        console.error('Error fetching vending machines:', error);
        document.getElementById('info-panel').innerHTML = 
            '<div class="error">Error loading vending machines. Please try again later.</div>';
    }
}

// Display vending machines on the map
function displayVendingMachines(machines) {
    // Clear existing markers
    allMarkers.forEach(marker => map.removeLayer(marker));
    allMarkers = [];
    
    machines.forEach(machine => {
        const popupContent = `
            <div class="custom-popup">
                <h4>${machine.name}</h4>
                <p><strong>Address:</strong> ${machine.address}</p>
                <p><strong>Available medications:</strong></p>
                <ul>
                    ${machine.available_meds.map(med => `<li>${med}</li>`).join('')}
                </ul>
                <button onclick="getDirections(${machine.lat}, ${machine.lng})">
                    <i class="fas fa-directions"></i> Get Directions
                </button>
            </div>
        `;
        
        const marker = L.marker([machine.lat, machine.lng])
            .bindPopup(popupContent)
            .bindTooltip(machine.name)
            .addTo(map);
            
        // Store reference to marker
        allMarkers.push(marker);
    });
}

// Center map based on all vending machine locations
function centerMap(machines) {
    if (machines.length === 0) return;
    
    // Calculate average position
    const avgLat = machines.reduce((sum, m) => sum + m.lat, 0) / machines.length;
    const avgLng = machines.reduce((sum, m) => sum + m.lng, 0) / machines.length;
    
    map.setView([avgLat, avgLng], 13);
}

// Update machine count in info panel
function updateMachineCount(count) {
    document.getElementById('machine-count').textContent = 
        `${count} medicine vending ${count === 1 ? 'machine' : 'machines'} found`;
}

// Search functionality
document.getElementById('search-input').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    if (!searchTerm) {
        // If search is empty, show all vending machines
        displayVendingMachines(vendingMachines);
        updateMachineCount(vendingMachines.length);
        return;
    }
    
    // Filter vending machines based on search term
    const filteredMachines = vendingMachines.filter(machine => {
        // Search in name, address, and available medications
        return machine.name.toLowerCase().includes(searchTerm) ||
               machine.address.toLowerCase().includes(searchTerm) ||
               machine.available_meds.some(med => med.toLowerCase().includes(searchTerm));
    });
    
    displayVendingMachines(filteredMachines);
    updateMachineCount(filteredMachines.length);
    
    // Center map on filtered results
    if (filteredMachines.length > 0) {
        centerMap(filteredMachines);
    }
});

// Locate me functionality
document.getElementById('locate-me').addEventListener('click', function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // Success callback
            position => {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                
                // Add a marker for the user's location
                const userMarker = L.marker([userLat, userLng], {
                    icon: L.divIcon({
                        className: 'user-location',
                        html: '<div style="background-color: #1E88E5; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
                        iconSize: [16, 16],
                        iconAnchor: [8, 8]
                    })
                }).addTo(map);
                
                // Add a circle to show accuracy
                L.circle([userLat, userLng], {
                    radius: position.coords.accuracy / 2,
                    fillColor: '#1E88E5',
                    fillOpacity: 0.15,
                    stroke: false
                }).addTo(map);
                
                // Center map on user's location
                map.setView([userLat, userLng], 15);
                
                // Find closest vending machine
                findClosestVendingMachine(userLat, userLng);
            },
            // Error callback
            error => {
                console.error('Error getting location:', error);
                alert('Unable to access your location. Please check your device settings.');
            }
        );
    } else {
        alert('Geolocation is not supported by your browser.');
    }
});

// Find closest vending machine
function findClosestVendingMachine(userLat, userLng) {
    if (vendingMachines.length === 0) return;
    
    let closestMachine = null;
    let closestDistance = Infinity;
    
    vendingMachines.forEach(machine => {
        const distance = calculateDistance(
            userLat, userLng, 
            machine.lat, machine.lng
        );
        
        if (distance < closestDistance) {
            closestDistance = distance;
            closestMachine = machine;
        }
    });
    
    if (closestMachine) {
        // Highlight the closest vending machine
        const markerIndex = vendingMachines.findIndex(m => m.id === closestMachine.id);
        if (markerIndex >= 0 && markerIndex < allMarkers.length) {
            allMarkers[markerIndex].openPopup();
        }
        
        // Show info about the closest machine
        const distanceKm = (closestDistance / 1000).toFixed(2);
        document.getElementById('info-panel').innerHTML = `
            <div id="machine-count">${vendingMachines.length} medicine vending machines found</div>
            <div id="closest-info">
                Closest: <strong>${closestMachine.name}</strong> (${distanceKm} km)
            </div>
        `;
    }
}

// Calculate distance between two coordinates in meters (Haversine formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Earth radius in meters
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; // Distance in meters
}

// Function to get directions to a vending machine
function getDirections(lat, lng) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                
                // Open Google Maps directions in a new tab
                window.open(
                    `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${lat},${lng}`,
                    '_blank'
                );
            },
            error => {
                // If can't get user location, just navigate to the destination
                window.open(
                    `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`,
                    '_blank'
                );
            }
        );
    } else {
        // If geolocation not supported, just navigate to the destination
        window.open(
            `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`,
            '_blank'
        );
    }
}

// Initialize the app
fetchVendingMachines();
        ''')

if __name__ == '__main__':
    setup_files()
    app.run(debug=True, host='0.0.0.0', port=5001)