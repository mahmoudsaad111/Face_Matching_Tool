# Face Matching Mini Tool

A simple desktop application that compares two facial images and reports whether they belong to the same person.

## Features
- Select or drag-and-drop two face images (Face 1 and Face 2)
- Side-by-side image preview
- Face detection and comparison using the `face_recognition` library
- Clear Match / No Match result
- Reset button to start over
- Basic error handling for unreadable images or images with no detectable face

## Requirements
- Python 3.9+ (tested on Python 3.12)
- Windows, macOS, or Linux

## Installation

1. Clone or download this project.
2. (Recommended) Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   **Note:** `face_recognition` depends on `dlib`, which requires CMake and a C++ compiler to build on some systems.
   - **Windows:** Install [CMake](https://cmake.org/download/) and Visual Studio Build Tools (C++ workload) before running `pip install`.
   - **macOS:** `brew install cmake` first.
   - **Linux:** `sudo apt install cmake build-essential` first.

## Usage

Run the app:
```
python gui.py
```

Workflow:
1. Click or drag an image into the "Face 1" box.
2. Click or drag an image into the "Face 2" box.
3. Click **Compare**.
4. The result (**MATCH** or **NO MATCH**) is shown below the buttons.
5. Click **Reset** to clear both images and start over.

## Notes
- Supported image formats: `.jpg`, `.jpeg`, `.png`
- If no face is detected in an image, or the file can't be opened, an error message is shown instead of a result.
- The matching threshold is set in `face_matcher.py` (`DISTANCE_THRESHOLD = 0.6`), which is the standard default recommended by the `face_recognition` library.

## Project Structure
```
face-matching-tool/
├── gui.py             # Desktop GUI application
├── face_matcher.py    # Face detection and comparison logic
├── requirements.txt   # Python dependencies
└── README.md
```
