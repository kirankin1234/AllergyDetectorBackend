from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.scan_service import scan_text
from app.utils.document_processor import extract_text_from_document, extract_text_from_image
from app.models.allergen_model import ScanResult

router = APIRouter(prefix="/scan", tags=["Scan"])

@router.post("/", response_model=ScanResult)
async def scan(
    selected_allergen_ids: List[str] = Form(...),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    if not selected_allergen_ids:
        raise HTTPException(status_code=400, detail="No allergens selected for scan.")

    analysis_text = ""

    if text:
        analysis_text = text
    elif file:
        file_content = await file.read()
        if file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
            analysis_text = extract_text_from_image(file_content)
        elif file.content_type in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]:
            analysis_text = extract_text_from_document(file_content, file.filename)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    if not analysis_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract any readable text from the input.")

    return scan_text(
        text=analysis_text,
        selected_allergen_ids=selected_allergen_ids,
    )
