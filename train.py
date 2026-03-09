import torch
import timm
import numpy as np
import cv2
import os
import random
from PIL import Image
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, WeightedRandomSampler
from torch import nn, optim
from collections import Counter

# -----------------------
# 1. Shared Preprocessing (Ben Graham)
# -----------------------
def ben_graham_processing(image):
    """
    Normalizes lighting and increases contrast for blood vessels/hemorrhages.
    MUST be used in both training and app inference.
    """
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (224, 224))
    
    # Gaussian Blur subtraction: highlights microaneurysms and exudates
    image = cv2.addWeighted(image, 4, cv2.GaussianBlur(image, (0, 0), 10), -4, 128)
    
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

# -----------------------
# 2. Settings & Device
# -----------------------
DATA_DIR = "dataset/train"
BATCH_SIZE = 32
EPOCHS = 20  
MODEL_PATH = "best_dr_model.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Device identified: {device}")

# -----------------------
# 3. Enhanced Image Transforms
# -----------------------
# Using ImageNet normalization stats which EfficientNet expects
train_transform = transforms.Compose([
    transforms.Lambda(ben_graham_processing),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(), # Eyes are circular, vertical flips work too!
    transforms.RandomRotation(20),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# -----------------------
# 4. Balanced Dataset & Sampler
# -----------------------
full_dataset = datasets.ImageFolder(DATA_DIR, transform=train_transform)
classes = full_dataset.classes

# Get labels to calculate balancing weights
targets = np.array(full_dataset.targets)
counts = Counter(targets)
print(f"📊 Dataset counts: {dict(counts)}")

# Calculate weights: 1 / frequency
class_weights = {cls: 1.0/count for cls, count in counts.items()}
sample_weights = [class_weights[t] for t in targets]

# WeightedRandomSampler forces the model to see Stage 3/4 as often as Stage 0
sampler = WeightedRandomSampler(
    weights=sample_weights,
    num_samples=len(sample_weights),
    replacement=True
)

train_loader = DataLoader(
    full_dataset, 
    batch_size=BATCH_SIZE, 
    sampler=sampler,
    pin_memory=True if device == "cuda" else False
)

# -----------------------
# 5. Model: EfficientNet-B0
# -----------------------
print("🧠 Initializing EfficientNet-B0...")
model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=5)
model.to(device)

# Loss with Label Smoothing to prevent over-fitting to 'No DR'
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.Adam(model.parameters(), lr=0.0001, weight_decay=1e-5)
scheduler = optim.lr_scheduler.OneCycleLR(optimizer, max_lr=0.001, steps_per_epoch=len(train_loader), epochs=EPOCHS)

# -----------------------
# 6. Optimized Training Loop
# -----------------------
print("\n🟢 Starting Balanced Training...")
best_acc = 0.0

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        
        # Forward
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100. * correct / total
    
    print(f"Epoch [{epoch+1}/{EPOCHS}] | Loss: {epoch_loss:.4f} | Training Acc: {epoch_acc:.2f}%")
    if epoch_acc > best_acc:
        best_acc = epoch_acc
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"⭐️ Model Improved! Saved to {MODEL_PATH}")

print(f"\n✅ Training Complete. Best Training Accuracy: {best_acc:.2f}%")