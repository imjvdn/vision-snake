import cv2
import numpy as np
import random
import time

class SnakeGame:
    """
    A class to handle the Snake game logic, including:
    - Snake movement
    - Food generation
    - Collision detection
    - Score tracking
    - Drawing the game elements on the screen
    """
    
    def __init__(self, game_width, game_height):
        """
        Initialize the Snake game.
        
        Args:
            game_width (int): Width of the game area
            game_height (int): Height of the game area
        """
        self.width = game_width
        self.height = game_height
        
        # Initialize snake properties
        self.snake_body = []
        self.max_length = 10  # Initial snake length
        self.score = 0
        self.game_over = False
        
        # Food properties
        self.food_pos = None
        self.food_radius = 15
        self.food_pulse_counter = 0  # For pulsating effect
        self.generate_food()
        
        # Colors based on score
        self.snake_colors = [
            (0, 255, 0),    # Green (score 0-5)
            (0, 255, 255),  # Yellow (score 6-10)
            (0, 165, 255),  # Orange (score 11-15)
            (0, 0, 255),    # Red (score 16+)
        ]
        
        # Game state
        self.last_update_time = time.time()
        self.update_interval = 0.05  # seconds between position updates
    
    def reset(self):
        """Reset the game to initial state"""
        self.snake_body = []
        self.max_length = 10
        self.score = 0
        self.game_over = False
        self.generate_food()
    
    def generate_food(self):
        """Generate food at a random position on the screen"""
        margin = 50  # Keep food away from the edges
        x = random.randint(margin, self.width - margin)
        y = random.randint(margin, self.height - margin)
        self.food_pos = (x, y)
    
    def update(self, head_pos):
        """
        Update the snake's position based on the head position.
        
        Args:
            head_pos (tuple): (x, y) coordinates of the snake's head
            
        Returns:
            bool: True if the game is still running, False if game over
        """
        if self.game_over or head_pos is None:
            return False
        
        current_time = time.time()
        force_update = False
        
        # For testing purposes, we'll force an update if the snake body is empty
        # or if we're in a test environment (no time-based throttling)
        if len(self.snake_body) == 0 or (current_time - self.last_update_time >= self.update_interval):
            force_update = True
            self.last_update_time = current_time
        
        # Update position if it's time or forced
        if force_update:
            # First, check if the snake has eaten the food
            # This needs to happen BEFORE collision detection to prevent false positives
            food_eaten = False
            if self.food_pos and head_pos:
                distance = np.sqrt((head_pos[0] - self.food_pos[0])**2 + 
                                 (head_pos[1] - self.food_pos[1])**2)
                
                if distance < self.food_radius + 10:  # +10 for snake head radius
                    self.score += 1
                    self.max_length += 5  # Increase snake length
                    self.generate_food()
                    food_eaten = True
                    
                    # Speed up the game slightly as score increases
                    self.update_interval = max(0.03, 0.05 - self.score * 0.001)
            
            # Add new head position to the snake body
            self.snake_body.append(head_pos)
            
            # Limit the snake length
            if len(self.snake_body) > self.max_length:
                self.snake_body = self.snake_body[-self.max_length:]
            
            # Check for collision with itself ONLY if not eating food
            # This prevents false collision detection when collecting food
            if not food_eaten and len(self.snake_body) >= 6:  # Only check if snake is long enough
                head = self.snake_body[-1]
                # Check against all body parts except the last 5 (near the head)
                for i in range(len(self.snake_body) - 6):
                    body_part = self.snake_body[i]
                    distance = np.sqrt((head[0] - body_part[0])**2 + 
                                     (head[1] - body_part[1])**2)
                    if distance < 10:  # Reduced collision threshold for better gameplay
                        self.game_over = True
                        return False
        
        return not self.game_over  # Return False if game is over, True otherwise
    
    def draw(self, frame):
        """
        Draw the snake, food, and score on the frame.
        
        Args:
            frame (numpy.ndarray): The frame to draw on
            
        Returns:
            numpy.ndarray: The frame with game elements drawn
        """
        # Draw snake body with danger highlighting
        if len(self.snake_body) > 0:
            # Determine snake color based on score
            color_index = min(self.score // 5, len(self.snake_colors) - 1)
            snake_color = self.snake_colors[color_index]
            
            # First, draw danger zones around the snake body (things to avoid)
            for i in range(len(self.snake_body) - 5):  # Skip the last 5 segments (near head)
                position = self.snake_body[i]
                # Draw a semi-transparent danger zone
                danger_overlay = frame.copy()
                cv2.circle(danger_overlay, position, 15, (0, 0, 200), 2)  # Red danger circle
                cv2.addWeighted(danger_overlay, 0.3, frame, 0.7, 0, frame)
            
            # Draw each segment of the snake with better visibility
            for i, position in enumerate(self.snake_body):
                # Make the segments larger toward the head
                radius = 5 + (i / len(self.snake_body)) * 5
                if i == len(self.snake_body) - 1:  # Head
                    # Draw the head with a highlight
                    cv2.circle(frame, position, 12, (255, 255, 255), 2)  # White outline
                    cv2.circle(frame, position, 10, snake_color, cv2.FILLED)
                else:  # Body
                    cv2.circle(frame, position, int(radius), snake_color, cv2.FILLED)
                    # Add a darker border to make it stand out
                    cv2.circle(frame, position, int(radius), (snake_color[0]//2, snake_color[1]//2, snake_color[2]//2), 1)
            
            # Connect snake segments with lines for a smoother appearance
            for i in range(1, len(self.snake_body)):
                if i > 0:
                    cv2.line(frame, self.snake_body[i-1], self.snake_body[i], 
                             snake_color, thickness=max(5, int(5 + (i / len(self.snake_body)) * 5)))
        
        # Draw food with attention-grabbing effects (things to collect)
        if self.food_pos:
            # Create pulsating effect for food
            self.food_pulse_counter = (self.food_pulse_counter + 1) % 30
            pulse_size = self.food_radius + 3 * np.sin(self.food_pulse_counter * 0.2)
            
            # Draw attention-grabbing circles around food
            cv2.circle(frame, self.food_pos, int(pulse_size + 10), (0, 140, 255), 2)  # Outer orange circle
            cv2.circle(frame, self.food_pos, int(pulse_size + 5), (0, 215, 255), 2)   # Middle yellow circle
            
            # Draw the food itself (bright red)
            cv2.circle(frame, self.food_pos, int(pulse_size), (0, 0, 255), cv2.FILLED)
            
            # Add a white border and highlight to make it more visible
            cv2.circle(frame, self.food_pos, int(pulse_size), (255, 255, 255), 2)
            
            # Add "COLLECT" text near the food
            cv2.putText(frame, "COLLECT", 
                       (self.food_pos[0] - 40, self.food_pos[1] - int(pulse_size) - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
        
        # Draw score with better visibility
        score_text = f"Score: {self.score}"
        # Draw text with black outline for better visibility
        cv2.putText(frame, score_text, (11, 31), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 0, 0), 4, cv2.LINE_AA)  # Thicker black outline
        cv2.putText(frame, score_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255, 255, 255), 2, cv2.LINE_AA)  # White text
        
        # Draw game over message if game is over
        if self.game_over:
            # Create a semi-transparent overlay for the game over message
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)  # 50% transparency
            
            # Draw a red border around the screen
            cv2.rectangle(frame, (10, 10), (self.width-10, self.height-10), (0, 0, 255), 5)
            
            # Draw "GAME OVER!" with a glowing effect
            game_over_text = "GAME OVER!"
            text_size = cv2.getTextSize(game_over_text, cv2.FONT_HERSHEY_DUPLEX, 2, 2)[0]
            text_x = int(self.width/2 - text_size[0]/2)
            text_y = int(self.height/2)
            
            # Draw outer glow effect
            for offset in range(5, 0, -1):
                cv2.putText(frame, game_over_text, 
                           (text_x-offset, text_y), 
                           cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 50+offset*40), 2, cv2.LINE_AA)
            
            # Draw main text
            cv2.putText(frame, game_over_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
            
            # Draw score with enhanced visibility
            score_text = f"Final Score: {self.score}"
            score_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            score_x = int(self.width/2 - score_size[0]/2)
            
            cv2.putText(frame, score_text, (score_x+1, text_y+50+1), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 4, cv2.LINE_AA)  # Shadow
            cv2.putText(frame, score_text, (score_x, text_y+50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Draw instruction with animated effect (pulsating)
            instruction = "Show open palm to restart"
            pulse = int(5 * np.sin(time.time() * 5) + 5)  # Pulsating effect
            inst_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            inst_x = int(self.width/2 - inst_size[0]/2)
            
            # Draw with yellow highlight
            cv2.putText(frame, instruction, (inst_x+1, text_y+110+1), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv2.LINE_AA)  # Shadow
            cv2.putText(frame, instruction, (inst_x, text_y+110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255-pulse*10, 255), 2, cv2.LINE_AA)
        
        return frame
