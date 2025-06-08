import cv2
import numpy as np
import time
import mediapipe as mp
from vision_snake.hand_tracker import HandTracker
from vision_snake.snake_game import SnakeGame
from vision_snake.state_manager import StateManager, MenuState, PlayingState

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
        
        # Initialize state manager with webcam dimensions
        self.state_manager = StateManager(game_width=self.frame_width, game_height=self.frame_height)
        
        # Add states
        self.state_manager.add_state("menu", MenuState)
        self.state_manager.add_state("playing", PlayingState)
        
        # Start with the menu state
        self.state_manager.change_state("menu")
        
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
        
        # Update the current state
        hand_landmarks = results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None
        self.state_manager.update(hand_landmarks, finger_pos)
        
        # Render the current state
        frame = self.state_manager.render(frame)
        
        # Calculate FPS
        self.curr_time = time.time()
        fps = 1 / (self.curr_time - self.prev_time) if self.prev_time > 0 else 0
        self.prev_time = self.curr_time
        
        return frame
    
    # The reset gesture detection is now handled in the PlayingState class
    
    def run(self):
        """Run the main game loop"""
        print("Starting Vision Snake Game...")
        print("Use your index finger to control the snake.")
        print("Show an open palm for 2 seconds to restart after game over.")
        print("Press 'p' to pause, 'm' to return to menu when paused.")
        print("Press 'q' or ESC to quit.")
        
        while True:
            frame = self.process_frame()
            if frame is None:
                print("Failed to read frame from webcam.")
                break
            
            # Display the frame
            cv2.imshow("Vision Snake Game", frame)
            
            # Check for key presses
            key = cv2.waitKey(1)
            if not self.state_manager.handle_key(key):
                break
        
        # Clean up
        self.cap.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        """Ensure resources are released when the object is destroyed"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
