import cv2
import math  # <-- NUEVO: Necesario para calcular distancias (math.hypot)
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
        self.is_fist = False
        
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
                # Note: hand_landmarks is a list of hands, we take the first one [0]
                hand = detection_result.hand_landmarks[0]
                
                # Extract landmark 9 (Middle Finger MCP - center of palm)
                normalized_x = hand[9].x
                normalized_y = hand[9].y
                
                screen_x, screen_y = map_coordinates(
                    normalized_x, normalized_y, WINDOW_WIDTH, WINDOW_HEIGHT
                )
                
                self.hand_x = screen_x
                self.hand_y = screen_y
                
                # ==========================================
                # NUEVA LÓGICA: DETECCIÓN DE PUÑO CERRADO
                # ==========================================
                wrist = hand[0] # Muñeca
                
                def is_finger_curled(tip_idx, pip_idx):
                    """
                    Compara la distancia de la punta del dedo (tip) a la muñeca
                    vs la articulación intermedia (pip) a la muñeca.
                    Si la punta está más cerca, el dedo está encogido.
                    """
                    tip = hand[tip_idx]
                    pip = hand[pip_idx]
                    dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
                    dist_pip = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
                    return dist_tip < dist_pip

                # Revisamos: Índice(8,6), Medio(12,10), Anular(16,14) y Meñique(20,18)
                fingers_curled = [
                    is_finger_curled(8, 6),
                    is_finger_curled(12, 10),
                    is_finger_curled(16, 14),
                    is_finger_curled(20, 18)
                ]
                
                # Si los 4 dedos principales están encogidos, es un puño
                self.is_fist = all(fingers_curled)
                
            else:
                # Si no se detecta ninguna mano, no hay puño
                self.is_fist = False
                    
        cap.release()
        
    def stop(self):
        """Safely terminates the camera thread."""
        self.running = False
