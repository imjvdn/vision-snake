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
        
        # Check for collision with existing body parts before adding the new head position
        # This is important for tests where we're explicitly testing collision detection
        if len(self.snake_body) >= 5:  # Only check if snake is long enough
            # Check if the new head position collides with any existing body part
            for i, body_part in enumerate(self.snake_body[:-1] if self.snake_body else []):
                if head_pos == body_part:  # Exact match for test cases
                    self.game_over = True
                    return False
                
                # Also check for proximity-based collisions
                distance = np.sqrt((head_pos[0] - body_part[0])**2 + 
                                 (head_pos[1] - body_part[1])**2)
                if distance < 15:  # Collision threshold
                    self.game_over = True
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
            # Add new head position to the snake body
            self.snake_body.append(head_pos)
            
            # Check if the snake has eaten the food
            if self.food_pos and head_pos:
                distance = np.sqrt((head_pos[0] - self.food_pos[0])**2 + 
                                 (head_pos[1] - self.food_pos[1])**2)
                
                if distance < self.food_radius + 10:  # +10 for snake head radius
                    self.score += 1
                    self.max_length += 5  # Increase snake length
                    self.generate_food()
                    
                    # Speed up the game slightly as score increases
                    self.update_interval = max(0.03, 0.05 - self.score * 0.001)
            
            # Limit the snake length
            if len(self.snake_body) > self.max_length:
                self.snake_body = self.snake_body[-self.max_length:]
        
        return not self.game_over  # Return False if game is over, True otherwise
    
    def draw(self, frame):
        """
        Draw the snake, food, and score on the frame.
        
        Args:
            frame (numpy.ndarray): The frame to draw on
            
        Returns:
            numpy.ndarray: The frame with game elements drawn
        """
        # Draw snake body
        if len(self.snake_body) > 0:
            # Determine snake color based on score
            color_index = min(self.score // 5, len(self.snake_colors) - 1)
            snake_color = self.snake_colors[color_index]
            
            # Draw each segment of the snake
            for i, position in enumerate(self.snake_body):
                # Make the segments larger toward the head
                radius = 5 + (i / len(self.snake_body)) * 5
                if i == len(self.snake_body) - 1:  # Head
                    cv2.circle(frame, position, 10, snake_color, cv2.FILLED)
                else:  # Body
                    cv2.circle(frame, position, int(radius), snake_color, cv2.FILLED)
            
            # Connect snake segments with lines for a smoother appearance
            for i in range(1, len(self.snake_body)):
                if i > 0:
                    cv2.line(frame, self.snake_body[i-1], self.snake_body[i], 
                             snake_color, thickness=max(5, int(5 + (i / len(self.snake_body)) * 5)))
        
        # Draw food
        if self.food_pos:
            cv2.circle(frame, self.food_pos, self.food_radius, (0, 0, 255), cv2.FILLED)
            # Add a white border to make it more visible
            cv2.circle(frame, self.food_pos, self.food_radius, (255, 255, 255), 2)
        
        # Draw score
        score_text = f"Score: {self.score}"
        cv2.putText(frame, score_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Draw game over message if game is over
        if self.game_over:
            cv2.putText(frame, "GAME OVER!", (int(self.width/2) - 100, int(self.height/2)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
            cv2.putText(frame, f"Final Score: {self.score}", (int(self.width/2) - 100, int(self.height/2) + 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "Show open palm to restart", (int(self.width/2) - 150, int(self.height/2) + 80), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        return frame
