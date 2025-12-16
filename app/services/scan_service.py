from typing import List
from datetime import datetime
from bson import ObjectId
import re

from app.database.mongo import allergen_collection, scan_collection
from app.models.allergen_model import MatchResult, ScanResult
from app.utils.document_processor import kmp_search


STOP_WORDS = {
    # Articles
    "a", "an", "the",

    # Conjunctions
    "and", "or", "but", "nor", "yet", "so",

    # Prepositions
    "in", "on", "at", "of", "for", "to", "with", "by", "from",
    "about", "against", "between", "into", "through", "during",
    "before", "after", "above", "below", "under", "over", "up",
    "down", "off", "out", "around", "near", "within", "without",

    # Pronouns
    "i", "me", "my", "mine", "myself",
    "we", "us", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "it", "its", "itself",
    "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those",

    # Auxiliary / Helping verbs
    "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did",
    "have", "has", "had",
    "will", "would", "shall", "should",
    "can", "could", "may", "might", "must",

    # Adverbs / fillers
    "very", "too", "so", "just", "only", "also", "not",

    # Common PDF noise / generic words
    "etc", "etcetera", "via", "per",

    # Quantifiers
    "some", "any", "all", "each", "every", "few", "many", "much", "more", "most",

    # Time / order words
    "now", "then", "when", "while", "before", "after",

    # Comparatives
    "such", "same", "other", "another"
}






# -------------------------------------------------
# Helper: tokenize text (works for PDF + plain text)
# -------------------------------------------------
def tokenize(text: str) -> List[str]:
    """
    Converts text into meaningful lowercase tokens.
    Removes stop-words to avoid false allergy matches.
    Works for both PDF-extracted and plain text.
    """
    tokens = re.findall(r"\b\w+\b", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]



# -------------------------------------------------
# Main Scan Logic
# -------------------------------------------------
def scan_text(text: str, selected_allergen_ids: List[str]) -> ScanResult:
    """
    Scans user input or PDF-extracted text against selected allergens.
    Supports:
    - Full phrase matching
    - Partial word matching
    - Multiple matches
    - PDF text
    """

    text_lower = text.lower()
    tokens = tokenize(text_lower)

    object_ids = [ObjectId(aid) for aid in selected_allergen_ids]
    allergens = list(allergen_collection.find({"_id": {"$in": object_ids}}))

    matches: List[MatchResult] = []
    detected_keywords = set()   # prevents duplicates

    for allergen in allergens:
        allergen_name = allergen["name"]
        severity = allergen["severity"]
        keywords = allergen.get("keywords", [])

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # -------- Case 1: Full phrase exists --------
            if kmp_search(text_lower, keyword_lower):
                if keyword_lower not in detected_keywords:
                    matches.append(
                        MatchResult(
                            allergen=allergen_name,
                            keyword_found=keyword,
                            severity=severity,
                            position=None,
                        )
                    )
                    detected_keywords.add(keyword_lower)
                continue

            # -------- Case 2: Partial word exists --------
            # Example: "dust" matches "small dust"
            keyword_tokens = tokenize(keyword_lower)

            for kt in keyword_tokens:
                for token in tokens:
                    if kmp_search(token, kt):
                        if keyword_lower not in detected_keywords:
                            matches.append(
                                MatchResult(
                                    allergen=allergen_name,
                                    keyword_found=keyword,
                                    severity=severity,
                                    position=None,
                                )
                            )
                            detected_keywords.add(keyword_lower)
                        break
                else:
                    continue
                break

    result = ScanResult(
        safe=len(matches) == 0,
        matches=matches,
        timestamp=datetime.now().isoformat(),
    )

    # Store scan history (PDF or text — same logic)
    scan_collection.insert_one(result.model_dump())

    return result
