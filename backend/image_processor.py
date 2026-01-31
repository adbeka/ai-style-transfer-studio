"""
Advanced image processing utilities for AI Style Transfer Studio
"""

import numpy as np
try:
    import cv2
except ImportError:
    cv2 = None  # Graceful fallback if OpenCV is not available
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import torch
import torch.nn.functional as F
from typing import Tuple, List, Optional
import io
import base64


class AdvancedImageProcessor:
    """Advanced image processing for style transfer enhancement"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def enhance_content_preservation(self, original: Image.Image, styled: Image.Image, 
                                   preservation_strength: float = 0.3) -> Image.Image:
        """Enhance content preservation by blending original structure"""
        # Convert to arrays for processing
        orig_array = np.array(original.convert('RGB'))
        styled_array = np.array(styled.convert('RGB'))
        
        # Extract edges from original
        gray = cv2.cvtColor(orig_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_3channel = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        # Blend edges with styled image
        preserved = styled_array * (1 - preservation_strength) + \
                   edges_3channel * preservation_strength
        
        return Image.fromarray(preserved.astype(np.uint8))
    
    def apply_artistic_filters(self, image: Image.Image, style_type: str) -> Image.Image:
        """Apply style-specific artistic filters"""
        if style_type == "oil_painting":
            return self._oil_painting_effect(image)
        elif style_type == "watercolor":
            return self._watercolor_effect(image)
        elif style_type == "pencil_sketch":
            return self._pencil_sketch_effect(image)
        elif style_type == "vintage":
            return self._vintage_effect(image)
        else:
            return image
    
    def _oil_painting_effect(self, image: Image.Image) -> Image.Image:
        """Apply oil painting effect"""
        # Convert to numpy array
        img_array = np.array(image)
        
        if cv2 is not None:
            # Apply bilateral filter for oil painting effect
            oil_effect = cv2.bilateralFilter(img_array, 15, 80, 80)
            oil_effect = cv2.bilateralFilter(oil_effect, 15, 80, 80)
            
            # Add slight blur
            oil_effect = cv2.GaussianBlur(oil_effect, (3, 3), 0)
        else:
            # Fallback without OpenCV
            oil_effect = img_array
            # Apply simple smoothing
            image_pil = Image.fromarray(img_array)
            image_pil = image_pil.filter(ImageFilter.SMOOTH)
            oil_effect = np.array(image_pil)
        
        return Image.fromarray(oil_effect)
    
    def _watercolor_effect(self, image: Image.Image) -> Image.Image:
        """Apply watercolor effect"""
        # Increase saturation and decrease contrast slightly
        enhancer = ImageEnhance.Color(image)
        enhanced = enhancer.enhance(1.4)
        
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(0.8)
        
        # Apply slight blur for watercolor softness
        enhanced = enhanced.filter(ImageFilter.GaussianBlur(radius=1.5))
        
        return enhanced
    
    def _pencil_sketch_effect(self, image: Image.Image) -> Image.Image:
        """Apply pencil sketch effect"""
        # Convert to grayscale
        gray = image.convert('L')
        
        # Create inverted image
        inverted = ImageOps.invert(gray)
        
        # Blur the inverted image
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=21))
        
        # Create sketch by blending
        sketch_array = np.array(gray)
        blurred_array = np.array(blurred)
        
        # Dodge blend mode
        sketch = sketch_array.astype(np.float64)
        blur = blurred_array.astype(np.float64)
        
        result = 255 * sketch / (255 - blur + 1e-7)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Convert back to RGB
        return Image.fromarray(result).convert('RGB')
    
    def _vintage_effect(self, image: Image.Image) -> Image.Image:
        """Apply vintage/retro effect"""
        # Reduce saturation
        enhancer = ImageEnhance.Color(image)
        vintage = enhancer.enhance(0.7)
        
        # Increase contrast slightly
        enhancer = ImageEnhance.Contrast(vintage)
        vintage = enhancer.enhance(1.2)
        
        # Add sepia tone
        width, height = vintage.size
        pixels = vintage.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = vintage.getpixel((px, py))
                
                # Sepia formula
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                vintage.putpixel((px, py), (min(255, tr), min(255, tg), min(255, tb)))
        
        return vintage
    
    def create_style_grid(self, content_image: Image.Image, style_images: List[Image.Image],
                         grid_size: Tuple[int, int] = (2, 3)) -> Image.Image:
        """Create a grid showing different style applications"""
        rows, cols = grid_size
        
        # Resize images to uniform size
        target_size = (300, 300)
        content_resized = content_image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Create grid image
        grid_width = cols * target_size[0]
        grid_height = rows * target_size[1]
        grid_image = Image.new('RGB', (grid_width, grid_height), 'white')
        
        # Place content image in top-left
        grid_image.paste(content_resized, (0, 0))
        
        # Place style examples
        for i, style_img in enumerate(style_images[:rows * cols - 1]):
            row = (i + 1) // cols
            col = (i + 1) % cols
            x = col * target_size[0]
            y = row * target_size[1]
            
            # Simulate style transfer (simple blend for demo)
            styled = Image.blend(
                content_resized, 
                style_img.resize(target_size, Image.Resampling.LANCZOS),
                0.3
            )
            grid_image.paste(styled, (x, y))
        
        return grid_image
    
    def optimize_for_web(self, image: Image.Image, max_size: int = 1024,
                        quality: int = 85) -> bytes:
        """Optimize image for web delivery"""
        # Resize if too large
        width, height = image.size
        if max(width, height) > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            # Create white background for transparent images
            rgb_image = Image.new('RGB', image.size, 'white')
            if image.mode == 'RGBA':
                rgb_image.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
            else:
                rgb_image.paste(image)
            image = rgb_image
        
        # Save as JPEG with compression
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    
    def extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from image"""
        try:
            from sklearn.cluster import KMeans
        except ImportError:
            # Fallback: simple color sampling
            image = image.resize((50, 50))
            colors = []
            for i in range(0, 50, 10):
                for j in range(0, 50, 10):
                    color = image.getpixel((i, j))
                    if isinstance(color, tuple) and len(color) >= 3:
                        colors.append(color[:3])
            return colors[:num_colors]
        
        # Resize image for faster processing
        image = image.resize((150, 150))
        data = np.array(image.convert('RGB'))
        data = data.reshape((-1, 3))
        
        # Use K-means clustering to find dominant colors
        kmeans = KMeans(n_clusters=num_colors, random_state=42)
        kmeans.fit(data)
        
        # Get the colors
        colors = kmeans.cluster_centers_.astype(int)
        return [tuple(color) for color in colors]
    
    def create_color_palette(self, image: Image.Image, palette_size: Tuple[int, int] = (300, 50)) -> Image.Image:
        """Create a color palette from dominant colors"""
        colors = self.extract_dominant_colors(image)
        
        palette_img = Image.new('RGB', palette_size, 'white')
        color_width = palette_size[0] // len(colors)
        
        for i, color in enumerate(colors):
            x1 = i * color_width
            x2 = x1 + color_width
            
            # Fill the section with the color
            for x in range(x1, min(x2, palette_size[0])):
                for y in range(palette_size[1]):
                    palette_img.putpixel((x, y), color)
        
        return palette_img
    
    def apply_texture_overlay(self, image: Image.Image, texture_type: str = "canvas") -> Image.Image:
        """Apply texture overlay to simulate different mediums"""
        if texture_type == "canvas":
            return self._apply_canvas_texture(image)
        elif texture_type == "paper":
            return self._apply_paper_texture(image)
        else:
            return image
    
    def _apply_canvas_texture(self, image: Image.Image) -> Image.Image:
        """Apply canvas texture overlay"""
        # Create a simple canvas texture pattern
        width, height = image.size
        texture = Image.new('L', (width, height))
        
        # Generate canvas-like pattern
        pixels = []
        for y in range(height):
            for x in range(width):
                # Create a weave pattern
                intensity = 128 + int(30 * np.sin(x * 0.1) * np.cos(y * 0.1))
                pixels.append(max(0, min(255, intensity)))
        
        texture.putdata(pixels)
        texture_rgb = texture.convert('RGB')
        
        # Blend with original image
        return Image.blend(image, texture_rgb, 0.1)
    
    def _apply_paper_texture(self, image: Image.Image) -> Image.Image:
        """Apply paper texture overlay"""
        # Add subtle noise for paper texture
        img_array = np.array(image)
        noise = np.random.randint(-15, 15, img_array.shape, dtype=np.int16)
        textured = np.clip(img_array.astype(np.int16) + noise, 0, 255)
        
        return Image.fromarray(textured.astype(np.uint8))


def create_style_preview_grid(content_image: Image.Image, styles: List[str]) -> Image.Image:
    """Create a preview grid of different style applications"""
    processor = AdvancedImageProcessor()
    
    # Resize content image
    size = (200, 200)
    content_resized = content_image.resize(size, Image.Resampling.LANCZOS)
    
    # Create grid
    grid_cols = 3
    grid_rows = (len(styles) + 2) // grid_cols  # +2 for original
    
    grid_width = grid_cols * size[0]
    grid_height = grid_rows * size[1]
    
    grid = Image.new('RGB', (grid_width, grid_height), 'white')
    
    # Place original image
    grid.paste(content_resized, (0, 0))
    
    # Apply different styles
    for i, style in enumerate(styles):
        row = (i + 1) // grid_cols
        col = (i + 1) % grid_cols
        x = col * size[0]
        y = row * size[1]
        
        styled = processor.apply_artistic_filters(content_resized, style)
        grid.paste(styled, (x, y))
    
    return grid