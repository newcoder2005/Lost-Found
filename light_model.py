import tensorflow as tf
import numpy as np
import os
import requests
from io import BytesIO
from PIL import Image

base_model = tf.keras.applications.MobileNetV2(
    include_top=False,
    pooling='avg',
    weights='imagenet'
)

dense_layer = tf.keras.layers.Dense(128, activation='relu')(base_model.output)
model = tf.keras.Model(inputs=base_model.input, outputs=dense_layer)

def preprocess_image(image):
    image = tf.image.resize(image, (224, 224))
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = tf.expand_dims(image, axis=0)
    return image

def get_embedding(image):
    image = preprocess_image(image)
    embedding = model(image, training=False)
    return [float(x) for x in embedding.numpy().flatten()]

def cosine_similarity(vec1, vec2):
    vec1_np = np.array(vec1, dtype=np.float64)
    vec2_np = np.array(vec2, dtype=np.float64)
    return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))

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
    
    result = cosine_similarity(emb1, emb2)
    return result

def get_embedding_for_db(image_path):
    image = load_image(image_path)
    embedding = get_embedding(image)
    return embedding

if __name__ == "__main__":
    txt_file = "file_paths.txt"
    
    with open(txt_file, "r") as file:
        image_paths = [line.strip() for line in file.readlines()]
    
    file_path = "/Users/khoale/vscode/UNIHACK/Testing Image Detection/same_cat_different_background/my_dieu_1.png"
    
    for img_path in image_paths:
        if os.path.exists(img_path) or img_path.startswith('http'):
            result = compare_image(img_path, file_path)
            print(img_path)
            print("Result is ", result)
            print("--------------------")