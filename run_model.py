import torch
import timm
from PIL import Image
from torchvision import transforms

classes = [
    "No DR",
    "Mild",
    "Moderate",
    "Severe",
    "Proliferative DR"
]

device = "cuda" if torch.cuda.is_available() else "cpu"

model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=5)

model.load_state_dict(torch.load("best_dr_model.pth", map_location=device))
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],
                         [0.229,0.224,0.225])
])

img = Image.open("test.jpg").convert("RGB")

img = transform(img).unsqueeze(0).to(device)

with torch.no_grad():
    outputs = model(img)
    pred = torch.argmax(outputs,1).item()

print("Prediction:", classes[pred])