import json
from pathlib import Path
from abc import ABC, abstractmethod


class ReprMixin:
    def __repr__(self):
        params = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({params})"

    def __init__(self, *args, **kwargs):
        print(
            f"Создан объект {self.__class__.__name__} с параметрами: {self.__repr__()}"
        )
        super().__init__(*args, **kwargs)


class ZeroQuantityError(Exception):
    """Исключение для товаров с нулевым количеством"""

    pass


class BaseProduct(ABC):
    def __init__(self, name, description, price, quantity):
        self.name = name
        self.description = description
        self._price = price
        self.quantity = quantity

    @abstractmethod
    def __str__(self):
        pass

    @property
    @abstractmethod
    def price(self):
        pass

    @price.setter
    @abstractmethod
    def price(self, new_price):
        pass


class Product(BaseProduct, ReprMixin):
    def __init__(self, name, description, price, quantity):
        if quantity <= 0:
            raise ValueError("Товар с нулевым количеством не может быть добавлен")
        super().__init__(name, description, price, quantity)

    def __str__(self):
        return f"{self.name}, {self.price} руб. Остаток: {self.quantity} шт."

    def __add__(self, other):
        if not isinstance(other, Product):
            raise TypeError("Можно складывать только объекты класса Product")
        if type(self) is not type(other):
            raise TypeError("Можно складывать только товары из одинаковых классов")
        return self.price * self.quantity + other.price * other.quantity

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, new_price):
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
        else:
            if new_price < self._price:
                confirmation = input("Цена понижается. Подтвердите изменение (y/n): ")
                if confirmation.lower() == "y":
                    self._price = new_price
                else:
                    print("Отмена изменения цены.")
            else:
                self._price = new_price

    @classmethod
    def new_product(cls, product_data, products=None):
        if products is None:
            products = []
        for product in products:
            if product.name == product_data["name"]:
                product.quantity += product_data["quantity"]
                product.price = product_data["price"]
                return product
        return cls(**product_data)


class Smartphone(Product):
    def __init__(
        self, name, description, price, quantity, efficiency, model, memory, color
    ):
        super().__init__(name, description, price, quantity)
        self.efficiency = efficiency
        self.model = model
        self.memory = memory
        self.color = color

    def __str__(self):
        return (
            f"{self.name} ({self.model}), {self.price} руб. Остаток: {self.quantity} шт. "
            f"Характеристики: {self.memory}GB, {self.color}, производительность: {self.efficiency}"
        )


class LawnGrass(Product):
    def __init__(
        self, name, description, price, quantity, country, germination_period, color
    ):
        super().__init__(name, description, price, quantity)
        self.country = country
        self.germination_period = germination_period
        self.color = color

    def __str__(self):
        return (
            f"{self.name}, {self.price} руб. Остаток: {self.quantity} шт. "
            f"Производитель: {self.country}, срок прорастания: {self.germination_period}, цвет: {self.color}"
        )


class Category:
    category_count = 0
    product_count = 0

    def __init__(self, name, description, products=None):
        self.name = name
        self.description = description
        self.__products = products if products is not None else []
        Category.category_count += 1
        Category.product_count += len(self.__products)

    def __str__(self):
        total_quantity = sum(product.quantity for product in self.__products)
        return f"{self.name}, количество продуктов: {total_quantity} шт."

    def add_product(self, product):
        try:
            if not isinstance(product, Product):
                raise TypeError(
                    "Можно добавлять только объекты класса Product или его наследников"
                )
            if product.quantity <= 0:
                raise ZeroQuantityError("Нельзя добавить товар с нулевым количеством")

            self.__products.append(product)
            Category.product_count += 1
            print(f"Товар {product.name} успешно добавлен")
        except (TypeError, ZeroQuantityError) as e:
            print(f"Ошибка: {e}")
        finally:
            print("Обработка добавления товара завершена")

    @property
    def products(self):
        return "\n".join(str(product) for product in self.__products)

    def average_price(self):
        try:
            total = sum(product.price for product in self.__products)
            return total / len(self.__products)
        except ZeroDivisionError:
            return 0

    def __iter__(self):
        return CategoryIterator(self.__products)


class CategoryIterator:
    def __init__(self, products):
        self.products = products
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.products):
            product = self.products[self.index]
            self.index += 1
            return product
        raise StopIteration


class Order:
    def __init__(self, product, quantity):
        if not isinstance(product, Product):
            raise TypeError("Заказ может содержать только объекты класса Product")
        if quantity <= 0:
            raise ZeroQuantityError("Нельзя создать заказ с нулевым количеством товара")
        self.product = product
        self.quantity = quantity
        self.total_price = product.price * quantity

    def __str__(self):
        return f"Заказ: {self.product.name}, {self.quantity} шт., Итого: {self.total_price} руб."


class BaseEntity(ABC):
    @abstractmethod
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def __str__(self):
        pass


class EnhancedCategory(BaseEntity):
    category_count = 0
    product_count = 0

    def __init__(self, name, description, products=None):
        super().__init__(name, description)
        self.__products = products if products is not None else []
        EnhancedCategory.category_count += 1
        EnhancedCategory.product_count += len(self.__products)

    def __str__(self):
        total_quantity = sum(product.quantity for product in self.__products)
        return f"{self.name}, количество продуктов: {total_quantity} шт."


def load_categories_from_json(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден")

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    categories = []
    for category_data in data:
        products = []
        for product_data in category_data["products"]:
            if "efficiency" in product_data:
                products.append(Smartphone(**product_data))
            elif "country" in product_data:
                products.append(LawnGrass(**product_data))
            else:
                products.append(Product(**product_data))
        categories.append(
            Category(category_data["name"], category_data["description"], products)
        )

    return categories


if __name__ == "__main__":
    try:
        categories = load_categories_from_json("products.json")
        for category in categories:
            print(f"Категория: {category.name}")
            print(f"Описание: {category.description}")
            print("Товары:")
            print(category.products)
            print(f"Средняя цена: {category.average_price()}")
            print()

        print(f"Всего категорий: {Category.category_count}")
        print(f"Всего товаров: {Category.product_count}")

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка в формате JSON: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
