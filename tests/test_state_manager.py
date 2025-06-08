"""
Tests for the state manager module.
"""

import unittest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch
from vision_snake.state_manager import StateManager, GameState, MenuState, PlayingState


class TestStateManager(unittest.TestCase):
    """Tests for the StateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.width = 640
        self.height = 480
        self.state_manager = StateManager(self.width, self.height)
        
        # Create mock states
        self.mock_menu_state = MagicMock()
        self.mock_playing_state = MagicMock()
        
        # Add mock states to manager
        self.state_manager.states["menu"] = self.mock_menu_state
        self.state_manager.states["playing"] = self.mock_playing_state
    
    def test_change_state(self):
        """Test changing states."""
        # Change to menu state
        self.state_manager.change_state("menu")
        self.assertEqual(self.state_manager.current_state, self.mock_menu_state)
        
        # Change to playing state
        self.state_manager.change_state("playing")
        self.assertEqual(self.state_manager.current_state, self.mock_playing_state)
        
        # Test changing to non-existent state
        with self.assertRaises(ValueError):
            self.state_manager.change_state("non_existent")
    
    def test_update(self):
        """Test updating the current state."""
        # Set current state
        self.state_manager.current_state = self.mock_menu_state
        
        # Create mock hand landmarks and finger position
        mock_landmarks = MagicMock()
        mock_finger_pos = (100, 100)
        
        # Update state
        self.state_manager.update(mock_landmarks, mock_finger_pos)
        
        # Check if update was called on the current state
        self.mock_menu_state.update.assert_called_once_with(mock_landmarks, mock_finger_pos)
    
    def test_render(self):
        """Test rendering the current state."""
        # Set current state
        self.state_manager.current_state = self.mock_playing_state
        
        # Create mock frame
        mock_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Mock the render method to return a modified frame
        self.mock_playing_state.render.return_value = mock_frame + 1
        
        # Render state
        result_frame = self.state_manager.render(mock_frame)
        
        # Check if render was called on the current state
        self.mock_playing_state.render.assert_called_once_with(mock_frame)
        
        # Check if the returned frame is the one from the state's render method
        self.assertTrue(np.array_equal(result_frame, mock_frame + 1))
    
    def test_handle_key(self):
        """Test handling key presses."""
        # Set current state
        self.state_manager.current_state = self.mock_menu_state
        
        # Mock the handle_key method to return True
        self.mock_menu_state.handle_key.return_value = True
        
        # Handle key press
        result = self.state_manager.handle_key(27)  # ESC key
        
        # Check if handle_key was called on the current state
        self.mock_menu_state.handle_key.assert_called_once_with(27)
        
        # Check if the returned value is the one from the state's handle_key method
        self.assertTrue(result)


class TestMenuState(unittest.TestCase):
    """Tests for the MenuState class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.width = 640
        self.height = 480
        self.state_manager = MagicMock()
        self.menu_state = MenuState(self.state_manager, self.width, self.height)
    
    def test_initialization(self):
        """Test initialization of MenuState."""
        self.assertEqual(self.menu_state.width, self.width)
        self.assertEqual(self.menu_state.height, self.height)
        self.assertEqual(self.menu_state.options, ["Start Game", "Settings", "Exit"])
        self.assertEqual(self.menu_state.selected_option, 0)
    
    def test_handle_key_navigation(self):
        """Test keyboard navigation in menu."""
        # Test down arrow
        self.menu_state.handle_key(ord('s'))
        self.assertEqual(self.menu_state.selected_option, 1)
        
        # Test down arrow again
        self.menu_state.handle_key(ord('s'))
        self.assertEqual(self.menu_state.selected_option, 2)
        
        # Test wrapping around to the first option
        self.menu_state.handle_key(ord('s'))
        self.assertEqual(self.menu_state.selected_option, 0)
        
        # Test up arrow
        self.menu_state.handle_key(ord('w'))
        self.assertEqual(self.menu_state.selected_option, 2)
    
    def test_handle_key_selection(self):
        """Test selecting options in menu."""
        # Select "Start Game"
        self.menu_state.selected_option = 0
        self.menu_state.handle_key(13)  # Enter key
        self.state_manager.change_state.assert_called_once_with("playing")
        
        # Reset mock
        self.state_manager.change_state.reset_mock()
        
        # Select "Exit"
        self.menu_state.selected_option = 2
        result = self.menu_state.handle_key(13)  # Enter key
        self.assertFalse(result)  # Should return False to exit the game
    
    def test_render(self):
        """Test rendering the menu."""
        # Create a frame to render on
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Render the menu
        result_frame = self.menu_state.render(frame.copy())  # Use a copy to ensure original isn't modified
        
        # Basic check that rendering happened (frame should be modified)
        self.assertFalse(np.all(result_frame == 0))  # Check that the result frame is not all zeros


class TestPlayingState(unittest.TestCase):
    """Tests for the PlayingState class."""
    
    @patch('vision_snake.state_manager.SnakeGame')
    def setUp(self, mock_snake_game_class):
        """Set up test fixtures."""
        self.width = 640
        self.height = 480
        self.state_manager = MagicMock()
        
        # Set up the mock SnakeGame
        self.mock_snake_game = MagicMock()
        mock_snake_game_class.return_value = self.mock_snake_game
        
        # Create the playing state after setting up the mock
        self.playing_state = PlayingState(self.state_manager, self.width, self.height)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # No need to stop any patchers as they're handled by the decorator
    
    def test_initialization(self):
        """Test initialization of PlayingState."""
        self.assertEqual(self.playing_state.width, self.width)
        self.assertEqual(self.playing_state.height, self.height)
        self.assertEqual(self.playing_state.game, self.mock_snake_game)
        self.assertFalse(self.playing_state.paused)
    
    def test_update(self):
        """Test updating the game state."""
        # Create mock finger position
        mock_finger_pos = (100, 100)
        
        # Update state
        self.playing_state.update(None, mock_finger_pos)
        
        # Check if update was called on the snake game
        self.mock_snake_game.update.assert_called_once_with(mock_finger_pos)
    
    def test_handle_key_pause(self):
        """Test pausing the game."""
        # Initially not paused
        self.assertFalse(self.playing_state.paused)
        
        # Pause the game
        self.playing_state.handle_key(ord('p'))
        self.assertTrue(self.playing_state.paused)
        
        # Unpause the game
        self.playing_state.handle_key(ord('p'))
        self.assertFalse(self.playing_state.paused)
    
    def test_handle_key_menu(self):
        """Test returning to menu."""
        # Pause the game first (menu only accessible when paused)
        self.playing_state.paused = True
        
        # Return to menu
        self.playing_state.handle_key(ord('m'))
        self.state_manager.change_state.assert_called_once_with("menu")
    
    def test_handle_key_reset(self):
        """Test resetting the game."""
        # Reset the game
        self.playing_state.handle_key(ord('r'))
        self.mock_snake_game.reset.assert_called_once()
    
    def test_render(self):
        """Test rendering the game."""
        # Create a frame to render on
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Mock the draw method to return a modified frame
        modified_frame = frame.copy() + 1
        self.mock_snake_game.draw.return_value = modified_frame
        
        # Render the game
        result_frame = self.playing_state.render(frame)
        
        # Check if draw was called on the snake game
        self.mock_snake_game.draw.assert_called_once_with(frame)
        
        # Check if the returned frame is the one from the game's draw method
        self.assertIs(result_frame, modified_frame)


if __name__ == '__main__':
    unittest.main()
