from app.tools.menu_tools import (
    search_menu_items,
    get_menu_summary,
    filter_by_dietary,
    ALL_TOOLS,
)


def test_all_tools_registered():
    assert len(ALL_TOOLS) == 3


def test_search_menu_items_finds_known_item():
    # .invoke is how you call a LangChain tool with its args.
    results = search_menu_items.invoke({"query": "pisco"})
    assert isinstance(results, list)
    assert any("pisco" in it["name"].lower() for it in results)


def test_search_menu_items_missing_returns_empty():
    results = search_menu_items.invoke({"query": "xyznotreal"})
    assert results == []


def test_get_menu_summary_is_lightweight():
    summary = get_menu_summary.invoke({})
    assert isinstance(summary, list)
    assert len(summary) > 0
    for s in summary:
        assert set(s.keys()) == {"name", "category", "type"}


def test_filter_by_dietary_has_disclaimer_and_items():
    result = filter_by_dietary.invoke({"restriction": "egg"})
    assert "disclaimer" in result
    assert "items_without_flagged_allergen" in result
    assert isinstance(result["items_without_flagged_allergen"], list)


def test_tool_descriptions_exist():
    # The LLM relies on these; make sure none are empty.
    for t in ALL_TOOLS:
        assert t.description and len(t.description) > 20