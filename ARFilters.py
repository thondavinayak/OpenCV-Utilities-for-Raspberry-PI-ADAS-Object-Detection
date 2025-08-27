# ar_filters.py
import cv2
import numpy as np

def apply_sunglasses_filter(frame, faces):
    sunglasses = cv2.imread('sunglasses.png', cv2.IMREAD_UNCHANGED)
    
    for (x, y, w, h) in faces:
        # Calculate position for sunglasses
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Adjust size and position of sunglasses
        sw = w
        sh = int(0.3 * h)
        sy = y + int(0.25 * h)
        
        if sy + sh > frame.shape[0] or x + sw > frame.shape[1]:
            continue
            
        # Resize sunglasses
        sunglasses_resized = cv2.resize(sunglasses, (sw, sh))
        
        # Extract alpha channel
        alpha_s = sunglasses_resized[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        
        # Apply overlay
        for c in range(0, 3):
            frame[sy:sy+sh, x:x+sw, c] = (alpha_s * sunglasses_resized[:, :, c] + 
                                         alpha_l * frame[sy:sy+sh, x:x+sw, c])
    
    return frame

def apply_dog_filter(frame, faces):
    dog_nose = cv2.imread('dog_nose.png', cv2.IMREAD_UNCHANGED)
    dog_ears = cv2.imread('dog_ears.png', cv2.IMREAD_UNCHANGED)
    
    for (x, y, w, h) in faces:
        # Calculate position for dog nose
        nose_w = int(w * 0.3)
        nose_h = int(h * 0.2)
        nose_x = x + int(w * 0.35)
        nose_y = y + int(h * 0.6)
        
        # Resize and apply dog nose
        if nose_x + nose_w < frame.shape[1] and nose_y + nose_h < frame.shape[0]:
            nose_resized = cv2.resize(dog_nose, (nose_w, nose_h))
            alpha_s = nose_resized[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s
            
            for c in range(0, 3):
                frame[nose_y:nose_y+nose_h, nose_x:nose_x+nose_w, c] = (
                    alpha_s * nose_resized[:, :, c] + 
                    alpha_l * frame[nose_y:nose_y+nose_h, nose_x:nose_x+nose_w, c]
                )
        
        # Calculate position for dog ears
        ears_w = int(w * 1.2)
        ears_h = int(h * 0.8)
        ears_x = x - int(w * 0.1)
        ears_y = y - int(h * 0.5)
        
        # Resize and apply dog ears
        if ears_x + ears_w < frame.shape[1] and ears_y + ears_h < frame.shape[0] and ears_x >= 0 and ears_y >= 0:
            ears_resized = cv2.resize(dog_ears, (ears_w, ears_h))
            alpha_s = ears_resized[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s
            
            for c in range(0, 3):
                frame[ears_y:ears_y+ears_h, ears_x:ears_x+ears_w, c] = (
                    alpha_s * ears_resized[:, :, c] + 
                    alpha_l * frame[ears_y:ears_y+ears_h, ears_x:ears_x+ears_w, c]
                )
    
    return frame

def ar_filters():
    global gray
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    
    current_filter = "sunglasses"
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if current_filter == "sunglasses":
            frame = apply_sunglasses_filter(frame, faces)
        elif current_filter == "dog":
            frame = apply_dog_filter(frame, faces)
        
        # Display instructions
        cv2.putText(frame, "Press 's' for Sunglasses, 'd' for Dog filter, 'ESC' to exit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Current filter: {current_filter}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('AR Filters', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            current_filter = "sunglasses"
        elif key == ord('d'):
            current_filter = "dog"
        elif key == 27:  # ESC key
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    ar_filters()
