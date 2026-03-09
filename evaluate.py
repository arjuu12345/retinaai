import torch
import timm
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = "dataset/train"
MODEL_PATH = "best_dr_model.pth"

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

dataset = datasets.ImageFolder(DATA_DIR, transform=transform)
loader = DataLoader(dataset, batch_size=32)

model = timm.create_model('mobilenetv2_100', pretrained=False, num_classes=5)
model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
model.eval()

all_preds = []
all_labels = []

with torch.no_grad():
    for images, labels in loader:
        outputs = model(images)
        preds = torch.argmax(outputs, dim=1)
        all_preds.extend(preds.numpy())
        all_labels.extend(labels.numpy())

cm = confusion_matrix(all_labels, all_preds)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

print(classification_report(all_labels, all_preds))