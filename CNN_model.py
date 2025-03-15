# CNN_model.py - With HTTPS functionality
import tensorflow as tf
import numpy as np
import os
import requests
from io import BytesIO
from PIL import Image

base_model = tf.keras.applications.EfficientNetB5(
    include_top=False,
    pooling='avg',
    weights='imagenet'
)
dense_layer = tf.keras.layers.Dense(512, activation='relu')(base_model.output)
model = tf.keras.Model(inputs=base_model.input, outputs=dense_layer)

def preprocess_to_effnet_specs(image):
    image = tf.image.resize(image, (456, 456))
    image = tf.keras.applications.efficientnet.preprocess_input(image)
    image = tf.expand_dims(image, axis=0)
    return image

def get_embedding(image):
    image = preprocess_to_effnet_specs(image)
    embedding = base_model(image, training=False)
    return embedding.numpy().flatten()

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def load_image(path):
    if path.startswith('http'):
        response = requests.get(path)
        img = Image.open(BytesIO(response.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        return tf.convert_to_tensor(img_array)
    else:
        raw_image = tf.io.read_file(path)
        return tf.image.decode_jpeg(raw_image, channels=3)

def compare_image(path1, path2):
    real_image1 = load_image(path1)
    real_image2 = load_image(path2)
    emb1 = get_embedding(real_image1)
    emb2 = get_embedding(real_image2)
    embedding1 = emb1.tolist()
    embedding2 = emb2.tolist()
    result = cosine_similarity(embedding1, embedding2)
    return result

txt_file = "file_paths.txt"

with open(txt_file, "r") as file:
    image_paths = [line.strip() for line in file.readlines()]

file_path = "/Users/khoale/vscode/UNIHACK/Testing Image Detection/same_cat_different_background/my_dieu_1.png"

for img_path in image_paths:
    if os.path.exists(img_path):
        result = compare_image(img_path, file_path)
        print(img_path)
        print("Result is ", result)
        print("--------------------")