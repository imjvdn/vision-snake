from setuptools import setup, find_packages

setup(
    name="vision_snake",
    version="0.1.0",
    description="A Snake game controlled by hand gestures via webcam",
    author="Vision Snake Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "opencv-python>=4.5.0",
        "mediapipe>=0.8.9",
        "numpy>=1.19.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "vision-snake=vision_snake.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
