import os
import pandas as pd
import shutil

csv_path = "dataset/trainLabels_cropped.csv"
image_dir = "dataset/resized_train_cropped/resized_train_cropped"
output_dir = "dataset/train"

df = pd.read_csv(csv_path)

print("CSV records:", len(df))
print("Checking image directory:", image_dir)
print("Total images found:", len(os.listdir(image_dir)))

# Create class folders
for i in range(5):
    os.makedirs(os.path.join(output_dir, str(i)), exist_ok=True)

# Create a lookup dictionary of all images
image_files = os.listdir(image_dir)
image_set = set(image_files)

copied = 0
missing = 0

for _, row in df.iterrows():
    base_name = str(row['image'])
    label = str(row['level'])

    # Find matching file (handles any extension)
    found = False
    for ext in [".jpeg", ".jpg", ".png"]:
        file_name = base_name + ext
        if file_name in image_set:
            src = os.path.join(image_dir, file_name)
            dst = os.path.join(output_dir, label, file_name)
            shutil.copy(src, dst)
            copied += 1
            found = True
            break

    if not found:
        missing += 1

print("Copied:", copied)
print("Missing:", missing)