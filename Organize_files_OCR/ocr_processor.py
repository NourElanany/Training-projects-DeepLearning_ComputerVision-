import os
import cv2
import pytesseract
import re
from pathlib import Path

# Configure Tesseract path
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print("INFO: Tesseract path set successfully.")
except Exception as e:
    print(f"WARNING: Could not set Tesseract path. Details: {e}")

def extract_text_from_image(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(gray, lang='ara+eng', config=custom_config).strip()
        return extracted_text
    except Exception as e:
        print(f"ERROR: Could not perform OCR on image '{image_path}'. Details: {e}")
        return ""

def create_safe_filename_from_text(text, num_words=2):
    if not text or not text.strip():
        return "Document"
    words = text.split()
    file_prefix = "_".join(words[:num_words]) if len(words) >= num_words else "_".join(words)
    file_prefix = re.sub(r'[^\w\s-]', '', file_prefix).strip()
    file_prefix = re.sub(r'\s+', '_', file_prefix)
    return file_prefix if file_prefix else "Document"

def process_images_in_folder(folder_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}")
            
            # Extract text
            extracted_text = extract_text_from_image(image_path)
            if not extracted_text:
                print(f"Skipping {filename} due to OCR failure.")
                continue
            
            # Generate new base name
            safe_name = create_safe_filename_from_text(extracted_text)
            
            # Ensure unique file names to avoid overwriting
            count = 1
            unique_name = safe_name
            while os.path.exists(os.path.join(output_folder, unique_name + '.jpg')) or \
                  os.path.exists(os.path.join(output_folder, unique_name + '.txt')):
                unique_name = f"{safe_name}_{count}"
                count += 1

            # Save image with new name
            img = cv2.imread(image_path)
            new_image_path = os.path.join(output_folder, unique_name + '.jpg')
            cv2.imwrite(new_image_path, img)
            
            # Save text file with same base name
            new_text_path = os.path.join(output_folder, unique_name + '.txt')
            with open(new_text_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)

            print(f"Saved Image: {new_image_path}")
            print(f"Saved Text : {new_text_path}\n")

if __name__ == "__main__":
    input_folder = r"C:/Users/ADMIN/Desktop/MyOrganizerProject/output_photos/document"  # Folder containing images
    output_folder = r"C:/Users/ADMIN/Desktop/MyOrganizerProject/output_photos/document" # Folder to save processed files
    process_images_in_folder(input_folder, output_folder)
