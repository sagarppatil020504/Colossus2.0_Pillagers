import serial
import time

# Function to check if COM4 is available
def is_serial_connected(port="COM4"):
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        ser.close()
        return True
    except serial.SerialException:
        return False

# Function to send patient data to Arduino
def send_patient_data(P_id, pat_name, age, medical_cond, medicines, time_medicines, medicine_taken, port="COM4"):
    if not is_serial_connected(port):
        print("❌ Error: Arduino (COM4) not connected. Please check the connection.")
        return False

    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)  # Allow time for the serial connection to establish

        # Format data as CSV
        data = f"{P_id},{pat_name},{age},{medical_cond},{','.join(medicines)},{','.join(time_medicines)},{medicine_taken}\n"
        ser.write(data.encode())  # Send data to Arduino
        ser.close()
        print("✅ Data successfully sent to Arduino!")
        return True
    except serial.SerialException as e:
        print(f"❌ Serial Error: {e}")
        return False
