# virtual_painter.py
import cv2
import numpy as np

# Initialize variables
drawing = False
ix, iy = -1, -1
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255)]  # Red, Green, Blue, Yellow
current_color = colors[0]
brush_thickness = 5
canvas = None

def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, current_color, canvas
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.line(canvas, (ix, iy), (x, y), current_color, brush_thickness)
            ix, iy = x, y
            
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.line(canvas, (ix, iy), (x, y), current_color, brush_thickness)
        
    return x, y

def virtual_painter():
    global canvas, current_color, brush_thickness
    
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        canvas = np.zeros_like(frame)
    
    cv2.namedWindow("Virtual Painter")
    cv2.setMouseCallback("Virtual Painter", draw_circle)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Combine the frame and canvas
        combined = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)
        
        # Create color palette
        for i, color in enumerate(colors):
            cv2.rectangle(combined, (10 + i*40, 10), (40 + i*40, 40), color, -1)
            if color == current_color:
                cv2.rectangle(combined, (10 + i*40, 10), (40 + i*40, 40), (255, 255, 255), 2)
        
        # Show brush thickness
        cv2.putText(combined, f"Brush: {brush_thickness}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Clear button
        cv2.rectangle(combined, (10, 70), (90, 100), (0, 0, 0), -1)
        cv2.putText(combined, "Clear", (15, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Virtual Painter", combined)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('0'):
            current_color = colors[0]  # Red
        elif key == ord('1'):
            current_color = colors[1]  # Green
        elif key == ord('2'):
            current_color = colors[2]  # Blue
        elif key == ord('3'):
            current_color = colors[3]  # Yellow
        elif key == ord('+'):
            brush_thickness += 1
        elif key == ord('-'):
            brush_thickness = max(1, brush_thickness - 1)
        elif key == ord('c'):
            canvas = np.zeros_like(frame)
        elif key == ord('s'):
            cv2.imwrite("virtual_painting.jpg", canvas)
            print("Painting saved!")
        elif key == 27:  # ESC key
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    virtual_painter()
