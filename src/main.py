import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class Product:
    def __init__(self, name: str, description: str, price: float, quantity: int):
        self.name = name
        self.description = description
        self.__price = price  # Приватный атрибут
        self.quantity = quantity

    @classmethod
    def new_product(
        cls, product_data: Dict[str, Any], products: Optional[List["Product"]] = None
    ) -> "Product":
        """Создает новый продукт, обрабатывая дубликаты"""
        name = product_data["name"]
        price = product_data["price"]
        quantity = product_data["quantity"]
        description = product_data.get("description", "")

        if products:
            for prod in products:
                if prod.name == name:
                    prod.quantity += quantity
                    if prod.price < price:
                        prod.price = price
                    return prod

        return cls(name, description, price, quantity)

    @property
    def price(self) -> float:
        """Возвращает цену продукта"""
        return self.__price

    @price.setter
    def price(self, new_price: float) -> None:
        """Устанавливает цену с проверками"""
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return

        if hasattr(self, "_Product__price") and new_price < self.__price:
            confirm = input(
                f"Цена снижается с {self.__price} до {new_price}. Подтвердите (y/n): "
            )
            if confirm.lower() != "y":
                print("Отмена изменения цены.")
                return

        self.__price = new_price


class Category:
    category_count: int = 0
    product_count: int = 0

    def __init__(
        self, name: str, description: str, products: Optional[List[Product]] = None
    ):
        self.name = name
        self.description = description
        self.__products = products if products is not None else []
        Category.category_count += 1
        Category.product_count += len(self.__products)

    def add_product(self, product: Product) -> None:
        """Добавляет продукт в категорию"""
        if not isinstance(product, Product):
            raise TypeError(
                "Можно добавлять только объекты класса Product или его наследников"
            )
        self.__products.append(product)
        Category.product_count += 1

    @property
    def products(self) -> str:
        """Возвращает строку с информацией о продуктах"""
        return "\n".join(
            f"{p.name}, {p.price} руб. Остаток: {p.quantity} шт."
            for p in self.__products
        )


def load_categories_from_json(file_path: str) -> List[Category]:
    """Загружает категории из JSON файла"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден!")

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Ошибка в формате JSON файла {file_path}", e.doc, e.pos
        )

    categories = []
    for category_data in data:
        products = [
            Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                quantity=product_data["quantity"],
            )
            for product_data in category_data["products"]
        ]
        categories.append(
            Category(
                name=category_data["name"],
                description=category_data["description"],
                products=products,
            )
        )
    return categories


if __name__ == "__main__":
    # Пример использования
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
