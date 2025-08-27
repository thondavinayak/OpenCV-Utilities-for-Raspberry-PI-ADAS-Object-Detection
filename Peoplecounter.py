# people_counter.py
import cv2
import numpy as np

class PeopleCounter:
    def __init__(self):
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.people_count = 0
        self.centroids = []
        self.max_disappeared = 50
        self.disappeared = {}
        self.next_object_id = 0
        
    def update(self, centroid):
        object_ids = list(self.disappeared.keys())
        object_centroids = [self.centroids[i] for i in object_ids]
        
        if len(object_centroids) == 0:
            for i in range(len(centroid)):
                self.disappeared[self.next_object_id] = 0
                self.centroids[self.next_object_id] = centroid[i]
                self.next_object_id += 1
                self.people_count += 1
        else:
            pass  # Simplified version - in practice you'd implement tracking logic
        
        return self.people_count

    def count_people(self, frame):
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(frame)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        centroids = []
        for contour in contours:
            # Filter small contours
            if cv2.contourArea(contour) < 500:
                continue
                
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate centroid
            centroid_x = int(x + w/2)
            centroid_y = int(y + h/2)
            centroids.append((centroid_x, centroid_y))
            
            # Draw bounding box and centroid
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(frame, (centroid_x, centroid_y), 4, (0, 0, 255), -1)
        
        # Update count
        count = self.update(centroids)
        
        # Display count
        cv2.putText(frame, f"People Count: {count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return frame, count

def people_counter():
    cap = cv2.VideoCapture(0)
    counter = PeopleCounter()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame, count = counter.count_people(frame)
        
        cv2.imshow("People Counter", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    people_counter()
