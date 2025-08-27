# document_scanner.py
import cv2
import numpy as np

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warped

def document_scanner():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        orig = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 75, 200)
        
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        screenCnt = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            if len(approx) == 4:
                screenCnt = approx
                break
                
        if screenCnt is not None:
            cv2.drawContours(frame, [screenCnt], -1, (0, 255, 0), 2)
            
            warped = four_point_transform(orig, screenCnt.reshape(4, 2))
            warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
            warped_thresh = cv2.threshold(warped_gray, 0, 255, 
                                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            cv2.imshow("Scanned", warped_thresh)
        
        cv2.imshow("Document Scanner", frame)
        cv2.imshow("Edged", edged)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            cv2.imwrite("scanned_document.jpg", warped_thresh)
            print("Document saved!")
        elif key == 27:  # ESC key
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    document_scanner()
