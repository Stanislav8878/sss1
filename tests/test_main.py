import pytest
from pathlib import Path
from main import Product, Category, load_categories_from_json

@pytest.fixture
def sample_product():
    return Product("Test", "Desc", 100.0, 10)

@pytest.fixture
def sample_category(sample_product):
    return Category("Test Cat", "Desc", [sample_product])

def test_product(sample_product):
    assert sample_product.name == "Test"

def test_category(sample_category):
    assert sample_category.name == "Test Cat"

def test_load_categories():
    # Используем путь относительно тестов
    test_data_path = Path(__file__).parent.parent / "src" / "products.json"
    categories = load_categories_from_json(str(test_data_path))
    assert len(categories) > 0
    assert isinstance(categories[0].products[0], Product)