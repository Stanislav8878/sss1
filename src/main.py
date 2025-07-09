import json
from pathlib import Path


class Product:
    def __init__(self, name, description, price, quantity):
        self.name = name
        self.description = description
        self.__price = price
        self.quantity = quantity

    def __str__(self):
        return f"{self.name}, {self.price} руб. Остаток: {self.quantity} шт."

    def __add__(self, other):
        if not isinstance(other, Product):
            raise TypeError("Можно складывать только объекты класса Product")
        if type(self) is not type(other):  # Исправлено на is not
            raise TypeError("Можно складывать только товары из одинаковых классов")
        return self.price * self.quantity + other.price * other.quantity

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, new_price):
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
        else:
            if new_price < self.__price:
                confirmation = input("Цена понижается. Подтвердите изменение (y/n): ")
                if confirmation.lower() == "y":
                    self.__price = new_price
                else:
                    print("Отмена изменения цены.")
            else:
                self.__price = new_price

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
        if not isinstance(product, Product):
            raise TypeError(
                "Можно добавлять только объекты класса Product или его наследников"
            )
        self.__products.append(product)
        Category.product_count += 1

    @property
    def products(self):
        return "\n".join(str(product) for product in self.__products)

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
            if "efficiency" in product_data:  # Это смартфон
                products.append(Smartphone(**product_data))
            elif "country" in product_data:  # Это газонная трава
                products.append(LawnGrass(**product_data))
            else:  # Обычный продукт
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
            print()

        print(f"Всего категорий: {Category.category_count}")
        print(f"Всего товаров: {Category.product_count}")

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка в формате JSON: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
