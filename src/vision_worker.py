import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading
from src.config import CAMERA_INDEX, WINDOW_WIDTH, WINDOW_HEIGHT, CV_DETECTION_CONFIDENCE, CV_TRACKING_CONFIDENCE
from src.utils.math_utils import map_coordinates

class VisionWorker(threading.Thread):
    """
    A background thread that continuously reads the webcam and processes
    hand tracking using the modern MediaPipe Tasks API.
    """
    def __init__(self):
        super().__init__()
        self.daemon = True 
        self.running = True
        
        self.hand_x = WINDOW_WIDTH // 2
        self.hand_y = WINDOW_HEIGHT // 2
        
        # ==========================================
        # NEW: MediaPipe Tasks API Configuration
        # ==========================================
        base_options = python.BaseOptions(model_asset_path='src/hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=CV_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=CV_DETECTION_CONFIDENCE,
            min_tracking_confidence=CV_TRACKING_CONFIDENCE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def run(self):
        """The main loop of the thread."""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        
        while self.running and cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue
            
            # Flip horizontally for a natural 'mirror' effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert OpenCV image to MediaPipe Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Perform hand landmark detection
            detection_result = self.detector.detect(mp_image)
            
            # If hands are detected, extract the coordinates
            if detection_result.hand_landmarks:
                # Extract landmark 9 (Middle Finger MCP - center of palm)
                # Note: hand_landmarks is a list of hands, we take the first one [0]
                hand = detection_result.hand_landmarks[0]
                normalized_x = hand[9].x
                normalized_y = hand[9].y
                
                screen_x, screen_y = map_coordinates(
                    normalized_x, normalized_y, WINDOW_WIDTH, WINDOW_HEIGHT
                )
                
                self.hand_x = screen_x
                self.hand_y = screen_y
                    
        cap.release()
        
    def stop(self):
        """Safely terminates the camera thread."""
        self.running = False
