import cv2
import mediapipe as mp
import winsound
import math
import datetime
import os

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Initialize webcam
camera = cv2.VideoCapture(0)

# Set camera properties for faster frame rate
camera.set(cv2.CAP_PROP_FPS, 30)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize coordinates
x1, y1, x2, y2 = 0, 0, 0, 0

# Create directory for selfies if it doesn't exist
if not os.path.exists("selfies"):
    os.makedirs("selfies")

# Variable to prevent multiple rapid selfies
last_selfie_time = 0
selfie_cooldown = 2000  # 2 seconds cooldown between selfies

while True:
    # Read frame from camera
    ret, image = camera.read()
    if not ret:
        break
        
    # Flip image horizontally for a mirror effect
    image = cv2.flip(image, 1)
    fh, fw, _ = image.shape
    
    # Convert to RGB for MediaPipe processing
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image with Face Mesh
    output = face_mesh.process(rgb_image)
    landmark_points = output.multi_face_landmarks
    
    if landmark_points:
        landmarks = landmark_points[0].landmark
        
        for id, landmark in enumerate(landmarks):
            x = int(landmark.x * fw)
            y = int(landmark.y * fh)
            
            # Get left mouth corner (landmark 61)
            if id == 61:
                x1 = x
                y1 = y
                # Draw circle on left mouth corner
                cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
                
            # Get right mouth corner (landmark 291)
            if id == 291:
                x2 = x
                y2 = y
                # Draw circle on right mouth corner
                cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
        
        # Calculate distance between mouth corners
        if x1 != 0 and y1 != 0 and x2 != 0 and y2 != 0:
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            dist = int(dist)
            
            # Display distance on screen
            cv2.putText(image, f"Smile Distance: {dist}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # If distance is greater than threshold (smiling), take selfie
            current_time = cv2.getTickCount()
            if dist > 60 and (current_time - last_selfie_time) / cv2.getTickFrequency() * 1000 > selfie_cooldown:
                # Generate timestamp for filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"selfies/selfie_{timestamp}.png"
                
                # Save the selfie
                cv2.imwrite(filename, image)
                print(f"Selfie saved as {filename}")
                
                # Play sound
                try:
                    winsound.PlaySound("sound.wav", winsound.SND_FILENAME)
                except:
                    print("Sound file not found or couldn't be played")
                
                # Update last selfie time
                last_selfie_time = current_time
    
    # Display instruction
    cv2.putText(image, "Smile to take a selfie! Press ESC to exit", 
                (10, fh - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Show the image with minimal delay
    cv2.imshow("Auto Selfie for Smiling Faces using Python", image)
    
    # Check for ESC key press to exit with minimal delay
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key with minimal delay
        break

# Release resources
camera.release()
cv2.destroyAllWindows()