import tensorflow as tf
import numpy as np
import os
import requests
from io import BytesIO
from PIL import Image
import gc

# Configure TensorFlow to use memory growth
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    for device in physical_devices:
        try:
            tf.config.experimental.set_memory_growth(device, True)
        except:
            pass

# Limit TensorFlow memory usage
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0],
            [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=512)]
        )
    except:
        pass

# Global model reference - load only once
_model = None

def get_model():
    global _model
    if _model is None:
        tf.keras.backend.clear_session()
        base_model = tf.keras.applications.MobileNetV2(
            include_top=False,
            pooling='avg',
            weights='imagenet'
        )
        dense_layer = tf.keras.layers.Dense(128, activation='relu')(base_model.output)
        _model = tf.keras.Model(inputs=base_model.input, outputs=dense_layer)
    return _model

def preprocess_image(image):
    image = tf.image.resize(image, (224, 224))
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = tf.expand_dims(image, axis=0)
    return image

def load_image(path):
    try:
        if path.startswith('http'):
            response = requests.get(path, timeout=10)
            img = Image.open(BytesIO(response.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_array = np.array(img)
            tensor = tf.convert_to_tensor(img_array)
            del img
            del img_array
            gc.collect()
            return tensor
        else:
            raw_image = tf.io.read_file(path)
            tensor = tf.image.decode_jpeg(raw_image, channels=3)
            del raw_image
            gc.collect()
            return tensor
    except Exception as e:
        print(f"Error loading image from {path}: {str(e)}")
        raise

def get_embedding(image):
    model = get_model()
    image = preprocess_image(image)
    embedding = model(image, training=False)
    # Convert to standard Python float list for MySQL compatibility
    result = [float(x) for x in embedding.numpy().flatten()]
    
    # Clean up
    del image
    del embedding
    gc.collect()
    
    return result

def cosine_similarity(vec1, vec2):
    # Convert inputs to numpy arrays with float64 type for calculation
    vec1_np = np.array(vec1, dtype=np.float64)
    vec2_np = np.array(vec2, dtype=np.float64)
    result = float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))
    
    # Clean up
    del vec1_np
    del vec2_np
    gc.collect()
    
    return result

def compare_image(path1, path2):
    try:
        # Load and process first image
        real_image1 = load_image(path1)
        emb1 = get_embedding(real_image1)
        del real_image1
        gc.collect()
        
        # Load and process second image
        real_image2 = load_image(path2)
        emb2 = get_embedding(real_image2)
        del real_image2
        gc.collect()
        
        # Calculate similarity
        result = cosine_similarity(emb1, emb2)
        
        # Clean up
        del emb1
        del emb2
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Comparison error: {str(e)}")
        # Return a very low similarity score on error
        return 0.0