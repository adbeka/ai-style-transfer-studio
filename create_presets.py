"""
Style preset generator for creating sample style images
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import os


def create_preset_images():
    """Create sample preset style images"""
    os.makedirs("public", exist_ok=True)
    
    # Van Gogh style preset
    van_gogh = create_van_gogh_style()
    van_gogh.save("public/preset-vangogh.jpg")
    
    # Picasso style preset  
    picasso = create_picasso_style()
    picasso.save("public/preset-picasso.jpg")
    
    # Monet style preset
    monet = create_monet_style()
    monet.save("public/preset-monet.jpg")
    
    # Pop art style preset
    pop_art = create_pop_art_style()
    pop_art.save("public/preset-popart.jpg")
    
    # Create example images
    create_example_images()
    
    print("Sample preset images created in public/ directory")


def create_van_gogh_style():
    """Create Van Gogh inspired swirly pattern"""
    img = Image.new('RGB', (300, 300), (30, 60, 150))
    draw = ImageDraw.Draw(img)
    
    # Create swirly patterns
    for i in range(20):
        for j in range(20):
            x = i * 15
            y = j * 15
            # Create spiral pattern
            for r in range(5, 25, 2):
                for angle in range(0, 360, 10):
                    rad = np.radians(angle)
                    px = x + r * np.cos(rad + r * 0.1)
                    py = y + r * np.sin(rad + r * 0.1)
                    if 0 <= px < 300 and 0 <= py < 300:
                        color_intensity = int(255 * (1 - r / 25))
                        color = (color_intensity, color_intensity // 2, 255 - color_intensity)
                        try:
                            img.putpixel((int(px), int(py)), color)
                        except:
                            pass
    
    # Apply blur for painterly effect
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Enhance colors
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.5)
    
    return img


def create_picasso_style():
    """Create Picasso inspired geometric pattern"""
    img = Image.new('RGB', (300, 300), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    # Create geometric shapes
    for i in range(15):
        x = np.random.randint(0, 250)
        y = np.random.randint(0, 250)
        w = np.random.randint(20, 80)
        h = np.random.randint(20, 80)
        color = colors[i % len(colors)]
        
        # Draw various geometric shapes
        if i % 3 == 0:
            draw.rectangle([x, y, x+w, y+h], fill=color, outline=(0, 0, 0), width=2)
        elif i % 3 == 1:
            draw.ellipse([x, y, x+w, y+h], fill=color, outline=(0, 0, 0), width=2)
        else:
            points = [(x, y+h), (x+w//2, y), (x+w, y+h)]
            draw.polygon(points, fill=color, outline=(0, 0, 0), width=2)
    
    return img


def create_monet_style():
    """Create Monet inspired impressionist pattern"""
    img = Image.new('RGB', (300, 300), (200, 220, 255))
    
    # Create brushstroke-like pattern
    img_array = np.array(img)
    
    # Add color variations
    for i in range(300):
        for j in range(300):
            # Create water lily pond effect
            center_x, center_y = 150, 150
            dist = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            
            if dist < 80:
                # Water lily area
                r = int(150 + 30 * np.sin(dist * 0.1))
                g = int(200 + 20 * np.cos(dist * 0.1))
                b = int(100 + 50 * np.sin(dist * 0.2))
            else:
                # Water area
                r = int(100 + 50 * np.sin(i * 0.02))
                g = int(150 + 30 * np.cos(j * 0.02))
                b = int(200 + 25 * np.sin((i+j) * 0.01))
            
            img_array[j, i] = [max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))]
    
    img = Image.fromarray(img_array.astype(np.uint8))
    
    # Apply slight blur for impressionist effect
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    return img


def create_pop_art_style():
    """Create Pop Art inspired pattern"""
    img = Image.new('RGB', (300, 300), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Create halftone pattern
    colors = [(255, 0, 128), (255, 255, 0), (0, 255, 255), (255, 0, 0)]
    
    # Grid of dots
    for x in range(0, 300, 20):
        for y in range(0, 300, 20):
            color = colors[(x//20 + y//20) % len(colors)]
            radius = 8 + int(4 * np.sin((x+y) * 0.1))
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    # Add some bold lines
    for i in range(0, 300, 50):
        draw.line([(i, 0), (i, 300)], fill=(0, 0, 0), width=3)
        draw.line([(0, i), (300, i)], fill=(0, 0, 0), width=3)
    
    return img


def create_example_images():
    """Create example gallery images"""
    # Example 1: Abstract colorful
    img1 = Image.new('RGB', (400, 400), (255, 255, 255))
    draw1 = ImageDraw.Draw(img1)
    
    for i in range(100):
        x = np.random.randint(0, 350)
        y = np.random.randint(0, 350)
        r = np.random.randint(10, 50)
        color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        draw1.ellipse([x, y, x+r, y+r], fill=color)
    
    img1.save("public/example1.jpg")
    
    # Example 2: Gradient pattern
    img2 = Image.new('RGB', (400, 400))
    img2_array = np.zeros((400, 400, 3))
    
    for i in range(400):
        for j in range(400):
            img2_array[j, i] = [
                int(255 * i / 400),
                int(255 * j / 400),
                int(255 * (i + j) / 800)
            ]
    
    img2 = Image.fromarray(img2_array.astype(np.uint8))
    img2.save("public/example2.jpg")
    
    # Example 3: Geometric pattern
    img3 = create_picasso_style().resize((400, 400))
    img3.save("public/example3.jpg")
    
    # Create recent generation examples
    for i in range(1, 5):
        example = create_monet_style().resize((300, 300))
        example.save(f"public/recent{i}.jpg")
    
    # Create user avatars
    for i in range(1, 4):
        avatar = create_avatar(i)
        avatar.save(f"public/user{i}.jpg")


def create_avatar(user_id):
    """Create a simple avatar"""
    colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
    color = colors[user_id - 1]
    
    avatar = Image.new('RGB', (100, 100), color)
    draw = ImageDraw.Draw(avatar)
    
    # Draw simple face
    # Eyes
    draw.ellipse([25, 30, 35, 40], fill=(255, 255, 255))
    draw.ellipse([65, 30, 75, 40], fill=(255, 255, 255))
    draw.ellipse([28, 33, 32, 37], fill=(0, 0, 0))
    draw.ellipse([68, 33, 72, 37], fill=(0, 0, 0))
    
    # Smile
    draw.arc([35, 50, 65, 70], 0, 180, fill=(255, 255, 255), width=3)
    
    return avatar


if __name__ == "__main__":
    create_preset_images()