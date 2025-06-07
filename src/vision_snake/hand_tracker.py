import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    """
    A class to handle hand tracking using MediaPipe.
    Tracks the position of the index finger tip in real-time.
    """
    
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initialize the hand tracker with MediaPipe Hands.
        
        Args:
            detection_confidence (float): Confidence threshold for hand detection
            tracking_confidence (float): Confidence threshold for hand tracking
        """
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Track only one hand for simplicity
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Store the previous index finger position to handle tracking loss
        self.prev_index_finger_pos = None
    
    def find_hands(self, frame):
        """
        Process a frame and detect hands.
        
        Args:
            frame (numpy.ndarray): The input frame from the webcam
            
        Returns:
            frame (numpy.ndarray): The processed frame with hand landmarks drawn
            results: MediaPipe hand detection results
        """
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe Hands
        results = self.hands.process(frame_rgb)
        
        return frame, results
    
    def get_index_finger_position(self, frame, results, draw=True):
        """
        Extract the position of the index finger tip from the detection results.
        
        Args:
            frame (numpy.ndarray): The input frame
            results: MediaPipe hand detection results
            draw (bool): Whether to draw hand landmarks on the frame
            
        Returns:
            tuple: (x, y) coordinates of the index finger tip, or None if not detected
            frame (numpy.ndarray): The frame with hand landmarks drawn (if draw=True)
        """
        h, w, c = frame.shape
        index_finger_pos = None
        
        if results.multi_hand_landmarks:
            # We're only tracking one hand (max_num_hands=1)
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw hand landmarks if requested
            if draw:
                self.mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS
                )
            
            # Get index finger tip coordinates (landmark 8 in MediaPipe Hands)
            index_finger = hand_landmarks.landmark[8]
            
            # Convert normalized coordinates to pixel coordinates
            x, y = int(index_finger.x * w), int(index_finger.y * h)
            index_finger_pos = (x, y)
            
            # Draw a circle at the index finger tip
            if draw:
                cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)
            
            # Update the previous position
            self.prev_index_finger_pos = index_finger_pos
        else:
            # If no hand is detected, return the previous position
            index_finger_pos = self.prev_index_finger_pos
        
        return index_finger_pos, frame
