import tensorflow as tf
import numpy as np
import os

# 1. Define (or import) your base model
base_model = tf.keras.applications.EfficientNetB5(
    include_top=False,
    pooling='avg',  # outputs a 2048-dimensional vector
    weights='imagenet'
)
dense_layer = tf.keras.layers.Dense(512, activation='relu')(base_model.output)
model = tf.keras.Model(inputs=base_model.input, outputs=dense_layer)

# 2. Define a preprocessing function that matches EfficientNetB5's requirements
def preprocess_to_effnet_specs(image):
    # Example: resize to 456x456, cast, normalize according to EfficientNetB5
    image = tf.image.resize(image, (456, 456))  # EfficientNetB5 input size
    image = tf.keras.applications.efficientnet.preprocess_input(image)
    # Expand dimensions so the model sees a batch of size 1
    image = tf.expand_dims(image, axis=0)
    return image

# 3. Define the embedding function
def get_embedding(image):
    image = preprocess_to_effnet_specs(image)
    embedding = base_model(image, training=False)
    return embedding.numpy().flatten()  # shape should be (2048,)

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def compare_image(path1, path2):
    raw_image1 = tf.io.read_file(path1)
    raw_image2 = tf.io.read_file(path2)
    real_image1 = tf.image.decode_jpeg(raw_image1, channels=3)
    real_image2 = tf.image.decode_jpeg(raw_image2, channels=3)
    emb1 = get_embedding(real_image1)
    emb2 = get_embedding(real_image2)
    embedding1 = emb1.tolist()
    embedding2 = emb2.tolist()
    result = cosine_similarity(embedding1, embedding2)
    return result

txt_file = "file_paths.txt"

# Read all image paths from the text file
with open(txt_file, "r") as file:
    image_paths = [line.strip() for line in file.readlines()]

file_path = "/Users/khoale/vscode/UNIHACK/Testing Image Detection/same_cat_different_background/my_dieu_1.png"
# Process each image
for img_path in image_paths:
    if os.path.exists(img_path):
        result = compare_image(img_path, file_path)
        print(img_path) 
        print("Result is ", result)
        print("--------------------")
