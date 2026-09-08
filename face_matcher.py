import face_recognition
from dataclasses import dataclass


DISTANCE_THRESHOLD = 0.6  # dlib's benchmarked default threshold on the LFW dataset (~99.38% accuracy)

# dataclass to hold the result of a face match
@dataclass
class MatchResult:
    is_match: bool
    distance: float
    error: str | None = None

# function to compare two face images and return a MatchResult
def compare_faces(image_path_1: str, image_path_2: str) -> MatchResult:
    try:
        image_1 = face_recognition.load_image_file(image_path_1)
        image_2 = face_recognition.load_image_file(image_path_2)
    except Exception:
        return MatchResult(is_match=False, distance=1.0, error="Could not read one of the image files.")

    encodings_1 = face_recognition.face_encodings(image_1)
    encodings_2 = face_recognition.face_encodings(image_2)

    # Check for errors in face detection since the task requires exactly one face in each image so multiple faces or no faces should be treated as errors.
    if len(encodings_1) == 0:
        return MatchResult(False, 1.0, "No face detected in Face 1.")

    if len(encodings_1) > 1:
        return MatchResult(False, 1.0, "Multiple faces detected in Face 1.")

    if len(encodings_2) == 0:
        return MatchResult(False, 1.0, "No face detected in Face 2.")

    if len(encodings_2) > 1:
        return MatchResult(False, 1.0, "Multiple faces detected in Face 2.")

    distance = face_recognition.face_distance([encodings_1[0]], encodings_2[0])[0]
    return MatchResult(is_match=bool(distance <= DISTANCE_THRESHOLD), distance=float(distance))




