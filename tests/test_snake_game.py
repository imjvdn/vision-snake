import unittest
import numpy as np
from vision_snake.snake_game import SnakeGame

class TestSnakeGame(unittest.TestCase):
    """Test cases for the SnakeGame class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game_width = 640
        self.game_height = 480
        self.game = SnakeGame(self.game_width, self.game_height)
    
    def test_initialization(self):
        """Test that the game initializes correctly"""
        self.assertEqual(self.game.width, self.game_width)
        self.assertEqual(self.game.height, self.game_height)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(len(self.game.snake_body), 0)
        self.assertFalse(self.game.game_over)
        self.assertIsNotNone(self.game.food_pos)
    
    def test_reset(self):
        """Test that the game resets correctly"""
        # Add some snake body parts and increase score
        self.game.snake_body = [(100, 100), (110, 100), (120, 100)]
        self.game.score = 5
        self.game.game_over = True
        
        # Reset the game
        self.game.reset()
        
        # Check that everything is reset
        self.assertEqual(len(self.game.snake_body), 0)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_over)
        self.assertIsNotNone(self.game.food_pos)
    
    def test_food_generation(self):
        """Test that food is generated within bounds"""
        for _ in range(10):  # Test multiple food generations
            self.game.generate_food()
            x, y = self.game.food_pos
            
            # Check that food is within game bounds
            self.assertGreaterEqual(x, 0)
            self.assertLess(x, self.game_width)
            self.assertGreaterEqual(y, 0)
            self.assertLess(y, self.game_height)
    
    def test_collision_with_food(self):
        """Test that collision with food increases score and snake length"""
        # Set up a specific food position
        self.game.food_pos = (100, 100)
        initial_max_length = self.game.max_length
        
        # Move snake head to food position
        self.game.update((100, 100))
        
        # Check that score increased and max_length increased
        self.assertEqual(self.game.score, 1)
        self.assertEqual(self.game.max_length, initial_max_length + 5)
        
        # Check that new food was generated
        self.assertIsNotNone(self.game.food_pos)
        self.assertNotEqual(self.game.food_pos, (100, 100))
    
    def test_collision_with_self(self):
        """Test that collision with self ends the game"""
        # Create a snake with enough segments
        self.game.snake_body = [(100, 100), (110, 100), (120, 100), 
                               (130, 100), (140, 100), (150, 100)]
        
        # Make sure the snake is long enough for collision detection
        self.assertGreater(len(self.game.snake_body), 5)
        
        # Force a collision by adding a new head position that matches an existing body segment
        result = self.game.update((100, 100))
        
        # The update should return False when game over
        self.assertFalse(result)
        
        # Check that game is over
        self.assertTrue(self.game.game_over)

if __name__ == '__main__':
    unittest.main()
