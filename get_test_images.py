from sklearn.datasets import fetch_lfw_people
from PIL import Image
import numpy as np
import os
from collections import defaultdict


def generate_test_images():
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_images")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Downloading dataset (only happens once, cached after)...")
    data = fetch_lfw_people(min_faces_per_person=10, resize=1.0, color=True)

    def save(index, filename):
        img_array = (data.images[index] * 255).astype(np.uint8)
        Image.fromarray(img_array).save(os.path.join(OUTPUT_DIR, filename))

    photos_by_person = defaultdict(list)
    for i, person_id in enumerate(data.target):
        photos_by_person[person_id].append(i)

    eligible_people = [pid for pid, indices in photos_by_person.items() if len(indices) >= 3]
    NUM_PEOPLE = min(5, len(eligible_people))
    print(f"Found {len(eligible_people)} eligible people, using {NUM_PEOPLE}.")

    for person_num, person_id in enumerate(eligible_people[:NUM_PEOPLE], start=1):
        name = data.target_names[person_id].replace(" ", "_")
        indices = photos_by_person[person_id][:3]
        for photo_num, idx in enumerate(indices, start=1):
            filename = f"person{person_num}_{name}_{photo_num}.jpg"
            save(idx, filename)
            print(f"Saved {filename}")

    print(f"\nDone! {NUM_PEOPLE} people saved to '{OUTPUT_DIR}/', each with up to 3 photos.")


if __name__ == "__main__":
    generate_test_images()