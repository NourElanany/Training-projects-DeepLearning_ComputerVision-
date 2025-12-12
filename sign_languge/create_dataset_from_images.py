import cv2
import mediapipe as mp
import pandas as pd
import os
import numpy as np

# Initialize MediaPipe Hands
# static_image_mode=True makes the model run more efficiently on static images
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

DATA_DIR = r'D:\BCAI_4\C_V\SEC\sign_languge\data\asl_alphabet_train'
CSV_FILE = 'hand_landmarks.csv'
VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png'] # Supported image types

# List to store all landmark data
all_landmarks = []

print("Starting image processing...")

# Loop through each label (letter) directory inside 'data'
for label in os.listdir(DATA_DIR):
    label_dir = os.path.join(DATA_DIR, label)
    if not os.path.isdir(label_dir):
        continue

    print(f"Processing label: {label}")

    # Loop through images inside the label directory
    for image_file in os.listdir(label_dir):
        # Check if the file is a valid image
        file_ext = os.path.splitext(image_file)[1].lower()
        if file_ext not in VALID_EXTENSIONS:
            continue
            
        image_path = os.path.join(label_dir, image_file)
        
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image {image_path}")
            continue

        # Convert the image to RGB (MediaPipe requires RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image to extract landmarks
        results = hands.process(image_rgb)

        # Check if a hand was found in the image
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Extract 42 keypoints (x, y)
            frame_data = []
            for lm in hand_landmarks.landmark:
                frame_data.append(lm.x)
                frame_data.append(lm.y)
            
            # Add the label (letter name)
            frame_data.append(label)
            all_landmarks.append(frame_data)
        else:
            print(f"Warning: No hand found in image {image_path}")

print("... Image processing finished.")

#////////////////////////////////////////////////////////////////////

# Create a DataFrame
# 42 columns for keypoints + 1 'target' column
columns = []
for i in range(21):
    columns.append(f'x{i}')
    columns.append(f'y{i}')
columns.append('target')

df = pd.DataFrame(all_landmarks, columns=columns)


#////////////////////////////////////////////////////////////////////


# Ensure data was extracted before saving
if df.empty:
    print("Error: No data extracted. Make sure images are in the correct path.")
else:
    # Save the file
    df.to_csv(CSV_FILE, index=False)
    print(f"Data saved successfully to {CSV_FILE}")

hands.close()