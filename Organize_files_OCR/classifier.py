import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input # <-- إضافة جديدة
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


MODEL_PATH = "C:/Users/ADMIN/Desktop/MyOrganizerProject/my_final_model.h5"

CLASS_NAMES = ['bike', 'cars', 'cats', 'document', 'dogs', 'flowers', 'horses', 'human']

print("INFO: Loading custom classification model...")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("INFO: Custom model loaded successfully.")
except Exception as e:
    print(f"ERROR: Could not load the model from '{MODEL_PATH}'. Details: {e}")
    exit()

def prepare_image(img_path, target_size=(224, 224)):
    """تحميل الصورة ومعالجتها بما في ذلك preprocess_input"""
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array_expanded = np.expand_dims(img_array, axis=0)

    return preprocess_input(img_array_expanded)

def classify_image(img_path):
    try:
        prepared_img = prepare_image(img_path)
        predictions = model.predict(prepared_img, verbose=0)
        score = tf.nn.softmax(predictions[0])
        predicted_class_index = np.argmax(score)
        predicted_class_name = CLASS_NAMES[predicted_class_index]
        return predicted_class_name
    except Exception as e:
        print(f"ERROR: Could not process image '{os.path.basename(img_path)}'. Details: {e}")
        return 'Error_Files'