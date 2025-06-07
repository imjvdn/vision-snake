import cv2
import numpy as np
import time
import mediapipe as mp
from vision_snake.hand_tracker import HandTracker
from vision_snake.snake_game import SnakeGame

class VisionSnakeGame:
    """
    Main game class that ties together hand tracking and snake game logic.
    """
    def __init__(self, camera_index=None):
        """Initialize the Vision Snake Game components"""
        # Initialize webcam based on camera_index parameter
        if camera_index is not None:
            # Use the specified camera index
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                print(f"Warning: Could not open camera with index {camera_index}")
                print("Falling back to auto-detection...")
                self.cap = None
        else:
            self.cap = None
        
        # If no camera was specified or the specified camera failed to open,
        # try to find a suitable camera automatically
        if self.cap is None:
            # First try the built-in webcam (usually index 0)
            self.cap = cv2.VideoCapture(0)
            
            # If that didn't work, try other indices
            if not self.cap.isOpened():
                for i in range(1, 3):  # Try indices 1, 2
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        self.cap = cap
                        print(f"Found camera at index {i}")
                        break
                    cap.release()
        
        # Get webcam dimensions
        success, frame = self.cap.read()
        if not success:
            raise RuntimeError("Failed to access webcam. Please check your camera connection.")
        
        self.frame_height, self.frame_width, _ = frame.shape
        
        # Initialize hand tracker
        self.hand_tracker = HandTracker(detection_confidence=0.7, tracking_confidence=0.5)
        
        # Initialize snake game with webcam dimensions
        self.game = SnakeGame(game_width=self.frame_width, game_height=self.frame_height)
        
        # Variables for reset gesture detection
        self.palm_shown_start_time = None
        self.palm_duration_required = 2.0  # seconds to hold palm for reset
        
        # FPS calculation variables
        self.prev_time = 0
        self.curr_time = 0
    
    def process_frame(self):
        """Process a single frame from the webcam"""
        # Read frame from webcam
        success, frame = self.cap.read()
        if not success:
            return None
        
        # Flip the frame horizontally for a more intuitive mirror view
        frame = cv2.flip(frame, 1)
        
        # Process the frame with hand tracker
        frame, results = self.hand_tracker.find_hands(frame)
        
        # Get index finger position
        finger_pos, frame = self.hand_tracker.get_index_finger_position(frame, results, draw=True)
        
        # Check for reset gesture (open palm) when game is over
        if self.game.game_over and results.multi_hand_landmarks:
            self._check_reset_gesture(frame, results)
        
        # Update and draw the game
        if finger_pos:
            self.game.update(finger_pos)
        frame = self.game.draw(frame)
        
        # Calculate and display FPS
        self.curr_time = time.time()
        fps = 1 / (self.curr_time - self.prev_time) if self.prev_time > 0 else 0
        self.prev_time = self.curr_time
        
        cv2.putText(frame, f"FPS: {int(fps)}", (self.frame_width - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def _check_reset_gesture(self, frame, results):
        """Check for open palm reset gesture"""
        # Get all finger landmarks
        hand_landmarks = results.multi_hand_landmarks[0].landmark
        
        # Check if all fingers are extended (simple open palm detection)
        # MediaPipe hand landmarks: thumb tip (4), index tip (8), middle tip (12), 
        # ring tip (16), pinky tip (20), wrist (0)
        finger_tips = [4, 8, 12, 16, 20]
        wrist_y = hand_landmarks[0].y
        
        # Count extended fingers (fingers whose tips are higher than the wrist)
        extended_fingers = sum(1 for tip_idx in finger_tips 
                             if hand_landmarks[tip_idx].y < wrist_y)
        
        # If all fingers are extended (open palm)
        if extended_fingers >= 4:
            if self.palm_shown_start_time is None:
                self.palm_shown_start_time = time.time()
            elif time.time() - self.palm_shown_start_time > self.palm_duration_required:
                # Reset the game
                self.game.reset()
                self.palm_shown_start_time = None
            
            # Draw a progress bar for reset gesture
            elapsed = time.time() - self.palm_shown_start_time if self.palm_shown_start_time else 0
            progress = min(elapsed / self.palm_duration_required, 1.0)
            bar_width = int(200 * progress)
            cv2.rectangle(frame, (self.frame_width//2-100, self.frame_height//2+120), 
                         (self.frame_width//2-100+bar_width, self.frame_height//2+140), 
                         (0, 255, 0), cv2.FILLED)
            cv2.rectangle(frame, (self.frame_width//2-100, self.frame_height//2+120), 
                         (self.frame_width//2+100, self.frame_height//2+140), 
                         (255, 255, 255), 2)
        else:
            self.palm_shown_start_time = None
    
    def run(self):
        """Run the main game loop"""
        while True:
            frame = self.process_frame()
            if frame is None:
                print("Failed to read frame from webcam.")
                break
            
            # Display the frame
            cv2.imshow("Vision Snake Game", frame)
            
            # Check for exit key (ESC or 'q')
            key = cv2.waitKey(1)
            if key == 27 or key == ord('q'):
                break
        
        # Clean up
        self.cap.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        """Ensure resources are released when the object is destroyed"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
