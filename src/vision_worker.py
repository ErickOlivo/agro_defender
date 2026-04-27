import cv2
import mediapipe as mp
import threading
from src.config import CAMERA_INDEX, WINDOW_WIDTH, WINDOW_HEIGHT, CV_DETECTION_CONFIDENCE, CV_TRACKING_CONFIDENCE
from src.utils.math_utils import map_coordinates

class VisionWorker(threading.Thread):
    """
    A background thread that continuously reads the webcam and processes
    hand tracking using MediaPipe, without blocking the main Pygame loop.
    """
    def __init__(self):
        super().__init__()
        # Daemon threads exit automatically when the main program closes
        self.daemon = True 
        self.running = True
        
        # Shared variables (read by the GameBroker)
        self.hand_x = WINDOW_WIDTH // 2
        self.hand_y = WINDOW_HEIGHT // 2
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1, # Tracking just 1 hand for optimal performance first
            min_detection_confidence=CV_DETECTION_CONFIDENCE,
            min_tracking_confidence=CV_TRACKING_CONFIDENCE
        )

    def run(self):
        """The main loop of the thread."""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        
        while self.running and cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue
            
            # Flip horizontally for a natural 'mirror' effect
            frame = cv2.flip(frame, 1)
            
            # MediaPipe requires RGB images, OpenCV uses BGR by default
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the image
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Extract landmark 9 (Middle Finger MCP - center of palm)
                    normalized_x = hand_landmarks.landmark[9].x
                    normalized_y = hand_landmarks.landmark[9].y
                    
                    # Map to screen dimensions
                    screen_x, screen_y = map_coordinates(
                        normalized_x, normalized_y, WINDOW_WIDTH, WINDOW_HEIGHT
                    )
                    
                    # Safely update the shared state
                    self.hand_x = screen_x
                    self.hand_y = screen_y
                    
        cap.release()
        
    def stop(self):
        """Safely terminates the camera thread."""
        self.running = False
