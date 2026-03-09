import torch
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np

def ben_graham_processing(image):
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (224, 224))
    image = cv2.addWeighted(image, 4, cv2.GaussianBlur(image, (0, 0), 10), -4, 128)
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

def preprocess(image):
    # This transform must be identical to the one in train.py (excluding augmentations)
    transform = transforms.Compose([
        transforms.Lambda(ben_graham_processing),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    # Add batch dimension: [1, 3, 224, 224]
    return transform(image).unsqueeze(0)