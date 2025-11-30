import os
import time
import smtplib
import datetime
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from imageai.Detection import ObjectDetection
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

def send_email(subject, body, sender_email, receiver_email, password, image_path, log_callback=None):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        image_mime = MIMEImage(image_data)
        image_mime.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
        message.attach(image_mime)

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.mailosaur.net", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        if log_callback:
            log_callback("Email sent successfully!")
    except Exception as e:
        error_msg = f"Failed to send email. Error: {e}"
        if log_callback:
            log_callback(error_msg)
    finally:
        try:
            server.quit()
        except:
            pass

class PersonDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Person Detection System")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        self.is_running = False
        self.detection_thread = None
        self.detector = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        title_label = ttk.Label(main_frame, text="Person Detection System", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        model_frame = ttk.LabelFrame(main_frame, text="Model Configuration", padding="10")
        model_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        model_frame.columnconfigure(1, weight=1)
        
        ttk.Label(model_frame, text="Model Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_path_entry = ttk.Entry(model_frame, width=40)
        self.model_path_entry.insert(0, os.path.join(os.getcwd(), "yolov3.pt"))
        self.model_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        config_frame = ttk.LabelFrame(main_frame, text="Email Configuration (Optional)", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        info_label = ttk.Label(config_frame, text="Leave empty to run without email notifications", 
                              font=("Arial", 9), foreground="gray")
        info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(config_frame, text="Sender Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sender_email_entry = ttk.Entry(config_frame, width=40)
        self.sender_email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(config_frame, text="Receiver Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.receiver_email_entry = ttk.Entry(config_frame, width=40)
        self.receiver_email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(config_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(config_frame, width=40, show="*")
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Detection", command=self.start_detection, width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Detection", command=self.stop_detection, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        logs_frame = ttk.LabelFrame(main_frame, text="Logs", padding="10")
        logs_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=15, width=70, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.config(state=tk.DISABLED)
        
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def start_detection(self):
        model_path = self.model_path_entry.get().strip()
        sender_email = self.sender_email_entry.get().strip()
        receiver_email = self.receiver_email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not model_path:
            messagebox.showerror("Error", "Please specify a model path!")
            return
        
        email_enabled = bool(sender_email and receiver_email and password)
        
        if sender_email or receiver_email or password:
            if not email_enabled:
                messagebox.showerror("Error", "Please fill in all email fields or leave all empty!")
                return
        
        if self.is_running:
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running", foreground="green")
        
        self.log_message("Starting person detection system...")
        self.log_message(f"Model path: {model_path}")
        if email_enabled:
            self.log_message(f"Email notifications: ENABLED")
            self.log_message(f"Sender: {sender_email}")
            self.log_message(f"Receiver: {receiver_email}")
        else:
            self.log_message("Email notifications: DISABLED (running without email)")
        
        self.detection_thread = threading.Thread(target=self.detection_loop, 
                                                 args=(model_path, sender_email, receiver_email, password, email_enabled),
                                                 daemon=True)
        self.detection_thread.start()
        
    def stop_detection(self):
        if not self.is_running:
            return
        
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", foreground="red")
        self.log_message("Stopping person detection system...")
        
    def detection_loop(self, model_path, sender_email, receiver_email, password, email_enabled):
        execution_path = os.getcwd()
        
        try:
            self.log_message("Loading YOLOv3 model...")
            
            if not os.path.exists(model_path):
                error_msg = f"YOLOv3 model file not found at: {model_path}\n\n"
                error_msg += "Please download the YOLOv3 model file:\n"
                error_msg += "1. Visit: https://github.com/OlafenwaMoses/ImageAI/releases\n"
                error_msg += "2. Download 'yolov3.pt' file\n"
                error_msg += "3. Place it in the specified location or update the model path"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("Model File Missing", error_msg))
                self.root.after(0, self.stop_detection)
                return
            
            self.detector = ObjectDetection()
            self.detector.setModelTypeAsYOLOv3()
            self.detector.setModelPath(model_path)
            self.detector.loadModel()
            self.log_message("Model loaded successfully!")
            
            processed_images_file = os.path.join(execution_path, "processed_images.txt")
            logs_file = os.path.join(execution_path, "logs.txt")
            
            detection_dir = os.path.join(execution_path, "detection_images")
            detected_dir = os.path.join(execution_path, "detected_images")
            os.makedirs(detection_dir, exist_ok=True)
            os.makedirs(detected_dir, exist_ok=True)
            
            processed_images = set()
            if os.path.exists(processed_images_file):
                with open(processed_images_file, 'r') as f:
                    processed_images = set(f.read().splitlines())
            
            self.log_message("Monitoring for new images...")
            
            while self.is_running:
                try:
                    detection_images = os.listdir(detection_dir)
                    
                    for image_name in detection_images:
                        if not self.is_running:
                            break
                            
                        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                            if image_name not in processed_images:
                                self.log_message(f"Processing image: {image_name}")
                                
                                input_image_path = os.path.join(detection_dir, image_name)
                                output_image_path = os.path.join(detected_dir, image_name)
                                
                                try:
                                    detections = self.detector.detectObjectsFromImage(
                                        input_image=input_image_path,
                                        output_image_path=output_image_path,
                                        minimum_percentage_probability=30
                                    )
                                    
                                    with open(logs_file, 'a') as log_file:
                                        log_file.write(f"Image: {image_name}\n")
                                        
                                    person_detected = False
                                    for eachObject in detections:
                                        if eachObject["name"] == "person":
                                            person_detected = True
                                            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            prob = eachObject['percentage_probability']
                                            
                                            self.log_message(f"PERSON DETECTED in {image_name}: {prob:.2f}%")
                                            
                                            with open(logs_file, 'a') as log_file:
                                                log_file.write(f"{current_time} - Person detected: {prob}%\n")
                                            
                                            if email_enabled:
                                                send_email(
                                                    "Person Detected",
                                                    f"A person was detected in the image '{image_name}' at {current_time}",
                                                    sender_email, receiver_email, password, output_image_path,
                                                    log_callback=self.log_message
                                                )
                                            else:
                                                self.log_message("Email notification skipped (email not configured)")
                                    
                                    if not person_detected:
                                        self.log_message(f"No person detected in {image_name}")
                                    
                                    with open(logs_file, 'a') as log_file:
                                        log_file.write("--------------------------------\n")
                                    
                                    processed_images.add(image_name)
                                    
                                    with open(processed_images_file, 'a') as f:
                                        f.write(image_name + '\n')
                                        
                                except Exception as e:
                                    error_msg = f"Error processing {image_name}: {str(e)}"
                                    self.log_message(error_msg)
                                    with open(logs_file, 'a') as log_file:
                                        log_file.write(f"ERROR: {error_msg}\n")
                                    
                except Exception as e:
                    self.log_message(f"Error reading detection directory: {str(e)}")
                
                if self.is_running:
                    time.sleep(5)
                    
        except Exception as e:
            error_msg = f"Fatal error in detection loop: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, self.stop_detection)

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonDetectionApp(root)
    root.mainloop()
