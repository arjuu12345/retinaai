import torch
import timm
import os

def load_model(model_path="best_dr_model.pth"):
    """
    Loads the EfficientNet-B0 model weights for inference.
    Ensures the model is mapped to CPU for deployment compatibility.
    """
    # 1. Recreate the exact architecture used in training
    # We set pretrained=False here because we are loading our own local weights
    model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=5)
    
    # 2. Check if the weight file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model weight file '{model_path}' not found. Please run train.py first.")

    # 3. Load the state dictionary
    # map_location=torch.device('cpu') ensures it works on computers without GPUs (like Streamlit Cloud)
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(state_dict)
    
    # 4. Set to evaluation mode
    # This is CRITICAL: it disables Dropout and BatchNorm updates during prediction
    model.eval()
    
    return model