import json
import os
from pathlib import Path


class Product:
    def __init__(self, name: str, description: str, price: float, quantity: int):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity


class Category:
    category_count = 0
    product_count = 0

    def __init__(self, name: str, description: str, products: list[Product]):
        self.name = name
        self.description = description
        self.products = products
        Category.category_count += 1
        Category.product_count += len(products)


def load_categories_from_json(file_path: str) -> list[Category]:
    path = Path(file_path)
    if not path.exists():
        # Проверяем наличие файла в директории src/
        src_path = Path(__file__).parent / "products.json"
        if src_path.exists():
            path = src_path
        else:
            raise FileNotFoundError(
                f"Файл {file_path} не найден! Проверьте пути: {os.getcwd()}"
            )

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

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
    try:
        categories = load_categories_from_json("products.json")

        for category in categories:
            print(f"Категория: {category.name}")
            print(f"Описание: {category.description}")
            print(f"Товары ({len(category.products)}):")
            for product in category.products:
                print(
                    f"  - {product.name}: {product.price} руб. (остаток: {product.quantity})"
                )
            print()

        print(f"Всего категорий: {Category.category_count}")
        print(f"Всего товаров: {Category.product_count}")

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        print(
            "Убедитесь, что файл 'products.json' находится в той же папке, что и скрипт."
        )
    except json.JSONDecodeError as e:
        print(f"Ошибка в формате JSON: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
