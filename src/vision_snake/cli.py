#!/usr/bin/env python3
"""
Command-line interface for Vision Snake Game
"""

import argparse
from vision_snake.game import VisionSnakeGame

def main():
    """
    Entry point for the vision-snake command-line tool
    """
    parser = argparse.ArgumentParser(description="Vision Snake Game - Control a snake with your index finger")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--camera', type=int, default=None, 
                        help='Specify camera index to use (0 for built-in, 1 for external, etc.)')
    args = parser.parse_args()
    
    try:
        print("Starting Vision Snake Game...")
        print("Use your index finger to control the snake.")
        print("Show an open palm for 2 seconds to restart after game over.")
        print("Press 'q' or ESC to quit.")
        
        game = VisionSnakeGame(camera_index=args.camera)
        game.run()
    except Exception as e:
        print(f"Error running Vision Snake Game: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
