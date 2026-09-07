from sklearn.datasets import fetch_lfw_people
from PIL import Image
import numpy as np
import os

OUTPUT_DIR = "test_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# min_faces_per_person=10 -> only pulls people who have at least 10 photos,
# so you get plenty of "same person, different photo" pairs to choose from.
print("Downloading dataset (only happens once, cached after)...")
data = fetch_lfw_people(min_faces_per_person=10, resize=1.0, color=True)

def save(index, filename):
    img_array = (data.images[index] * 255).astype(np.uint8)
    Image.fromarray(img_array).save(os.path.join(OUTPUT_DIR, filename))

# Group all photo indices by person
from collections import defaultdict
photos_by_person = defaultdict(list)
for i, person_id in enumerate(data.target):
    photos_by_person[person_id].append(i)

# Only keep people who have at least 3 photos (gives us room to pick a few pairs)
eligible_people = [pid for pid, indices in photos_by_person.items() if len(indices) >= 3]

NUM_PEOPLE = min(5, len(eligible_people))  # grab up to 5 different people
print(f"Found {len(eligible_people)} eligible people, using {NUM_PEOPLE}.")

for person_num, person_id in enumerate(eligible_people[:NUM_PEOPLE], start=1):
    name = data.target_names[person_id].replace(" ", "_")
    indices = photos_by_person[person_id][:3]  # take up to 3 photos of this person

    for photo_num, idx in enumerate(indices, start=1):
        filename = f"person{person_num}_{name}_{photo_num}.jpg"
        save(idx, filename)
        print(f"Saved {filename}")

print(f"\nDone! {NUM_PEOPLE} people saved to '{OUTPUT_DIR}/', each with up to 3 photos.")
print("Use different photo numbers of the SAME person for match tests,")
print("and photos from DIFFERENT person numbers for no-match tests.")