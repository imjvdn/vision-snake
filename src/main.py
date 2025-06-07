#!/usr/bin/env python3
"""
Main entry point for the Vision Snake Game
"""

from vision_snake.game import VisionSnakeGame

def main():
    """Run the Vision Snake Game"""
    try:
        game = VisionSnakeGame()
        print("Starting Vision Snake Game...")
        print("Use your index finger to control the snake.")
        print("Press 'q' or ESC to quit.")
        game.run()
    except Exception as e:
        print(f"Error running Vision Snake Game: {e}")

if __name__ == "__main__":
    main()
