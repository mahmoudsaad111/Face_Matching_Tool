import os
import glob
from face_matcher import compare_faces, distance_to_confidence

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_images")


def path(filename):
    return os.path.join(TEST_DIR, filename)


def photos_for_person(person_number):
    """Finds all photo files belonging to a given person number (1, 2, 3...)."""
    pattern = os.path.join(TEST_DIR, f"person{person_number}_*.jpg")
    return sorted(glob.glob(pattern))


# ---- Real face pairs, pulled dynamically from whatever the LFW script generated ----

person1_photos = photos_for_person(1)
person2_photos = photos_for_person(2)


def test_test_images_folder_has_enough_photos():
    """Sanity check: make sure the dataset script actually produced usable files
    before running the real tests below."""
    assert len(person1_photos) >= 2, "Need at least 2 photos of person 1 — run get_test_images.py"
    assert len(person2_photos) >= 1, "Need at least 1 photo of person 2 — run get_test_images.py"


def test_same_person_different_photos_is_a_match():
    result = compare_faces(person1_photos[0], person1_photos[1])
    assert result.error is None
    assert result.is_match is True


def test_two_different_people_is_not_a_match():
    result = compare_faces(person1_photos[0], person2_photos[0])
    assert result.error is None
    assert result.is_match is False


def test_image_with_no_face_returns_error():
    result = compare_faces(path("no_face.jpg"), person1_photos[0])
    assert result.error is not None
    assert "No face detected" in result.error


def test_nonexistent_file_returns_error():
    result = compare_faces(path("does_not_exist.jpg"), person1_photos[0])
    assert result.error is not None


def test_confidence_score_is_within_valid_range():
    result = compare_faces(person1_photos[0], person1_photos[1])
    confidence = distance_to_confidence(result.distance)
    assert 0 <= confidence <= 100


def test_matching_pair_has_higher_confidence_than_non_matching_pair():
    same_person = compare_faces(person1_photos[0], person1_photos[1])
    different_people = compare_faces(person1_photos[0], person2_photos[0])

    confidence_same = distance_to_confidence(same_person.distance)
    confidence_different = distance_to_confidence(different_people.distance)

    assert confidence_same > confidence_different


def test_all_available_people_are_distinguishable():
    """Bonus: compares every pair of DIFFERENT people found in test_images
    and confirms none of them incorrectly match."""
    all_people_numbers = []
    n = 1
    while photos_for_person(n):
        all_people_numbers.append(n)
        n += 1

    for i in range(len(all_people_numbers)):
        for j in range(i + 1, len(all_people_numbers)):
            photos_i = photos_for_person(all_people_numbers[i])
            photos_j = photos_for_person(all_people_numbers[j])
            result = compare_faces(photos_i[0], photos_j[0])
            assert result.is_match is False, (
                f"person{all_people_numbers[i]} and person{all_people_numbers[j]} "
                f"were incorrectly matched"
            )