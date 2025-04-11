import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
import argparse
import os
from datetime import datetime

class PrescriptionOCR:
    def __init__(self, use_transformer=True):
        """
        Initialize the Prescription OCR system
        
        Args:
            use_transformer (bool): If True, uses a medical NER model for entity extraction
        """
        self.use_transformer = use_transformer
        
        # Initialize Tesseract path (you may need to modify this based on your installation)
        pytesseract.pytesseract.tesseract_cmd = r'tesseract'  # Update with your path if needed
        
        # Load medical NER model if transformer approach is selected
        if use_transformer:
            self.tokenizer = AutoTokenizer.from_pretrained("samrawal/bert-base-uncased_medical-ner")
            self.model = AutoModelForTokenClassification.from_pretrained("samrawal/bert-base-uncased_medical-ner")
            self.ner = pipeline('ner', model=self.model, tokenizer=self.tokenizer, aggregation_strategy='simple')
    
    def capture_image(self, camera_id=0, save_dir="captured_prescriptions"):
        """
        Capture an image from a camera
        
        Args:
            camera_id (int): Camera device ID (usually 0 for built-in webcam)
            save_dir (str): Directory to save captured images
            
        Returns:
            str: Path to the captured image file
        """
        # Create directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Initialize camera
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise Exception(f"Could not open camera with ID {camera_id}")
        
        # Check camera properties
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Camera initialized: {frame_width}x{frame_height}")
        print("Position the prescription in the frame and press SPACE to capture")
        print("Press ESC to cancel")
        
        while True:
            # Capture frame
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Display the frame
            cv2.imshow('Capture Prescription (SPACE to capture, ESC to cancel)', frame)
            
            # Wait for key press
            key = cv2.waitKey(1)
            
            # ESC key to exit
            if key == 27:  # ESC key
                print("Image capture cancelled")
                cap.release()
                cv2.destroyAllWindows()
                return None
            
            # SPACE key to capture
            elif key == 32:  # SPACE key
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{save_dir}/prescription_{timestamp}.jpg"
                
                # Save the captured image
                cv2.imwrite(filename, frame)
                print(f"Image captured and saved as {filename}")
                
                # Release camera and close windows
                cap.release()
                cv2.destroyAllWindows()
                
                return filename
        
        # Release if loop exits
        cap.release()
        cv2.destroyAllWindows()
        return None

    def capture_from_file(self, file_path):
        """
        Process an image from a file by creating a copy in the prescriptions directory
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            str: Path to the copied image file
        """
        save_dir = "captured_prescriptions"
        
        # Create directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_dir}/prescription_{timestamp}.jpg"
        
        # Read and save the image
        img = cv2.imread(file_path)
        cv2.imwrite(filename, img)
        
        return filename
    
    def preprocess_image(self, image_path):
        """
        Preprocess the prescription image to improve OCR accuracy
        
        Args:
            image_path (str): Path to the prescription image
            
        Returns:
            np.array: Preprocessed image
        """
        # Read the image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Dilation to make text clearer
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(opening, kernel, iterations=1)
        
        return dilated
    
    def extract_text(self, image_path):
        """
        Extract all text from the prescription image
        
        Args:
            image_path (str): Path to the prescription image
            
        Returns:
            str: Extracted text
        """
        # Preprocess the image
        processed_img = self.preprocess_image(image_path)
        
        # Extract text using Tesseract OCR
        text = pytesseract.image_to_string(processed_img, lang='eng', config='--psm 6')
        
        return text
    
    def extract_structured_info(self, text):
        """
        Extract structured information from the prescription text
        
        Args:
            text (str): Raw text extracted from the prescription
            
        Returns:
            dict: Structured prescription information
        """
        if self.use_transformer:
            # Use NER model to extract entities
            entities = self.ner(text)
            
            # Organize entities by type
            prescription_info = {
                "patient_name": "",
                "doctor_name": "",
                "medications": [],
                "dosage": [],
                "frequency": [],
                "date": ""
            }
            
            # Map NER results to prescription fields
            for entity in entities:
                if entity['entity_group'] == 'PATIENT':
                    prescription_info["patient_name"] += entity['word'] + " "
                elif entity['entity_group'] == 'DOCTOR':
                    prescription_info["doctor_name"] += entity['word'] + " "
                elif entity['entity_group'] == 'DRUG':
                    prescription_info["medications"].append(entity['word'])
                elif entity['entity_group'] == 'DOSAGE':
                    prescription_info["dosage"].append(entity['word'])
                elif entity['entity_group'] == 'FREQUENCY':
                    prescription_info["frequency"].append(entity['word'])
                elif entity['entity_group'] == 'DATE':
                    prescription_info["date"] += entity['word'] + " "
            
            # Clean up any trailing spaces
            for key in ["patient_name", "doctor_name", "date"]:
                prescription_info[key] = prescription_info[key].strip()
                
        else:
            # Rule-based extraction using regex patterns
            prescription_info = {
                "patient_name": "",
                "doctor_name": "",
                "medications": [],
                "dosage": [],
                "frequency": [],
                "date": ""
            }
            
            # Extract patient name (assuming format "Patient: Name" or "Name: Patient")
            patient_match = re.search(r"Patient\s*:\s*([A-Za-z\s]+)", text, re.IGNORECASE) or \
                           re.search(r"Name\s*:\s*([A-Za-z\s]+)", text, re.IGNORECASE)
            if patient_match:
                prescription_info["patient_name"] = patient_match.group(1).strip()
            
            # Extract doctor name
            doctor_match = re.search(r"Dr\.?\s*([A-Za-z\s]+)", text, re.IGNORECASE) or \
                          re.search(r"Doctor\s*:\s*([A-Za-z\s]+)", text, re.IGNORECASE) or \
                          re.search(r"Physician\s*:\s*([A-Za-z\s]+)", text, re.IGNORECASE)
            if doctor_match:
                prescription_info["doctor_name"] = doctor_match.group(1).strip()
            
            # Extract date
            date_match = re.search(r"Date\s*:\s*([0-9\-/\.]+)", text, re.IGNORECASE) or \
                        re.search(r"([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})", text)
            if date_match:
                prescription_info["date"] = date_match.group(1).strip()
            
            # Extract medications with dosage and frequency
            # Look for common medication patterns
            med_patterns = [
                r"(?:Rx|R/)?\s*([A-Za-z]+(?:[\s-][A-Za-z]+)*)\s+(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg)\s*(?:(\d+)\s*times\s*(?:a|per)\s*day|(\w+))",
                r"(\w+(?:[\s-]\w+)*)\s+(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg)"
            ]
            
            for pattern in med_patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    groups = match.groups()
                    if groups[0]:  # Medication name
                        prescription_info["medications"].append(groups[0].strip())
                    if groups[1] and groups[2]:  # Dosage with unit
                        prescription_info["dosage"].append(f"{groups[1]} {groups[2]}")
                    if len(groups) > 3 and (groups[3] or groups[4]):  # Frequency
                        freq = groups[3] if groups[3] else groups[4]
                        prescription_info["frequency"].append(freq.strip())
        
        return prescription_info
    
    def process_prescription(self, image_path=None):
        """
        Process a prescription image and extract structured information
        
        Args:
            image_path (str, optional): Path to the prescription image. If None, capture from camera.
            
        Returns:
            dict: Structured prescription information
        """
        # If no image path is provided, capture one
        if image_path is None:
            image_path = self.capture_image()
            if image_path is None:
                return {"error": "Image capture cancelled or failed"}
        
        # Extract raw text
        text = self.extract_text(image_path)
        
        # Extract structured information
        prescription_info = self.extract_structured_info(text)
        
        return {
            "image_path": image_path,
            "raw_text": text,
            "structured_info": prescription_info
        }
    
    def display_results(self, results):
        """
        Display the extracted information
        
        Args:
            results (dict): Results from process_prescription
        """
        if "error" in results:
            print(f"Error: {results['error']}")
            return
            
        print("=== PRESCRIPTION ANALYSIS RESULTS ===\n")
        print(f"Image: {results['image_path']}")
        
        print("\nRAW EXTRACTED TEXT:")
        print("-----------------------")
        print(results["raw_text"])
        print("\n")
        
        print("STRUCTURED INFORMATION:")
        print("-----------------------")
        info = results["structured_info"]
        
        print(f"Patient: {info['patient_name']}")
        print(f"Doctor: {info['doctor_name']}")
        print(f"Date: {info['date']}")
        
        print("\nMedications:")
        for i, med in enumerate(info["medications"]):
            dosage = info["dosage"][i] if i < len(info["dosage"]) else "N/A"
            frequency = info["frequency"][i] if i < len(info["frequency"]) else "N/A"
            print(f"  - {med}, {dosage}, {frequency}")
        
        # Display the original and processed images
        orig_img = cv2.imread(results["image_path"])
        proc_img = self.preprocess_image(results["image_path"])
        
        # Resize images for display
        height, width = orig_img.shape[:2]
        max_display_height = 800
        if height > max_display_height:
            scale = max_display_height / height
            new_height = int(height * scale)
            new_width = int(width * scale)
            orig_img = cv2.resize(orig_img, (new_width, new_height))
            proc_img = cv2.resize(proc_img, (new_width, new_height))
        
        # Display original and processed images side by side
        combined = np.hstack((orig_img, cv2.cvtColor(proc_img, cv2.COLOR_GRAY2BGR)))
        cv2.imshow("Original (left) vs Processed (right)", combined)
        print("\nPress any key to close image display")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Example usage with command line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prescription OCR System')
    parser.add_argument('--image', type=str, help='Path to prescription image file (optional)')
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID (default: 0)')
    parser.add_argument('--no-transformer', action='store_true', help='Use rule-based approach instead of transformer')
    
    args = parser.parse_args()
    
    # Initialize the OCR system
    ocr = PrescriptionOCR(use_transformer=not args.no_transformer)
    
    if args.image:
        # Process existing image file
        image_path = ocr.capture_from_file(args.image)
        results = ocr.process_prescription(image_path)
    else:
        # Capture and process image from camera
        results = ocr.process_prescription()
    
    # Display the results
    ocr.display_results(results)