from typing import List
from bson import ObjectId
from fastapi import HTTPException

from app.database.mongo import allergen_collection
from app.models.allergen_model import AllergenIn, AllergenOut

def create_allergen(data: AllergenIn) -> dict:
    """Add a new allergen."""
    if allergen_collection.find_one({"name": data.name}):
        raise HTTPException(status_code=400, detail="Allergen with this name already exists")

    result = allergen_collection.insert_one(data.model_dump())
    return {"message": "Allergen added successfully", "id": str(result.inserted_id)}


def get_all_allergens() -> List[AllergenOut]:
    """Return all allergens."""
    allergens = list(allergen_collection.find())
    return [AllergenOut(**a) for a in allergens]


def update_allergen(allergen_id: str, data: AllergenIn) -> dict:
    """Update allergen by ID."""
    if not ObjectId.is_valid(allergen_id):
        raise HTTPException(status_code=400, detail="Invalid Allergen ID format")

    result = allergen_collection.update_one(
        {"_id": ObjectId(allergen_id)},
        {"$set": data.model_dump(exclude_unset=True)},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Allergen with ID '{allergen_id}' not found")

    return {"message": "Allergen updated successfully"}


def delete_allergen(allergen_id: str) -> dict:
    """Delete allergen by ID."""
    if not ObjectId.is_valid(allergen_id):
        raise HTTPException(status_code=400, detail="Invalid Allergen ID format")

    result = allergen_collection.delete_one({"_id": ObjectId(allergen_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Allergen with ID '{allergen_id}' not found")

    return {"message": "Allergen deleted successfully"}
