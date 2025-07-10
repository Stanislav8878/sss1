import pytest
from pathlib import Path
from main import (
    Product, Category, Smartphone, LawnGrass,
    load_categories_from_json, CategoryIterator,
    BaseProduct, ReprMixin, Order, BaseEntity, EnhancedCategory
)
from unittest.mock import patch
import json
from abc import ABC


@pytest.fixture(autouse=True)
def reset_counters():
    """Сбрасывает счетчики перед каждым тестом"""
    Category.category_count = 0
    Category.product_count = 0
    EnhancedCategory.category_count = 0
    EnhancedCategory.product_count = 0
    yield


@pytest.fixture
def sample_product():
    with patch('builtins.print'):
        return Product("Test", "Desc", 100.0, 10)


@pytest.fixture
def sample_smartphone():
    with patch('builtins.print'):
        return Smartphone("Smart", "Desc", 500.0, 5, "High", "X1", 128, "Black")


@pytest.fixture
def sample_lawn_grass():
    with patch('builtins.print'):
        return LawnGrass("Grass", "Desc", 50.0, 20, "Russia", "2 weeks", "Green")


@pytest.fixture
def sample_category(sample_product):
    return Category("Test Cat", "Desc", [sample_product])


def test_base_product_abc():
    """Тест, что BaseProduct является абстрактным классом"""
    with pytest.raises(TypeError):
        BaseProduct("Test", "Desc", 100, 10)
    assert issubclass(BaseProduct, ABC)


def test_repr_mixin():
    """Тест функциональности миксина ReprMixin"""
    with patch('builtins.print'):
        product = Product("Test", "Desc", 100.0, 10)
    expected_repr = "Product(name='Test', description='Desc', _price=100.0, quantity=10)"
    assert repr(product) == expected_repr


def test_order_creation(sample_product):
    """Тест создания заказа"""
    order = Order(sample_product, 3)
    assert order.quantity == 3
    assert order.total_price == 300.0
    assert str(order) == "Заказ: Test, 3 шт., Итого: 300.0 руб."


def test_order_invalid_product():
    """Тест обработки неверного типа продукта в заказе"""
    with pytest.raises(TypeError) as exc_info:
        Order("invalid", 1)
    assert "Заказ может содержать только объекты класса Product" in str(exc_info.value)


def test_base_entity_abc():
    """Тест, что BaseEntity является абстрактным классом"""
    with pytest.raises(TypeError):
        BaseEntity("Test", "Desc")
    assert issubclass(BaseEntity, ABC)


def test_enhanced_category():
    """Тест функциональности EnhancedCategory"""
    cat = EnhancedCategory("Test", "Desc")
    assert str(cat) == "Test, количество продуктов: 0 шт."
    assert EnhancedCategory.category_count == 1
    assert EnhancedCategory.product_count == 0


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
    with patch('builtins.print'):
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
    sample_product._price = 80.0
    sample_product.price = 70.0
    assert sample_product.price == 70.0


@patch('builtins.input', return_value='n')
def test_price_decrease_cancel(mock_input, sample_product, capsys):
    sample_product._price = 80.0
    sample_product.price = 70.0
    captured = capsys.readouterr()
    assert "Отмена изменения цены." in captured.out
    assert sample_product.price == 80.0


def test_new_product_duplicate():
    with patch('builtins.print'):
        existing_product = Product("Duplicate", "Desc", 50.0, 10)
    new_data = {
        "name": "Duplicate",
        "description": "New Desc",
        "price": 60.0,
        "quantity": 5
    }
    result = Product.new_product(new_data, [existing_product])
    assert result.quantity == 15
    assert result.price == 60.0


def test_new_product_no_duplicate():
    new_data = {
        "name": "New",
        "description": "New Desc",
        "price": 100.0,
        "quantity": 5
    }
    with patch('builtins.print'):
        result = Product.new_product(new_data)
    assert result.name == "New"
    assert result.price == 100.0


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


def test_product_str(sample_product):
    assert str(sample_product) == "Test, 100.0 руб. Остаток: 10 шт."


def test_category_str(sample_category):
    assert str(sample_category) == "Test Cat, количество продуктов: 10 шт."


def test_category_iterator(sample_category):
    products = list(sample_category)
    assert len(products) == 1
    assert products[0].name == "Test"


def test_category_iterator_empty():
    empty_category = Category("Empty", "Empty desc")
    products = list(empty_category)
    assert len(products) == 0


def test_category_iterator_class():
    with patch('builtins.print'):
        products = [Product("A", "Desc", 100, 5), Product("B", "Desc", 200, 3)]
    iterator = CategoryIterator(products)
    assert list(iterator) == products


def test_smartphone_init(sample_smartphone):
    assert sample_smartphone.name == "Smart"
    assert sample_smartphone.price == 500.0
    assert sample_smartphone.efficiency == "High"
    assert sample_smartphone.model == "X1"
    assert sample_smartphone.memory == 128
    assert sample_smartphone.color == "Black"


def test_lawn_grass_init(sample_lawn_grass):
    assert sample_lawn_grass.name == "Grass"
    assert sample_lawn_grass.price == 50.0
    assert sample_lawn_grass.country == "Russia"
    assert sample_lawn_grass.germination_period == "2 weeks"
    assert sample_lawn_grass.color == "Green"


def test_product_addition_same_type(sample_product):
    with patch('builtins.print'):
        product2 = Product("Test2", "Desc2", 50.0, 5)
    assert sample_product + product2 == 100.0 * 10 + 50.0 * 5


def test_product_addition_different_types(sample_product, sample_smartphone):
    with pytest.raises(TypeError) as exc_info:
        sample_product + sample_smartphone
    assert "Можно складывать только товары из одинаковых классов" in str(exc_info.value)


def test_smartphone_addition(sample_smartphone):
    with patch('builtins.print'):
        smartphone2 = Smartphone("Smart2", "Desc", 600.0, 3, "High", "X2", 256, "White")
    assert sample_smartphone + smartphone2 == 500.0 * 5 + 600.0 * 3


def test_category_add_smartphone(sample_category, sample_smartphone):
    sample_category.add_product(sample_smartphone)
    assert "Smart (X1)" in sample_category.products
    assert Category.product_count == 2


def test_category_add_lawn_grass(sample_category, sample_lawn_grass):
    sample_category.add_product(sample_lawn_grass)
    assert "Grass" in sample_category.products
    assert Category.product_count == 2


def test_category_add_invalid_type(sample_category):
    with pytest.raises(TypeError) as exc_info:
        sample_category.add_product("invalid product")
    assert "Можно добавлять только объекты класса Product или его наследников" in str(exc_info.value)
    assert Category.product_count == 1


def test_load_categories_with_new_products(tmp_path):
    data = [{
        "name": "Test Category",
        "description": "Test Desc",
        "products": [
            {
                "name": "Smartphone",
                "description": "Test",
                "price": 50000,
                "quantity": 5,
                "efficiency": "High",
                "model": "X100",
                "memory": 256,
                "color": "Black"
            },
            {
                "name": "Grass",
                "description": "Test",
                "price": 1000,
                "quantity": 50,
                "country": "Russia",
                "germination_period": "2 weeks",
                "color": "Green"
            }
        ]
    }]
    file_path = tmp_path / "products.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    categories = load_categories_from_json(str(file_path))
    assert len(categories) == 1
    assert isinstance(categories[0]._Category__products[0], Smartphone)
    assert isinstance(categories[0]._Category__products[1], LawnGrass)
    assert Category.category_count == 1
    assert Category.product_count == 2