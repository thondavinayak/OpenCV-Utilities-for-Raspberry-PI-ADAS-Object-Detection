import cv2
import winsound
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time

class SecurityCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Security Camera")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.is_running = False
        self.sensitivity = 5000  # Default sensitivity
        self.alarm_enabled = True
        self.webcam = None
        self.current_frame = None
        
        # Setup UI
        self.setup_ui()
        
        # Initialize webcam
        self.init_webcam()
        
    def setup_ui(self):
        # Main frames
        control_frame = tk.Frame(self.root, bg='#2c3e50', padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        display_frame = tk.Frame(self.root, bg='#34495e')
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(control_frame, text="SECURITY CAMERA", 
                              font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
        title_label.pack(pady=10)
        
        # Status indicator
        self.status_label = tk.Label(control_frame, text="STATUS: OFF", 
                                    font=("Arial", 12), fg="#e74c3c", bg="#2c3e50")
        self.status_label.pack(pady=5)
        
        # Start/Stop button
        self.toggle_btn = ttk.Button(control_frame, text="Start Detection", 
                                    command=self.toggle_detection, width=20)
        self.toggle_btn.pack(pady=10)
        
        # Sensitivity control
        sens_frame = tk.Frame(control_frame, bg='#2c3e50')
        sens_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(sens_frame, text="Sensitivity:", fg="white", bg="#2c3e50").pack(anchor=tk.W)
        self.sens_scale = tk.Scale(sens_frame, from_=1000, to=10000, orient=tk.HORIZONTAL,
                                  length=200, showvalue=True, bg="#2c3e50", fg="white",
                                  highlightthickness=0, command=self.update_sensitivity)
        self.sens_scale.set(self.sensitivity)
        
        # Alarm toggle
        self.alarm_var = tk.BooleanVar(value=True)
        alarm_check = tk.Checkbutton(control_frame, text="Enable Alarm", variable=self.alarm_var,
                                    command=self.toggle_alarm, fg="white", bg="#2c3e50",
                                    selectcolor="#34495e")
        alarm_check.pack(pady=10)
        
        # Motion indicator
        motion_frame = tk.Frame(control_frame, bg='#2c3e50')
        motion_frame.pack(pady=10)
        
        tk.Label(motion_frame, text="Motion Detection:", fg="white", bg="#2c3e50").pack()
        self.motion_indicator = tk.Label(motion_frame, text="NO MOTION", fg="white", 
                                        bg="#2c3e50", font=("Arial", 10, "bold"))
        self.motion_indicator.pack(pady=5)
        
        # Stats
        stats_frame = tk.Frame(control_frame, bg='#2c3e50')
        stats_frame.pack(pady=10, fill=tk.X)
        
        self.motion_count = 0
        self.motion_counter = tk.Label(stats_frame, text=f"Motions Detected: {self.motion_count}",
                                      fg="white", bg="#2c3e50")
        self.motion_counter.pack(anchor=tk.W)
        
        # Video display
        self.video_label = tk.Label(display_frame, bg='#34495e')
        self.video_label.pack(pady=20)
        
        # Instructions
        instruct = tk.Label(control_frame, text="Press 'ESC' to exit\nPress 'Space' to pause",
                           fg="#bdc3c7", bg="#2c3e50", justify=tk.LEFT)
        instruct.pack(side=tk.BOTTOM, pady=10)
        
    def init_webcam(self):
        try:
            self.webcam = cv2.VideoCapture(0)
            if not self.webcam.isOpened():
                messagebox.showerror("Error", "Cannot access webcam. Please check your camera.")
                self.root.destroy()
                return
                
            # Test capture
            ret, frame = self.webcam.read()
            if not ret:
                messagebox.showerror("Error", "Cannot read from webcam.")
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize webcam: {str(e)}")
            self.root.destroy()
            
    def toggle_detection(self):
        if self.is_running:
            self.is_running = False
            self.toggle_btn.config(text="Start Detection")
            self.status_label.config(text="STATUS: OFF", fg="#e74c3c")
        else:
            self.is_running = True
            self.toggle_btn.config(text="Stop Detection")
            self.status_label.config(text="STATUS: ACTIVE", fg="#2ecc71")
            # Start detection in a separate thread
            threading.Thread(target=self.detect_motion, daemon=True).start()
            
    def update_sensitivity(self, value):
        self.sensitivity = int(value)
        
    def toggle_alarm(self):
        self.alarm_enabled = self.alarm_var.get()
        
    def detect_motion(self):
        # Initialize background subtractor
        back_sub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
        
        # For frame rate calculation
        prev_time = 0
        
        while self.is_running:
            try:
                # Read frames
                ret, frame1 = self.webcam.read()
                if not ret:
                    continue
                    
                ret, frame2 = self.webcam.read()
                if not ret:
                    continue
                
                # Calculate FPS
                current_time = time.time()
                fps = 1 / (current_time - prev_time) if prev_time > 0 else 0
                prev_time = current_time
                
                # Flip frame for mirror effect
                frame1 = cv2.flip(frame1, 1)
                frame2 = cv2.flip(frame2, 1)
                
                # Convert to grayscale
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                
                # Calculate absolute difference
                diff = cv2.absdiff(gray1, gray2)
                
                # Apply threshold
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                
                # Dilate to fill holes
                kernel = np.ones((5, 5), np.uint8)
                thresh = cv2.dilate(thresh, kernel, iterations=2)
                
                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                motion_detected = False
                
                for contour in contours:
                    if cv2.contourArea(contour) < self.sensitivity:
                        continue
                    
                    motion_detected = True
                    self.motion_count += 1
                    
                    # Draw bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    
                    # Trigger alarm if enabled
                    if self.alarm_enabled:
                        winsound.Beep(500, 100)
                
                # Update motion indicator
                if motion_detected:
                    self.motion_indicator.config(text="MOTION DETECTED", fg="#e74c3c")
                else:
                    self.motion_indicator.config(text="NO MOTION", fg="#2ecc71")
                
                # Update motion counter
                self.motion_counter.config(text=f"Motions Detected: {self.motion_count}")
                
                # Add info text to frame
                cv2.putText(frame1, f"FPS: {int(fps)}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame1, f"Sensitivity: {self.sensitivity}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                status_text = "ACTIVE" if self.is_running else "PAUSED"
                cv2.putText(frame1, f"Status: {status_text}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Convert frame for display in Tkinter
                frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail((800, 600))  # Resize image to fit GUI
                img_tk = ImageTk.PhotoImage(img)
                
                # Update GUI from main thread
                self.root.after(0, self.update_display, img_tk)
                
                # Check for exit key
                if cv2.waitKey(10) == 27:  
                    self.is_running = False
                    break
                    
            except Exception as e:
                print(f"Error in motion detection: {e}")
                continue
                
    def update_display(self, img):
        self.video_label.configure(image=img)
        self.video_label.image = img
        
    def on_closing(self):
        self.is_running = False
        if self.webcam:
            self.webcam.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityCameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()