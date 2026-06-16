"""
MenuRepository — the single source of truth for India Rosa's menu data.

It loads the three menu files plus a kitchen-curated allergy guide, normalizes
every item into one consistent shape, and exposes deterministic query methods.

ALLERGEN STRATEGY — "curated wins, keywords fill gaps":
    1. Curated data (allergy_guide.json) is authoritative. If the kitchen lists
       a dish under contains_nuts, it is flagged nuts, source = "curated".
    2. Keyword inference runs underneath and catches anything curated did not
       mention (e.g. egg white in cocktails), source = "inferred".
    3. Each allergen flag therefore carries a SOURCE so the bot can speak with
       the right confidence. Neither source is a guarantee — the disclaimer
       always applies and staff must confirm with the kitchen.

    `lactose_free_potential` is conditional ("if coconut milk") and is NOT a
    clean flag — it is surfaced as a separate "note", never as "dairy-free".
"""

from __future__ import annotations

import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

DATA_DIR = Path(__file__).parent

# Keyword -> allergen label. Best-effort fallback layer. Extend as needed.
ALLERGEN_KEYWORDS: dict[str, str] = {
    "blanc d'oeuf": "egg",
    "oeuf": "egg",
    "œuf": "egg",
    "cream": "dairy",
    "milk": "dairy",
    "butter": "dairy",
    "baileys": "dairy",
    "irish cream": "dairy",
    "coconut cream": "dairy",
    "lait de coco": "dairy",
    "amaretto": "nuts",
    "disaronno": "nuts",
    "orgeat": "nuts",
    "lait": "dairy",
    "crème": "dairy",
    "creme": "dairy",
    "beurre": "dairy",
    "fromage": "dairy",
    "parmesan": "dairy",
    "paneer": "dairy",
    "ghee": "dairy",
    "yogourt": "dairy",
    "yaourt": "dairy",
    "noix": "nuts",
    "cajou": "nuts",
    "amande": "nuts",
    "pacane": "nuts",
    "pistache": "nuts",
    "arachide": "peanuts",
    "gluten": "gluten",
    "blé": "gluten",
    "ble": "gluten",
    "farine": "gluten",
    "naan": "gluten",
    "soja": "soy",
    "poisson": "fish",
    "crevette": "shellfish",
    "moule": "shellfish",
    "fruits de mer": "shellfish",
}

DIETARY_DISCLAIMER = (
    "Allergen info combines kitchen-provided lists with automatic ingredient "
    "checks. It is not a guarantee — always confirm allergies with the kitchen."
)


def _normalize_name(name: str) -> str:
    """Loose key for matching names across files despite spelling/accents.

    Lowercase, strip accents, drop parenthetical notes, collapse spacing.
    'Aloo Tikki' and 'Aloo Tiki' -> 'aloo tikki'/'aloo tiki' still differ by a
    letter, so we ALSO compare on a prefix; see _name_matches.
    """
    name = name.split("(")[0]  # drop "(pacanes)" etc.
    name = name.split("/")[0]  # drop "Madras / Punjabi" tails for the key
    nfkd = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in nfkd if not unicodedata.combining(c))
    name = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    return re.sub(r"\s+", " ", name).strip()


def _name_matches(menu_name: str, guide_name: str) -> bool:
    """True if a menu item and a curated-guide entry refer to the same dish."""
    a, b = _normalize_name(menu_name), _normalize_name(guide_name)
    if not a or not b:
        return False
    return a == b or a.startswith(b) or b.startswith(a) or a in b or b in a


def _infer_possible_allergens(ingredients: list[str]) -> set[str]:
    found: set[str] = set()
    for ing in ingredients:
        low = ing.lower()
        for keyword, label in ALLERGEN_KEYWORDS.items():
            if keyword in low:
                found.add(label)
    return found


class MenuRepository:
    def __init__(self, data_dir: Path | str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self._items: list[dict] = []
        self._guide: dict = {}
        self._load_guide()
        self._load_all()

    # ---- loading -------------------------------------------------------

    def _read(self, filename: str) -> dict:
        with open(self.data_dir / filename, encoding="utf-8") as f:
            return json.load(f)

    def _load_guide(self) -> None:
        try:
            self._guide = self._read("allergy_guide.json")
        except FileNotFoundError:
            self._guide = {}

    def _curated_for(self, name: str) -> tuple[set[str], list[str]]:
        """Return (curated allergens, notes) for a menu item by name."""
        allergens: set[str] = set()
        notes: list[str] = []
        guide = self._guide
        if any(_name_matches(name, g) for g in guide.get("contains_gluten", [])):
            allergens.add("gluten")
        if any(_name_matches(name, g) for g in guide.get("contains_nuts", [])):
            allergens.add("nuts")
        if any(_name_matches(name, g) for g in guide.get("lactose_free_potential", [])):
            notes.append("May be made dairy-free on request (e.g. coconut milk) — confirm with kitchen.")
        if any(_name_matches(name, g) for g in guide.get("vegan_options", [])):
            notes.append("Listed by the kitchen as a vegan option.")
        return allergens, notes

    def _normalize(self, raw: dict, *, category: str, type_: str) -> dict:
        name = raw.get("name", "").strip()
        ingredients = raw.get("ingredients", []) or []

        inferred = _infer_possible_allergens(ingredients)
        curated, notes = self._curated_for(name)

        sources: dict[str, str] = {}
        for a in curated:
            sources[a] = "curated"
        for a in inferred:
            sources.setdefault(a, "inferred")  

        return {
            "name": name,
            "category": category,
            "type": type_,
            "ingredients": ingredients,
            "possible_allergens": sorted(sources.keys()),
            "allergen_sources": sources,  # {"nuts": "curated", "dairy": "inferred"}
            "dietary_notes": notes,
            "description": raw.get("description"),
            "spice_level": raw.get("spice_level"),
            "method": raw.get("method"),
            "glass": raw.get("glass"),
            "ice": raw.get("ice"),
            "garnish": raw.get("garnish"),
            "note": raw.get("note"),
        }

    def _load_all(self) -> None:
        self._items = []
        self._load_signature_drinks("SignatureDrinks_hiver_2026.json")
        self._load_classic_cocktails("cocktail_classics.json")
        self._load_food("foodMenu.json")

    def _load_signature_drinks(self, filename: str) -> None:
        for raw in self._read(filename).get("cocktails", []):
            cat = raw.get("category", "Signature")
            self._items.append(self._normalize(raw, category=cat, type_="drink"))

    def _load_classic_cocktails(self, filename: str) -> None:
        for raw in self._read(filename).get("sections", {}).get("cocktails", []):
            self._items.append(self._normalize(raw, category="Classic", type_="drink"))

    def _load_food(self, filename: str) -> None:
        for section, items in self._read(filename).get("sections", {}).items():
            for raw in items:
                self._items.append(self._normalize(raw, category=section, type_="food"))

    # ---- queries -------------------------------------------------------

    def find_item(self, query: str, fuzzy_cutoff: float = 0.6) -> list[dict]:
        """Find menu items by name.

        Strategy: try fast exact substring match first (precise). Only if that
        finds nothing, fall back to fuzzy matching to catch typos and small
        misspellings (e.g. "poulet au boeur" -> "Poulet au beurre"). This keeps
        precise queries precise while still helping on misspellings.
        """
        q = query.strip().lower()
        if not q:
            return []

        # 1. Exact substring match (fast, precise).
        exact = [it for it in self._items if q in it["name"].lower()]
        if exact:
            return exact

        # 2. Fuzzy fallback: score every item name against the query, keep the
        #    close ones. Also check word-level overlap so a typo in one word of
        #    a multi-word dish still matches.
        scored = []
        for it in self._items:
            name = it["name"].lower()
            ratio = SequenceMatcher(None, q, name).ratio()
            # also compare against each word, helps short queries vs long names
            word_ratio = max(
                (SequenceMatcher(None, q, w).ratio() for w in name.split()),
                default=0.0,
            )
            best = max(ratio, word_ratio)
            if best >= fuzzy_cutoff:
                scored.append((best, it))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [it for _, it in scored[:5]]  # top 5 closest matches

    def all_summaries(self) -> list[dict]:
        return [
            {"name": it["name"], "category": it["category"], "type": it["type"]}
            for it in self._items
        ]

    def filter_by_restriction(self, restriction: str) -> dict:
        r = restriction.strip().lower()
        safe = [it for it in self._items if r not in it["possible_allergens"]]
        return {
            "restriction": r,
            "disclaimer": DIETARY_DISCLAIMER,
            "items_without_flagged_allergen": [
                {"name": it["name"], "category": it["category"], "type": it["type"]}
                for it in safe
            ],
        }

    # ---- convenience ---------------------------------------------------

    def __len__(self) -> int:
        return len(self._items)

    @property
    def items(self) -> list[dict]:
        return list(self._items)