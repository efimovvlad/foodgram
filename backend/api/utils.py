from datetime import datetime


def generate_txt(ingredients):
    """Генерация текстового файла из списка продуктов."""

    today = datetime.today()
    shopping_list = (
        f'Список покупок от {today:%Y-%m-%d}\n\n'
    )
    shopping_list += '\n'.join([
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]}) - '
        f'{ingredient["amount"]}'
        for ingredient in ingredients
    ])
    return shopping_list
