from segment_anything import sam_model_registry, SamPredictor
import torch

# STEP 1: Choose checkpoint + model type
sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"  

# STEP 2: Load model
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)

# STEP 3: Move to GPU or CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
sam.to(device)

# STEP 4: Initialize the predictor object
predictor = SamPredictor(sam)
