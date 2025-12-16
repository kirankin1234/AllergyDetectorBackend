from typing import List, Optional, Annotated
from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator, WithJsonSchema
from datetime import datetime


def validate_object_id(v):
    if isinstance(v, ObjectId):
        return v
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId format")
    return ObjectId(v)


PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    WithJsonSchema({"type": "string"}, mode="validation"),
]


class AllergenIn(BaseModel):
    name: str = Field(..., min_length=1)
    severity: str = Field(..., pattern="^(HIGH|MEDIUM|LOW)$")
    keywords: List[str] = Field(..., min_length=1)


class AllergenOut(AllergenIn):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "extra": "ignore",
        "arbitrary_types_allowed": True,   # <- add this line
    }


class MatchResult(BaseModel):
    allergen: str
    keyword_found: str
    severity: str
    position: Optional[dict] = None


class ScanResult(BaseModel):
    safe: bool
    matches: List[MatchResult]
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
