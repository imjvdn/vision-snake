# Vision Snake Game

A Snake game controlled by your index finger using webcam input. The snake follows the tip of your index finger in real-time, detected via MediaPipe hand tracking.

## Features

- Real-time hand tracking using MediaPipe Hands
- Snake follows your index finger movement
- Food randomly spawns on screen
- Score increases when food is eaten
- Snake color changes based on score
- Game over when snake collides with itself
- Reset game by showing an open palm for 2 seconds

## Project Structure

```
vision-snake/
├── assets/                # Resources and static files
├── src/                   # Source code
│   ├── vision_snake/      # Main package
│   │   ├── __init__.py    # Package initialization
│   │   ├── cli.py         # Command-line interface
│   │   ├── game.py        # Main game class
│   │   ├── hand_tracker.py # Hand tracking module
│   │   └── snake_game.py  # Snake game logic
│   └── main.py            # Direct script entry point
├── tests/                 # Test files
│   ├── __init__.py
│   └── test_snake_game.py # Unit tests for snake game
├── README.md              # This file
├── requirements.txt       # Dependencies
└── setup.py               # Package installation setup
```

## Requirements

- Python 3.7+
- OpenCV (cv2)
- MediaPipe
- NumPy

## Installation

### Option 1: Install directly from the repository

```bash
# Clone the repository
git clone https://github.com/yourusername/vision-snake.git
cd vision-snake

# Install the package in development mode
pip install -e .
```

### Option 2: Install dependencies only

```bash
pip install -r requirements.txt
```

## How to Run

### As an installed package (recommended)

After installing with `pip install -e .`:

```bash
# Run as a command-line tool
vision-snake

# Run with debug mode for more detailed error messages
vision-snake --debug

# Specify a specific camera to use (useful for systems with multiple cameras)
vision-snake --camera 0  # Use the built-in webcam (usually index 0)
vision-snake --camera 1  # Use an external webcam or other camera
```

### As a Python script

```bash
# Run the main script directly
python src/main.py
```

## How to Play

1. Position yourself in front of your webcam
2. Point your index finger to control the snake
3. Guide the snake to eat the food (red circles)
4. Avoid colliding with the snake's own body
5. When game over, show an open palm for 2 seconds to restart
6. Press 'q' or ESC to quit the game

## Development

### Running Tests

```bash
python -m unittest discover -s tests
```

## Module Overview

### vision_snake.hand_tracker

The `HandTracker` class:
- Initializes MediaPipe Hands for hand detection and tracking
- Processes webcam frames to detect hands
- Extracts the position of the index finger tip
- Draws hand landmarks on the frame

### vision_snake.snake_game

The `SnakeGame` class:
- Manages the snake's body as a list of positions
- Generates food at random positions
- Detects collisions between the snake and food or itself
- Updates the snake's position based on the index finger position
- Draws the snake, food, and score on the frame

### vision_snake.game

The `VisionSnakeGame` class:
- Integrates hand tracking and snake game logic
- Manages the webcam and game loop
- Processes frames and handles user input
- Detects the reset gesture (open palm)
- Displays FPS and game information
