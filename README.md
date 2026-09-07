# Face Matching Mini Tool

A simple desktop application that compares two facial images and reports whether they belong to the same person.

## Features
- Select or drag-and-drop two face images (Face 1 and Face 2)
- Side-by-side image preview with filenames shown
- Face detection and comparison using the `face_recognition` library
- Clear Match / No Match result, with a confidence percentage indicating how close the match was
- Comparison runs in the background so the window never freezes
- Reset button to clear both images and start over
- Basic error handling for unreadable images, images with no detectable face, and missing files
- Also available as a standalone Windows executable (no Python installation required) — see **Packaged Executable** below

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
4. The result (**MATCH** or **NO MATCH**, with a confidence percentage) is shown below the buttons.
5. Click **Reset** to clear both images and start over.

## Notes
- Supported image formats: `.jpg`, `.jpeg`, `.png`
- If no face is detected in an image, or the file can't be opened, an error message is shown instead of a result, naming which face (Face 1 or Face 2) caused the issue.
- The matching threshold is set in `face_matcher.py` (`DISTANCE_THRESHOLD = 0.6`), which is the standard default recommended by the `face_recognition` library.
- The confidence percentage is a simplified indicator derived from the face-distance score, not a calibrated statistical probability — it's meant to give a general sense of how close a match was, not a precise likelihood.

## Running Tests

Unit tests use `pytest` and real sample photos from the public LFW (Labeled Faces in the Wild) research dataset.

1. Install dev dependencies:
   ```
   pip install -r requirements-dev.txt
   ```
2. Generate test images (only needs to be run once; downloads and caches the dataset):
   ```
   python get_test_images.py
   ```
3. Add one additional file manually: `test_images/no_face.jpg` — any image with no face in it (a landscape, a screenshot, etc.), used to test the "no face detected" error path.
4. Run the tests:
   ```
   pytest test_face_matcher.py -v
   ```

## Packaged Executable

A standalone Windows `.exe` can be built with PyInstaller so the app can run without a Python installation:

```
pip install -r requirements-dev.txt
pyinstaller --onefile --windowed --name "FaceMatchingTool" --add-data "<path-to-face_recognition_models-folder>;face_recognition_models" gui.py
```

Find the `face_recognition_models` folder path with:
```
python -c "import face_recognition_models; print(face_recognition_models.__path__[0])"
```

The built executable will be in the `dist/` folder.

## Project Structure
```
face-matching-tool/
├── gui.py                  # Desktop GUI application
├── face_matcher.py         # Face detection and comparison logic
├── get_test_images.py      # Downloads sample photos for testing
├── test_face_matcher.py    # Unit tests
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Additional dependencies for testing/packaging
└── README.md
```
