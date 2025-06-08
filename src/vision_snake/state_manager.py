"""
Game State Manager for Vision Snake.

This module provides a state management system to handle different game states
such as menu, playing, paused, and game over. It separates game logic from
rendering and input handling, making state transitions cleaner and more maintainable.
"""

from abc import ABC, abstractmethod
import cv2
import numpy as np
import time
from vision_snake.snake_game import SnakeGame


class GameState(ABC):
    """Abstract base class for all game states."""
    
    def __init__(self, state_manager, game_width, game_height):
        """
        Initialize the game state.
        
        Args:
            state_manager: The StateManager instance that manages this state
            game_width: Width of the game area
            game_height: Height of the game area
        """
        self.state_manager = state_manager
        self.width = game_width
        self.height = game_height
    
    @abstractmethod
    def update(self, hand_landmarks, finger_pos):
        """
        Update the state based on input.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            finger_pos: Position of the index finger
            
        Returns:
            None
        """
        pass
    
    @abstractmethod
    def render(self, frame):
        """
        Render the state on the frame.
        
        Args:
            frame: The frame to render on
            
        Returns:
            The rendered frame
        """
        pass
    
    @abstractmethod
    def handle_key(self, key):
        """
        Handle keyboard input.
        
        Args:
            key: The key code
            
        Returns:
            True if the game should continue, False if it should exit
        """
        pass


class MenuState(GameState):
    """State for the main menu."""
    
    def __init__(self, state_manager, game_width, game_height):
        super().__init__(state_manager, game_width, game_height)
        self.options = ["Start Game", "Settings", "Exit"]
        self.selected_option = 0
        self.selection_cooldown = 0
        self.pulse_value = 0
        
    def update(self, hand_landmarks, finger_pos):
        # Update pulse effect for visual feedback
        self.pulse_value = (self.pulse_value + 0.1) % (2 * np.pi)
        
        # Handle selection cooldown
        if self.selection_cooldown > 0:
            self.selection_cooldown -= 1
            return
            
        if finger_pos is None:
            return
            
        # Check if finger is pointing at an option
        x, y = finger_pos
        option_height = 60
        option_start_y = self.height // 2 - len(self.options) * option_height // 2
        
        for i, option in enumerate(self.options):
            option_y = option_start_y + i * option_height
            if option_y - 20 <= y <= option_y + 20:
                if i != self.selected_option:
                    self.selected_option = i
                    self.selection_cooldown = 10  # Prevent rapid selection changes
                break
        
        # Check if finger is held on an option (selection gesture)
        if hand_landmarks and finger_pos:
            # Simple selection: hold finger in place for a moment
            # In a real implementation, you might want a more sophisticated gesture
            if self.selection_cooldown == 0:
                # Detect if finger is stationary for selection
                # For now, just a placeholder for a more sophisticated gesture detection
                if self.selected_option == 0:  # Start Game
                    self.state_manager.change_state("playing")
                elif self.selected_option == 1:  # Settings
                    # Would transition to settings state in a full implementation
                    pass
                elif self.selected_option == 2:  # Exit
                    return False
    
    def render(self, frame):
        # Create a semi-transparent overlay for the menu background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)  # 70% opacity
        
        # Draw game title with glow effect
        title = "VISION SNAKE"
        title_scale = 2.0
        title_thickness = 2
        title_font = cv2.FONT_HERSHEY_DUPLEX
        
        title_size = cv2.getTextSize(title, title_font, title_scale, title_thickness)[0]
        title_x = int(self.width/2 - title_size[0]/2)
        title_y = int(self.height/4)
        
        # Draw glow effect
        glow_color = (0, int(100 + 50 * np.sin(self.pulse_value)), 255)
        for offset in range(5, 0, -1):
            cv2.putText(frame, title, 
                       (title_x-offset, title_y), 
                       title_font, title_scale, (0, 0, 50+offset*40), title_thickness, cv2.LINE_AA)
        
        # Draw main title
        cv2.putText(frame, title, (title_x, title_y), 
                   title_font, title_scale, (0, 200, 255), title_thickness, cv2.LINE_AA)
        
        # Draw menu options
        option_font = cv2.FONT_HERSHEY_SIMPLEX
        option_scale = 1.0
        option_thickness = 2
        option_height = 60
        option_start_y = self.height // 2 - len(self.options) * option_height // 2
        
        for i, option in enumerate(self.options):
            option_size = cv2.getTextSize(option, option_font, option_scale, option_thickness)[0]
            option_x = int(self.width/2 - option_size[0]/2)
            option_y = option_start_y + i * option_height
            
            # Highlight selected option
            if i == self.selected_option:
                # Pulsating highlight effect
                highlight_intensity = int(155 + 100 * np.sin(self.pulse_value))
                
                # Draw selection box
                box_padding = 20
                box_start = (option_x - box_padding, option_y - option_size[1] - box_padding)
                box_end = (option_x + option_size[0] + box_padding, option_y + box_padding)
                
                cv2.rectangle(frame, box_start, box_end, (0, highlight_intensity, 255), 2)
                
                # Draw the text with brighter color
                cv2.putText(frame, option, (option_x, option_y), 
                           option_font, option_scale, (0, 255, 255), option_thickness, cv2.LINE_AA)
            else:
                # Draw normal option
                cv2.putText(frame, option, (option_x, option_y), 
                           option_font, option_scale, (200, 200, 200), option_thickness, cv2.LINE_AA)
        
        # Draw instruction at the bottom
        instruction = "Point at an option and hold to select"
        inst_size = cv2.getTextSize(instruction, option_font, 0.7, 1)[0]
        inst_x = int(self.width/2 - inst_size[0]/2)
        inst_y = int(self.height * 0.85)
        
        cv2.putText(frame, instruction, (inst_x, inst_y), 
                   option_font, 0.7, (150, 150, 150), 1, cv2.LINE_AA)
        
        return frame
    
    def handle_key(self, key):
        # Handle keyboard navigation
        if key == ord('w') or key == ord('i') or key == 82:  # Up arrow
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == ord('s') or key == ord('k') or key == 84:  # Down arrow
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == 13 or key == 32:  # Enter or Space
            if self.selected_option == 0:  # Start Game
                self.state_manager.change_state("playing")
            elif self.selected_option == 1:  # Settings
                # Would transition to settings state in a full implementation
                pass
            elif self.selected_option == 2:  # Exit
                return False
        elif key == 27 or key == ord('q'):  # ESC or q
            return False
        
        return True


class PlayingState(GameState):
    """State for active gameplay."""
    
    def __init__(self, state_manager, game_width, game_height):
        super().__init__(state_manager, game_width, game_height)
        self.game = SnakeGame(game_width=game_width, game_height=game_height)
        
        # Variables for reset gesture detection
        self.palm_shown_start_time = None
        self.palm_duration_required = 2.0  # seconds to hold palm for reset
        
        # FPS calculation variables
        self.prev_time = 0
        self.curr_time = 0
        self.paused = False
    
    def update(self, hand_landmarks, finger_pos):
        if self.paused:
            return True
            
        # Check for reset gesture (open palm) when game is over
        if self.game.game_over and hand_landmarks:
            self._check_reset_gesture(hand_landmarks)
        
        # Update the game state
        if finger_pos:
            self.game.update(finger_pos)
            
        # If game is over, consider transitioning to game over state
        if self.game.game_over:
            # We're keeping the game over screen in the snake_game.py for now
            # In a full implementation, you might want to transition to a GameOverState
            pass
            
        # Calculate FPS
        self.curr_time = time.time()
        if self.prev_time == 0:  # First frame
            self.prev_time = self.curr_time
        
        return True
    
    def render(self, frame):
        # Draw the game elements
        frame = self.game.draw(frame)
        
        # Calculate and display FPS
        fps = 0
        if self.prev_time > 0 and self.curr_time > self.prev_time:
            fps = 1 / (self.curr_time - self.prev_time)
            # Update prev_time for next frame's calculation
            self.prev_time = self.curr_time
        
        cv2.putText(frame, f"FPS: {int(fps)}", (self.width - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw pause indicator if paused
        if self.paused:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
            
            pause_text = "PAUSED"
            text_size = cv2.getTextSize(pause_text, cv2.FONT_HERSHEY_DUPLEX, 2, 2)[0]
            text_x = int(self.width/2 - text_size[0]/2)
            text_y = int(self.height/2)
            
            cv2.putText(frame, pause_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            
            resume_text = "Press 'P' to resume"
            resume_size = cv2.getTextSize(resume_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)[0]
            resume_x = int(self.width/2 - resume_size[0]/2)
            resume_y = text_y + 50
            
            cv2.putText(frame, resume_text, (resume_x, resume_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 1, cv2.LINE_AA)
            
            menu_text = "Press 'M' for menu"
            menu_size = cv2.getTextSize(menu_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)[0]
            menu_x = int(self.width/2 - menu_size[0]/2)
            menu_y = resume_y + 40
            
            cv2.putText(frame, menu_text, (menu_x, menu_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 1, cv2.LINE_AA)
        
        return frame
    
    def handle_key(self, key):
        if key == ord('p'):  # Toggle pause
            self.paused = not self.paused
        elif key == ord('m') and self.paused:  # Return to menu (only when paused)
            self.state_manager.change_state("menu")
        elif key == ord('r'):  # Reset game
            self.game.reset()
        elif key == 27 or key == ord('q'):  # ESC or q
            return False
        
        return True
    
    def _check_reset_gesture(self, hand_landmarks):
        """Check for open palm reset gesture"""
        # Get all finger landmarks
        landmarks = hand_landmarks.landmark
        
        # Check if all fingers are extended (simple open palm detection)
        # MediaPipe hand landmarks: thumb tip (4), index tip (8), middle tip (12), 
        # ring tip (16), pinky tip (20), wrist (0)
        finger_tips = [4, 8, 12, 16, 20]
        wrist_y = landmarks[0].y
        
        # Count extended fingers (fingers whose tips are higher than the wrist)
        extended_fingers = sum(1 for tip_idx in finger_tips 
                             if landmarks[tip_idx].y < wrist_y)
        
        # If all fingers are extended (open palm)
        if extended_fingers >= 4:
            if self.palm_shown_start_time is None:
                self.palm_shown_start_time = time.time()
            elif time.time() - self.palm_shown_start_time > self.palm_duration_required:
                # Reset the game
                self.game.reset()
                self.palm_shown_start_time = None
        else:
            self.palm_shown_start_time = None


class StateManager:
    """
    Manages game states and transitions between them.
    """
    
    def __init__(self, game_width, game_height):
        """
        Initialize the state manager.
        
        Args:
            game_width: Width of the game area
            game_height: Height of the game area
        """
        self.game_width = game_width
        self.game_height = game_height
        self.states = {}
        self.current_state = None
    
    def add_state(self, name, state_class):
        """
        Add a state to the manager.
        
        Args:
            name: Name of the state
            state_class: Class of the state
        """
        self.states[name] = state_class(self, self.game_width, self.game_height)
    
    def change_state(self, name):
        """
        Change to a different state.
        
        Args:
            name: Name of the state to change to
        """
        if name in self.states:
            self.current_state = self.states[name]
        else:
            raise ValueError(f"State '{name}' does not exist")
    
    def update(self, hand_landmarks, finger_pos):
        """
        Update the current state.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            finger_pos: Position of the index finger
            
        Returns:
            True if the game should continue, False if it should exit
        """
        if self.current_state:
            return self.current_state.update(hand_landmarks, finger_pos)
        return True
    
    def render(self, frame):
        """
        Render the current state.
        
        Args:
            frame: The frame to render on
            
        Returns:
            The rendered frame
        """
        if self.current_state:
            return self.current_state.render(frame)
        return frame
    
    def handle_key(self, key):
        """
        Handle keyboard input for the current state.
        
        Args:
            key: The key code
            
        Returns:
            True if the game should continue, False if it should exit
        """
        if self.current_state:
            return self.current_state.handle_key(key)
        return True
