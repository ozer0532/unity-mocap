# Unity Mocap

## Prerequisites:
- Python 3.9
- Unity 2021.3 (Project is on 2021.3.0f1)
- Windows (may run on other platforms, but not tested)

## How to Initialize:
- (Optional) create a new virtual environment under `./venv/` directory
- Install Python requirements in requirements.txt

## Running the Calibration
- First, run the calibration app
  - If you use a virtual environment, run `./venv/Scripts/python.exe ./Assets/Python/gui.py`
  - Otherwise, just run `./Assets/Python/gui.py`
- To run the internal calibration for each camera
  - Take a photo of a checkerboard pattern on different angles using "Save Sample"
  - After taking several photos (around 8-12), use "Calibrate Camera"
- To run the external calibration
  - Take a photo of some objects on both cameras (make sure the same sides are visible on both cameras)
  - Use "Calibrate Camera" and make sure the epipolar lines are at the correct position

## Running the Animator
- Open the Unity project
- A few things to make sure before running the sample scene:
  - Under the main character "yBot", check if the `Python Runner` script is enabled and set to the correct cameras
  - You can pick between different methods, but I recommend the "Inference" method for first time use

