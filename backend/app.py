
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
from model import StyleTransferModel
from utils import load_image, tensor_to_image, validate_image, resize_for_processing
from PIL import Image
import io
import os
import time
import uuid
from datetime import datetime
from auth import auth_router, oauth2_scheme, get_current_active_user, User
from database import db
from image_processor import AdvancedImageProcessor, create_style_preview_grid
from typing import List, Optional


app = FastAPI(title="AI Style Transfer Studio", description="Real-time neural style transfer API")

# Ensure upload directories exist
os.makedirs("/tmp/uploads", exist_ok=True)
os.makedirs("/tmp/results", exist_ok=True)
os.makedirs("/tmp/styles", exist_ok=True)

# Initialize image processor
image_processor = AdvancedImageProcessor()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://frontend:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)



models = {}

def get_model(model_type: str = 'adain'):
    if model_type not in models:
        m = StyleTransferModel(model_type)
        m.eval()
        models[model_type] = m
    return models[model_type]




from fastapi import Query

@app.post("/api/v1/style-transfer")
async def style_transfer(
    request: Request,
    content: UploadFile = File(...),
    style: UploadFile = File(...),
    model_type: str = Query('adain', description="Model type: 'adain' or 'cartoon'"),
    style_strength: float = Query(1.0, ge=0.0, le=2.0, description="Style strength"),
    preserve_content: float = Query(0.0, ge=0.0, le=1.0, description="Content preservation"),
    artistic_filter: str = Query('none', description="Additional artistic filter"),
    current_user: User = Depends(get_current_active_user)
):
    try:
        start_time = time.time()
        
        # Validate images
        content_data = await content.read()
        style_data = await style.read()
        
        valid, msg = validate_image(io.BytesIO(content_data))
        if not valid:
            raise HTTPException(status_code=400, detail=f"Content image: {msg}")
            
        valid, msg = validate_image(io.BytesIO(style_data))
        if not valid:
            raise HTTPException(status_code=400, detail=f"Style image: {msg}")
        
        # Process images
        content_image = Image.open(io.BytesIO(content_data)).convert('RGB')
        style_image = Image.open(io.BytesIO(style_data)).convert('RGB')
        
        # Resize for processing
        content_image = resize_for_processing(content_image)
        style_image = resize_for_processing(style_image)
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Save input images
        content_path = f"/tmp/uploads/content_{session_id}.jpg"
        style_path = f"/tmp/uploads/style_{session_id}.jpg"
        content_image.save(content_path)
        style_image.save(style_path)
        
        # Perform style transfer
        content_tensor = load_image(content_image)
        style_tensor = load_image(style_image)
        model = get_model(model_type)
        
        with torch.no_grad():
            output_tensor = model(content_tensor, style_tensor)
        
        result_image = tensor_to_image(output_tensor)
        
        # Apply content preservation if requested
        if preserve_content > 0:
            result_image = image_processor.enhance_content_preservation(
                content_image, result_image, preserve_content
            )
        
        # Apply artistic filter if requested
        if artistic_filter != 'none':
            result_image = image_processor.apply_artistic_filters(result_image, artistic_filter)
        
        # Save result
        result_path = f"/tmp/results/result_{session_id}.jpg"
        result_image.save(result_path, quality=95)
        
        processing_time = time.time() - start_time
        
        # Save to database
        user_id = getattr(current_user, 'id', 1)  # Default for demo
        transfer_id = db.save_transfer_history(
            user_id=user_id,
            session_id=session_id,
            content_path=content_path,
            style_path=style_path,
            result_path=result_path,
            model_type=model_type,
            style_strength=style_strength,
            processing_time=processing_time
        )
        
        # Log analytics
        db.log_user_action(
            user_id=user_id,
            action='style_transfer',
            details={
                'model_type': model_type,
                'style_strength': style_strength,
                'preserve_content': preserve_content,
                'artistic_filter': artistic_filter,
                'processing_time': processing_time
            },
            ip_address=request.client.host if request.client else None
        )
        
        return FileResponse(
            result_path, 
            media_type='image/jpeg', 
            filename='styled_image.jpg',
            headers={
                'X-Transfer-ID': str(transfer_id),
                'X-Processing-Time': str(processing_time)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/presets")
async def get_style_presets():
    """Get available style presets from database"""
    presets = db.get_style_presets()
    return {"presets": presets}

@app.post("/api/v1/history")
async def get_user_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's style transfer history"""
    user_id = getattr(current_user, 'id', 1)
    history = db.get_user_history(user_id, limit)
    return {"history": history}

@app.post("/api/v1/preferences")
async def save_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Save user preferences"""
    user_id = getattr(current_user, 'id', 1)
    db.save_user_preferences(user_id, preferences)
    return {"message": "Preferences saved successfully"}

@app.get("/api/v1/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_active_user)
):
    """Get user preferences"""
    user_id = getattr(current_user, 'id', 1)
    preferences = db.get_user_preferences(user_id)
    return preferences

@app.post("/api/v1/gallery")
async def create_gallery(
    name: str,
    description: str = "",
    is_public: bool = False,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new gallery"""
    user_id = getattr(current_user, 'id', 1)
    gallery_id = db.create_gallery(user_id, name, description, is_public)
    return {"gallery_id": gallery_id, "message": "Gallery created successfully"}

@app.get("/api/v1/galleries")
async def get_user_galleries(
    current_user: User = Depends(get_current_active_user)
):
    """Get user's galleries"""
    user_id = getattr(current_user, 'id', 1)
    galleries = db.get_user_galleries(user_id)
    return {"galleries": galleries}

@app.post("/api/v1/style-preview")
async def create_style_preview(
    content: UploadFile = File(...),
    styles: List[str] = Query(["oil_painting", "watercolor", "pencil_sketch"])
):
    """Create a preview grid with different styles"""
    try:
        content_image = Image.open(io.BytesIO(await content.read())).convert('RGB')
        content_image = resize_for_processing(content_image, max_size=512)
        
        preview_grid = create_style_preview_grid(content_image, styles)
        
        result_path = f"/tmp/preview_{uuid.uuid4().hex}.jpg"
        preview_grid.save(result_path)
        
        return FileResponse(result_path, media_type='image/jpeg', filename='style_preview.jpg')
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/popular-styles")
async def get_popular_styles(limit: int = Query(10, ge=1, le=50)):
    """Get most popular style presets"""
    popular_styles = db.get_popular_styles(limit)
    return {"popular_styles": popular_styles}

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary (admin endpoint)"""
    # In production, add admin authentication
    summary = db.get_analytics_summary()
    return summary

@app.post("/api/v1/style-transfer-batch")
async def style_transfer_batch(
    files: list[UploadFile] = File(...),
    style: UploadFile = File(...),
    model_type: str = Query('adain', description="Model type: 'adain' or 'cartoon'")
):
    """Process multiple images with the same style"""
    try:
        style_image = Image.open(io.BytesIO(await style.read())).convert('RGB')
        style_tensor = load_image(style_image)
        model = get_model(model_type)
        
        results = []
        for i, content_file in enumerate(files):
            content_image = Image.open(io.BytesIO(await content_file.read())).convert('RGB')
            content_tensor = load_image(content_image)
            
            with torch.no_grad():
                output_tensor = model(content_tensor, style_tensor)
            
            result_image = tensor_to_image(output_tensor)
            result_path = f"/tmp/batch_result_{i}.jpg"
            result_image.save(result_path)
            results.append(result_path)
        
        # In a real implementation, return a zip file or individual file links
        return {"message": f"Processed {len(files)} images", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/text-to-image")
async def text_to_image(request: dict):
    """Generate image from text prompt using a simple approach"""
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # For demo purposes, create a placeholder image with the prompt
        # In a real implementation, you would use models like DALL-E, Stable Diffusion, etc.
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        # Create a colorful gradient background
        width, height = 512, 512
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        for y in range(height):
            r = int(255 * (y / height))
            g = int(128 + 127 * ((height - y) / height))
            b = int(255 * (1 - y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add text
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        wrapped_text = textwrap.fill(f"Generated: {prompt}", width=30)
        draw.text((20, height//2 - 50), wrapped_text, fill=(255, 255, 255), font=font)
        
        # Add decorative elements based on prompt keywords
        if "cat" in prompt.lower():
            draw.ellipse([width-100, 50, width-50, 100], fill=(255, 200, 100))
        if "van gogh" in prompt.lower() or "swirl" in prompt.lower():
            for i in range(10):
                x, y = i*30, i*20
                draw.ellipse([x, y, x+20, y+20], outline=(255, 255, 0), width=3)
        
        result_path = "/tmp/text_to_image_result.jpg"
        img.save(result_path)
        return FileResponse(result_path, media_type='image/jpeg', filename='generated_image.jpg')
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)