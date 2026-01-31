import torch
from torchvision import transforms
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
try:
    import cv2
except ImportError:
    cv2 = None  # Graceful fallback if OpenCV is not available

def load_image(image, size=512):
    """Load and preprocess image for neural style transfer"""
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)

def tensor_to_image(tensor):
    """Convert tensor back to PIL Image"""
    image = tensor.cpu().clone()
    image = image.squeeze(0)
    image = transforms.Normalize(mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225], std=[1/0.229, 1/0.224, 1/0.225])(image)
    image = torch.clamp(image, 0, 1)
    return transforms.ToPILImage()(image)

def apply_post_processing(image, style="none", strength=0.5):
    """Apply post-processing effects to enhance style transfer results"""
    if style == "vintage":
        # Add vintage effect
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.8)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
    elif style == "dramatic":
        # Increase contrast and saturation
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.4)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)
    elif style == "soft":
        # Apply slight blur for softer look
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return image

def create_style_preview(content_img, style_img, grid_size=3):
    """Create a preview grid showing different style strengths"""
    previews = []
    for i in range(grid_size):
        strength = (i + 1) / grid_size
        # Simple blend for preview (in real implementation, use actual model)
        blended = Image.blend(content_img, style_img, strength * 0.3)
        previews.append(blended)
    return previews

def validate_image(image_data):
    """Validate uploaded image"""
    try:
        image = Image.open(image_data)
        # Check file size (max 10MB)
        image_data.seek(0, 2)  # Seek to end
        size = image_data.tell()
        image_data.seek(0)  # Reset
        
        if size > 10 * 1024 * 1024:  # 10MB
            return False, "Image too large (max 10MB)"
        
        # Check dimensions
        if max(image.size) > 4096:
            return False, "Image dimensions too large (max 4096px)"
        
        return True, "Valid"
    except Exception as e:
        return False, f"Invalid image: {str(e)}"

def resize_for_processing(image, max_size=1024):
    """Resize image for optimal processing while maintaining aspect ratio"""
    width, height = image.size
    if max(width, height) > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image