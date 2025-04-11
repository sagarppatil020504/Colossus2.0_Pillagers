import cv2
import numpy as np
import time
import os
import patient_db
from ultralytics import YOLO
import torch
import urllib.request

class FaceRecog:
    def __init__(self):
        self.known_face_embeddings = []
        self.known_face_names = []
        self.video_capture = None
        
        # Download YOLO face model if not available
        self.yolo_model_path = self.download_yolo_model()
        
        # Load YOLO model for face detection
        self.face_detector = YOLO(self.yolo_model_path)
        
        # Determine model path for face recognition
        self.face_model_path = self.get_face_model_path()
        
        # Initialize face recognition model
        try:
            # Try to use OpenCV's face recognition model if available
            self.face_embedding_model = cv2.FaceRecognizerSF.create(
                self.face_model_path,
                ""
            )
            self.use_cv_face_model = True
            print("✅ Using OpenCV face recognition model")
        except Exception as e:
            print(f"⚠️ Could not load OpenCV face model: {e}")
            print("⚠️ Using basic face similarity comparison")
            self.use_cv_face_model = False

    def download_yolo_model(self):
        """Download or use general YOLO model for face detection."""
        # Try using general YOLOv8n model first (which will download automatically)
        model_path = "yolov8n.pt"
        
        # Check if general YOLO model exists
        if not os.path.exists(model_path):
            print(f"⬇️ Downloading YOLOv8n model...")
            try:
                # Use ultralytics to download it
                YOLO("yolov8n.pt")
            except Exception as e:
                print(f"❌ Error downloading model: {e}")
                # Create models directory if it doesn't exist
                os.makedirs("models", exist_ok=True)
                
                # Direct download as backup
                try:
                    print("⬇️ Trying direct download...")
                    urllib.request.urlretrieve(
                        "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
                        model_path
                    )
                except Exception as e:
                    print(f"❌ Direct download failed: {e}")
                    raise Exception("Could not download YOLO model. Please download it manually.")
        
        print(f"✅ Using YOLO model at: {model_path}")
        return model_path

    def get_face_model_path(self):
        """Get path to OpenCV face recognition model, downloading if needed."""
        model_name = "face_recognition_sface_2021dec.onnx"
        model_dir = "models"
        model_path = os.path.join(model_dir, model_name)
        
        # Create models directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Check if model exists, download if not
        if not os.path.exists(model_path):
            print(f"⬇️ Downloading face recognition model...")
            try:
                url = "https://github.com/opencv/opencv_zoo/raw/master/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
                urllib.request.urlretrieve(url, model_path)
                print(f"✅ Downloaded face recognition model to {model_path}")
            except Exception as e:
                print(f"❌ Could not download face model: {e}")
                print("⚠️ Will use basic face comparison")
                return None
        
        return model_path
    
    def extract_face_features(self, face):
        """Extract face features using available method."""
        # Resize face to standard size
        face_resized = cv2.resize(face, (112, 112))
        
        if self.use_cv_face_model:
            # Use OpenCV's face recognition model
            return self.face_embedding_model.feature(face_resized)
        else:
            # Use simple feature extraction (flatten and normalize RGB values)
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            face_norm = face_gray.flatten().astype(np.float32) / 255.0
            return face_norm
    
    def compare_faces(self, face_embedding, known_embedding):
        """Compare faces using available method."""
        if self.use_cv_face_model:
            # Use OpenCV's cosine similarity
            return self.face_embedding_model.match(
                face_embedding, known_embedding, cv2.FaceRecognizerSF_FR_COSINE
            )
        else:
            # Use simple cosine similarity
            norm_a = np.linalg.norm(face_embedding)
            norm_b = np.linalg.norm(known_embedding)
            if norm_a == 0 or norm_b == 0:
                return 0
            return np.dot(face_embedding, known_embedding) / (norm_a * norm_b)

    def load_known_faces(self, photo_directory="IOT_relational_Database/patient_photos"):
        """Load known face images from a directory and generate embeddings."""
        known_faces = []
        
        # Handle case where directory doesn't exist
        if not os.path.exists(photo_directory):
            print(f"⚠️ Directory not found: {photo_directory}")
            print(f"🔍 Checking current directory...")
            
            # Try in current directory as fallback
            base_dir = os.path.basename(photo_directory)
            if os.path.exists(base_dir):
                print(f"✅ Found directory in current path: {base_dir}")
                photo_directory = base_dir
            else:
                # Try to create the directory
                try:
                    os.makedirs(photo_directory, exist_ok=True)
                    print(f"✅ Created directory: {photo_directory}")
                    print(f"ℹ️ Please add face images to this directory")
                    return False
                except Exception as e:
                    print(f"❌ Failed to create directory: {e}")
                    return False

        # List all JPG files in the directory
        image_files = [f for f in os.listdir(photo_directory) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        
        if not image_files:
            print(f"⚠️ No image files found in {photo_directory}")
            return False
        
        print(f"🔍 Found {len(image_files)} images to process")
        
        for filename in image_files:
            img_path = os.path.join(photo_directory, filename)
            label = os.path.splitext(filename)[0]
            known_faces.append((img_path, label))

        for image_path, name in known_faces:
            try:
                # Load image
                image = cv2.imread(image_path)
                if image is None:
                    print(f"⚠️ Warning: Could not read image {image_path}")
                    continue
                
                # Detect faces using YOLO
                results = self.face_detector(image)
                
                if len(results[0].boxes) > 0:
                    # Get the first face detected (assuming one face per image)
                    box = results[0].boxes[0].xyxy.cpu().numpy()[0]
                    x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                    
                    # Extract the face
                    face = image[y1:y2, x1:x2]
                    if face.size == 0:
                        print(f"⚠️ Warning: Face extraction failed for {image_path}")
                        continue
                    
                    # Get face embedding
                    face_embedding = self.extract_face_features(face)
                    
                    self.known_face_embeddings.append(face_embedding)
                    self.known_face_names.append(name)
                    print(f"✅ Loaded face for: {name}")
                else:
                    print(f"⚠️ Warning: No face detected in {image_path}")
            except Exception as e:
                print(f"❌ Error loading {image_path}: {e}")

        print(f"✅ Successfully loaded {len(self.known_face_embeddings)} face(s)")
        return len(self.known_face_embeddings) > 0

    def initialize_webcam(self):
        """Initialize the webcam with a lower resolution."""
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            print("❌ Error: Could not open webcam.")
            return False

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
        return True

    def process_frame(self, frame):
        """Process a frame for face detection and recognition using YOLO."""
        # Detect faces using YOLO
        results = self.face_detector(frame, classes=[0])  # Class 0 for person in YOLO
        
        face_names = []
        face_locations = []
        
        if len(results[0].boxes) > 0:
            for box in results[0].boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                
                # Only process faces with reasonable size
                if (x2-x1) < 10 or (y2-y1) < 10:
                    continue
                    
                face_locations.append((y1, x2, y2, x1))  # Convert to (top, right, bottom, left)
                
                # Extract the face and align it
                face = frame[y1:y2, x1:x2]
                if face.size == 0:
                    face_names.append("Unknown")
                    continue
                
                # Get face embedding
                face_embedding = self.extract_face_features(face)
                
                # Compare with known faces
                name = "Unknown"
                if self.known_face_embeddings:
                    # Calculate similarities
                    similarities = []
                    for emb in self.known_face_embeddings:
                        similarity = self.compare_faces(face_embedding, emb)
                        similarities.append(similarity)
                    
                    # If similarity is above threshold, assign name
                    best_match_index = np.argmax(similarities)
                    similarity_threshold = 0.6 if self.use_cv_face_model else 0.8
                    if similarities[best_match_index] > similarity_threshold:
                        name = self.known_face_names[best_match_index]
                
                face_names.append(name)

        return frame, face_names, face_locations

    def main(self):
        """Run face recognition in a loop until 'q' is pressed."""
        print("🔍 Loading face database...")
        if not self.load_known_faces():
            print("⚠️ No valid face embeddings loaded.")
            print("ℹ️ You can add face images to the photos directory and restart.")
            print("ℹ️ Continuing with empty database...")
        
        print("📹 Initializing webcam...")
        if not self.initialize_webcam():
            return

        prev_time = time.time()
        process_this_frame = True
        processed_faces = set()  # Store processed faces across frames

        print("✅ System ready! Press 'q' to quit or 'r' to reset face processing.")

        try:
            while True:
                ret, frame = self.video_capture.read()
                if not ret:
                    print("⚠️ Could not read frame, retrying...")
                    time.sleep(0.1)
                    continue

                current_time = time.time()
                elapsed_time = current_time - prev_time
                fps = 1 / elapsed_time if elapsed_time > 0 else 0
                prev_time = current_time

                if process_this_frame:
                    frame, face_names, face_locations = self.process_frame(frame)

                    # Only initialize database if faces were detected
                    if face_names:
                        try:
                            pat = patient_db.MedicalRecords()  # Initialize once per frame

                            for id_face in face_names:
                                if id_face != "Unknown" and id_face not in processed_faces:
                                    print(f"🔍 Processing ID: {id_face}")
                                    try:
                                        pat.get_patients_withPid(id_face)
                                        processed_faces.add(id_face)  # Add to processed set
                                    except Exception as e:
                                        print(f"⚠️ Error processing patient data: {e}")
                                elif id_face != "Unknown":
                                    print(f"⏩ Skipping already processed ID: {id_face}")
                        except Exception as e:
                            print(f"⚠️ Error with patient database: {e}")

                process_this_frame = not process_this_frame  # Skip alternate frames

                # Draw face rectangles and names
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 150), 2)
                    cv2.putText(frame, name, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 150), 2)
                
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.imshow("Real-Time Face Recognition", frame)

                time.sleep(0.001)  # Prevent CPU overload

                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):  # Quit
                    break
                elif key == ord('r'):  # Reset face processing
                    print("🔄 Resetting processed faces...")
                    processed_faces.clear()  # Clear stored IDs for reprocessing

        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user (Ctrl+C).")
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
        finally:
            if self.video_capture is not None:
                self.video_capture.release()
            cv2.destroyAllWindows()
            print("🛑 Webcam closed. Exiting.")


if __name__ == "__main__":
    FaceRecog().main()