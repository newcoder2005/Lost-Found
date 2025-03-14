import tensorflow as tf
import numpy as np

base_model = tf.keras.applications.EfficientNetB5(
    include_top=False,
    weights='imagenet',
    pooling='avg'
)

# Preprocessing specific to EfficientNet
def preprocess_to_efficientnet(image):
    image = tf.image.resize(image, (456, 456))  # B3 likes 300x300 images
    image = tf.keras.applications.efficientnet.preprocess_input(image)
    image = tf.expand_dims(image, axis=0)
    return image

# Get feature vector
def get_embedding(image):
    image = preprocess_to_efficientnet(image)
    embedding = base_model(image, training=False)
    return embedding.numpy().flatten()  # Default size for B3: 1536-dim vector


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))



file_path = "/Users/khoale/vscode/UNIHACK/Screenshot 2025-03-12 at 9.23.00 pm.png"
raw_image = tf.io.read_file(file_path)
real_image = tf.image.decode_jpeg(raw_image, channels=3)
emb = get_embedding(real_image)

file_path = "/Users/khoale/vscode/UNIHACK/Screenshot 2025-03-12 at 9.23.12 pm.png"
raw_image = tf.io.read_file(file_path)
real_image = tf.image.decode_jpeg(raw_image, channels=3)
emb2 = get_embedding(real_image)

embedding1 = emb.tolist()
embedding2 = emb2.tolist()

result = cosine_similarity(embedding1, embedding2)

print(result)

file_path = "/Users/khoale/vscode/UNIHACK/meocam.jpeg"
raw_image = tf.io.read_file(file_path)
real_image = tf.image.decode_jpeg(raw_image, channels=3)
emb = get_embedding(real_image)

file_path = "/Users/khoale/vscode/UNIHACK/meocam2.jpeg"
raw_image = tf.io.read_file(file_path)
real_image = tf.image.decode_jpeg(raw_image, channels=3)
emb2 = get_embedding(real_image)

embedding1 = emb.tolist()
embedding2 = emb2.tolist()

result = cosine_similarity(embedding1, embedding2)

print(result)