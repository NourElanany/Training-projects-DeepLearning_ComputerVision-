# organizer.py
import os
import shutil
from classifier import classify_image 


INPUT_FOLDER = 'input_photos'
OUTPUT_FOLDER = 'output_photos'

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

def organize_photos():

    print("-" * 50)
    print("Starting Auto Photo Organizer on Local Machine...")
    print("-" * 50)

    # التأكد من وجود مجلد الإدخال
    if not os.path.exists(INPUT_FOLDER) or not os.path.isdir(INPUT_FOLDER):
        print(f"ERROR: Input folder '{INPUT_FOLDER}' not found. Please create it and add photos.")
        return


    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"INFO: Created output folder at '{OUTPUT_FOLDER}'")

    files_to_process = [f for f in os.listdir(INPUT_FOLDER) if os.path.isfile(os.path.join(INPUT_FOLDER, f))]

    if not files_to_process:
        print("INFO: Input folder is empty. Nothing to organize.")
        return

    print(f"Found {len(files_to_process)} files to process.\n")

    for filename in files_to_process:
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension in ALLOWED_EXTENSIONS:
            source_path = os.path.join(INPUT_FOLDER, filename)
            category = classify_image(source_path)

            destination_folder = os.path.join(OUTPUT_FOLDER, category)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            destination_path = os.path.join(destination_folder, filename)
            try:
                shutil.move(source_path, destination_path)
                print(f"MOVED: '{filename}'  >>  Category: {category}")
            except Exception as e:
                print(f"ERROR: Could not move file '{filename}'. Details: {e}")
        else:
            print(f"SKIPPED: '{filename}' (Not a recognized image file)")

    print("\n" + "-" * 50)
    print("Organization complete!")
    print("-" * 50)


if __name__ == '__main__':
    organize_photos()