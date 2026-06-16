from pathlib import Path
import pytest
from app.data.repository import MenuRepository

DATA_DIR = Path(__file__).parent.parent / "app" / "data"


@pytest.fixture(scope="module")
def repo() -> MenuRepository:
    return MenuRepository(data_dir=DATA_DIR)


def test_loads_items(repo):
    assert len(repo) > 0


def test_find_existing_item(repo):
    results = repo.find_item("pisco")
    assert len(results) >= 1
    assert any("pisco" in it["name"].lower() for it in results)


def test_find_is_case_insensitive(repo):
    assert repo.find_item("amaretto") == repo.find_item("AMARETTO")


def test_find_missing_item_returns_empty(repo):
    assert repo.find_item("xyznotareal item") == []


def test_find_empty_query_returns_empty(repo):
    assert repo.find_item("") == []
    assert repo.find_item("   ") == []


def test_summaries_are_lightweight(repo):
    summaries = repo.all_summaries()
    assert len(summaries) == len(repo)
    for s in summaries:
        assert set(s.keys()) == {"name", "category", "type"}


def test_every_item_has_allergen_fields(repo):
    for it in repo.items:
        assert isinstance(it["possible_allergens"], list)
        assert isinstance(it["allergen_sources"], dict)
        assert isinstance(it["dietary_notes"], list)


def test_allergen_source_is_valid(repo):
    for it in repo.items:
        for allergen, source in it["allergen_sources"].items():
            assert source in {"curated", "inferred"}
            assert allergen in it["possible_allergens"]


def test_dietary_filter_includes_disclaimer(repo):
    result = repo.filter_by_restriction("egg")
    assert result["disclaimer"]


def test_dietary_filter_excludes_unsafe_items(repo):
    result = repo.filter_by_restriction("nuts")
    safe_names = {s["name"] for s in result["items_without_flagged_allergen"]}
    for it in repo.items:
        if "nuts" in it["possible_allergens"]:
            assert it["name"] not in safe_names