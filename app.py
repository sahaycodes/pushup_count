import cv2
import numpy as np
import mediapipe as mp
from flask import Flask, render_template, Response, request,jsonify,make_response
from cam_check import check_camera #import other cam_checker code to check for camera

app = Flask(__name__)


@app.route('/')
def index():
    resp=make_response(render_template('index.html'))
    #return render_template('index.html')
    resp.set_cookie('camera_access','requested',max_age=60*60*24)
    return resp

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# Check camera before starting the video feed
#if not check_camera():
    #print("Camera issues detected. Please check the camera connection, index, and permissions.")

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle


def gen_frames():
    # PUSHUP/CURL COUNTER Variables

    counter = 0
    stage = None
    
# Process frame for push-up detection


    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Video feed
    cap = cv2.VideoCapture(0)

    # Settingup instance of mediapipe
    with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            results = pose.process(image)
            #
            # Recolor back to BGR
            image.flags.writeable = True 
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Extract landmarks
            if results.pose_landmarks:
                try:
                    landmarks = results.pose_landmarks.landmark

                    # Get the relevant coordinates for the left side of the body 
                    #for a pushup we use the wrist/hand , elbow , shoulder and our hips to push against and make the 
                    #appropriate poses

                    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

                    # Get the relevant coordinates for the right side of the body
                    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]


                    # Calculate angles
                    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    left_hip_angle = calculate_angle(left_shoulder, left_hip, left_knee)
                    right_hip_angle = calculate_angle(right_shoulder, right_hip, right_knee)
                    

                    # Visualize data
                    cv2.putText(image, str(left_elbow_angle), 
                                tuple(np.multiply(left_elbow, [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, str(right_elbow_angle), 
                                tuple(np.multiply(right_elbow, [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, str(left_hip_angle), 
                                tuple(np.multiply(left_hip, [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, str(right_hip_angle), 
                                tuple(np.multiply(right_hip, [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    # Counter logic
                    if left_elbow_angle > 160 and right_elbow_angle > 160 and left_hip_angle > 160 and right_hip_angle > 160:
                        stage = 'down'
                    if left_elbow_angle < 30 and right_elbow_angle < 30 and left_hip_angle > 160 and right_hip_angle > 160 and stage == 'down':
                        stage = 'up'
                        counter += 1 #increases counter
                        print(counter)
                    
                except Exception as e:
                    print(f"Error: {e}")
            
            
            # Render the counter
            # Setup the counter box
            cv2.rectangle(image, (0, 0), (225, 85), (245, 125, 16), -1)
            
            # Push-uP data 
            cv2.putText(image, 'Reps', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Stage data
            cv2.putText(image, 'Stage', (75, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, stage, (75, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Render the detections
            
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                     mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                     mp_drawing.DrawingSpec(color=(245, 66, 240), thickness=2, circle_radius=2))
            
            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
    
    cap.release()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
