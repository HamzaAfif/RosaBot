from pydantic import BaseModel, Field


class FindItemInput(BaseModel):
    query: str = Field(
        ...,
        description=(
            "The name (or part of the name) of a single menu item to look up, "
            "e.g. 'Pisco Sour', 'Butter Chicken', 'Amaretto'. Use this when the "
            "guest or staff member asks about one specific dish or drink."
        ),
    )


class FilterByRestrictionInput(BaseModel):
    restriction: str = Field(
        ...,
        description=(
            "A single allergen or dietary keyword to screen out, in lowercase, "
            "e.g. 'egg', 'dairy', 'nuts', 'gluten', 'shellfish'. Returns items "
            "that do NOT have this allergen flagged. This is a hint only, never "
            "a safety guarantee."
        ),
    )