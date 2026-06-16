from langchain_core.tools import tool

from app.data.repository import MenuRepository
from app.tools.schemas import FindItemInput, FilterByRestrictionInput

# One shared repository instance, loaded once at import time.
_repo = MenuRepository()


@tool(args_schema=FindItemInput)
def search_menu_items(query: str) -> list[dict]:
    """Look up one specific menu item by name and return its full details
    (ingredients, possible allergens, preparation, spice level, etc.).

    Use this when the question is about a PARTICULAR dish or drink — for
    example "Does the Pisco Sour have egg?", "What's in the Butter Chicken?",
    or "How is the Amaretto Sour made?". Returns a list because a partial
    name may match more than one item. Returns an empty list if nothing
    matches.
    """
    return _repo.find_item(query)


@tool
def get_menu_summary() -> list[dict]:
    """Return a lightweight list of every menu item — names, categories, and
    whether each is food or drink — WITHOUT ingredients or details.

    Use this for open-ended or browsing questions where you need to see what
    exists before answering, for example "What do you recommend?", "What
    cocktails do you have?", or "What's on the menu?". After seeing the list,
    call search_menu_items if you need the details of a specific item.
    """
    return _repo.all_summaries()


@tool(args_schema=FilterByRestrictionInput)
def filter_by_dietary(restriction: str) -> dict:
    """Return menu items that do NOT have a given allergen flagged, along with
    a mandatory safety disclaimer.

    Use this for dietary questions like "What's safe for a nut allergy?" or
    "Anything without dairy?". IMPORTANT: the result is based on inferred
    ingredient keywords, not verified data. Never tell staff a dish is
    definitively "safe" — always relay the disclaimer and advise confirming
    with the kitchen.
    """
    return _repo.filter_by_restriction(restriction)


# Convenient list to bind to the agent in Phase 3.
ALL_TOOLS = [search_menu_items, get_menu_summary, filter_by_dietary]