import cv2

def check_camera():
    # Check if camera is connected and accessible
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return False
    
    # Check camera index
    if cap.get(cv2.CAP_PROP_FRAME_WIDTH) == 0 or cap.get(cv2.CAP_PROP_FRAME_HEIGHT) == 0:
        print("Error: Camera index may be out of range.")
        cap.release()
        return False
    
    # Check permissions
    _, frame = cap.read()
    if frame is None:
        print("Error: Insufficient permissions to access the camera.")
        cap.release()
        return False
    
    # Release the camera and return True if everything is fine
    cap.release()
    print("Camera is connected and accessible.")
    return True

if __name__ == "__main__":
    if check_camera():
        print("You can start using the camera in your application.")
    else:
        print("Please check the camera connection, index, and permissions.")
