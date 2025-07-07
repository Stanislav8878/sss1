import pytest
from pathlib import Path
from main import Product, Category, load_categories_from_json
from unittest.mock import patch
import json


@pytest.fixture(autouse=True)
def reset_counters():
    """Сбрасывает счетчики перед каждым тестом"""
    Category.category_count = 0
    Category.product_count = 0
    yield


@pytest.fixture
def sample_product():
    return Product("Test", "Desc", 100.0, 10)


@pytest.fixture
def sample_category(sample_product):
    return Category("Test Cat", "Desc", [sample_product])


@pytest.fixture
def sample_products_json(tmp_path):
    data = [{
        "name": "Test Category",
        "description": "Test Desc",
        "products": [{
            "name": "Test Product",
            "description": "Test Product Desc",
            "price": 100.0,
            "quantity": 5
        }]
    }]
    file_path = tmp_path / "products.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")
    return file_path


def test_product_init(sample_product):
    assert sample_product.name == "Test"
    assert sample_product.description == "Desc"
    assert sample_product.price == 100.0
    assert sample_product.quantity == 10


def test_category_init(sample_category):
    assert sample_category.name == "Test Cat"
    assert sample_category.description == "Desc"
    assert "Test, 100.0 руб. Остаток: 10 шт." in sample_category.products
    assert Category.category_count == 1
    assert Category.product_count == 1


def test_add_product(sample_category):
    new_product = Product("New", "New Desc", 200.0, 5)
    sample_category.add_product(new_product)
    assert "New, 200.0 руб. Остаток: 5 шт." in sample_category.products
    assert Category.product_count == 2


def test_price_validation(sample_product, capsys):
    sample_product.price = -50
    captured = capsys.readouterr()
    assert "Цена не должна быть нулевая или отрицательная" in captured.out
    assert sample_product.price == 100.0

    sample_product.price = 0
    captured = capsys.readouterr()
    assert "Цена не должна быть нулевая или отрицательная" in captured.out
    assert sample_product.price == 100.0


@patch('builtins.input', return_value='y')
def test_price_decrease_confirmation(mock_input, sample_product):
    sample_product._Product__price = 80.0
    sample_product.price = 70.0
    assert sample_product.price == 70.0


@patch('builtins.input', return_value='n')
def test_price_decrease_cancel(mock_input, sample_product, capsys):
    sample_product._Product__price = 80.0
    sample_product.price = 70.0
    captured = capsys.readouterr()
    assert "Отмена изменения цены." in captured.out
    assert sample_product.price == 80.0


def test_new_product_duplicate():
    existing_product = Product("Duplicate", "Desc", 50.0, 10)
    new_data = {"name": "Duplicate", "price": 60.0, "quantity": 5}
    result = Product.new_product(new_data, [existing_product])
    assert result.quantity == 15
    assert result.price == 60.0


def test_new_product_no_duplicate():
    new_data = {"name": "New", "price": 100.0, "quantity": 5}
    result = Product.new_product(new_data)
    assert result.name == "New"
    assert result.price == 100.0


def test_load_categories(sample_products_json):
    categories = load_categories_from_json(str(sample_products_json))
    assert len(categories) == 1
    assert categories[0].name == "Test Category"
    assert "Test Product, 100.0 руб. Остаток: 5 шт." in categories[0].products
    assert Category.category_count == 1
    assert Category.product_count == 1


def test_load_categories_file_not_found(tmp_path):
    bad_path = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError) as exc_info:
        load_categories_from_json(str(bad_path))
    assert str(bad_path) in str(exc_info.value)


def test_load_categories_invalid_json(tmp_path):
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{invalid}")
    with pytest.raises(json.JSONDecodeError):
        load_categories_from_json(str(invalid_json))


def test_empty_category():
    category = Category("Empty", "Empty desc")
    assert category.products == ""
    assert Category.category_count == 1
    assert Category.product_count == 0