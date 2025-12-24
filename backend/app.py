from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import torch
from model import StyleTransferModel
from utils import load_image, tensor_to_image
from PIL import Image
import io
import os

app = FastAPI(title="AI Style Transfer Studio", description="Real-time neural style transfer API")

model = None

def load_model():
    global model
    model = StyleTransferModel()
    model.eval()
    # Load pre-trained weights if available
    # model.load_state_dict(torch.load('path/to/weights.pth'))

@app.on_event("startup")
async def startup_event():
    load_model()

@app.post("/api/v1/style-transfer")
async def style_transfer(content: UploadFile = File(...), style: UploadFile = File(...)):
    try:
        content_image = Image.open(io.BytesIO(await content.read())).convert('RGB')
        style_image = Image.open(io.BytesIO(await style.read())).convert('RGB')
        
        content_tensor = load_image(content_image)
        style_tensor = load_image(style_image)
        
        with torch.no_grad():
            output_tensor = model(content_tensor, style_tensor)
        
        result_image = tensor_to_image(output_tensor)
        
        # Save result to temp file
        result_path = "/tmp/result.jpg"
        result_image.save(result_path)
        
        return FileResponse(result_path, media_type='image/jpeg', filename='styled_image.jpg')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/styles")
async def get_styles():
    # TODO: Return list of available styles
    return {"styles": ["impressionism", "cubism", "pop_art"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)