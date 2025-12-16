from typing import List
from fastapi import APIRouter

from app.services.allergen_service import (
    create_allergen,
    get_all_allergens,
    update_allergen,
    delete_allergen,
)
from app.models.allergen_model import AllergenIn, AllergenOut

router = APIRouter(prefix="/allergens", tags=["Allergens"])

@router.post("/", response_model=dict)
def add_allergen(data: AllergenIn):
    return create_allergen(data)

@router.get("/", response_model=List[AllergenOut])
def get_allergens():
    return get_all_allergens()

@router.put("/{allergen_id}", response_model=dict)
def edit_allergen(allergen_id: str, data: AllergenIn):
    return update_allergen(allergen_id, data)

@router.delete("/{allergen_id}", response_model=dict)
def remove_allergen(allergen_id: str):
    return delete_allergen(allergen_id)
