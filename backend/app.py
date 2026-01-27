
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
from model import StyleTransferModel
from utils import load_image, tensor_to_image
from PIL import Image
import io
import os
from auth import auth_router


app = FastAPI(title="AI Style Transfer Studio", description="Real-time neural style transfer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://frontend:5173"],
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
    content: UploadFile = File(...),
    style: UploadFile = File(...),
    model_type: str = Query('adain', description="Model type: 'adain' or 'cartoon'")
):
    try:
        content_image = Image.open(io.BytesIO(await content.read())).convert('RGB')
        style_image = Image.open(io.BytesIO(await style.read())).convert('RGB')
        content_tensor = load_image(content_image)
        style_tensor = load_image(style_image)
        model = get_model(model_type)
        with torch.no_grad():
            output_tensor = model(content_tensor, style_tensor)
        result_image = tensor_to_image(output_tensor)
        result_path = "/tmp/result.jpg"
        result_image.save(result_path)
        return FileResponse(result_path, media_type='image/jpeg', filename='styled_image.jpg')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/styles")
async def get_styles():
    # Return available style models
    return {"styles": ["adain", "cartoon"]}

@app.post("/api/v1/text-to-image")
async def text_to_image(request: dict):
    # Placeholder for text-to-image functionality
    return {"message": "Text-to-image feature coming soon", "prompt": request.get("prompt")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)