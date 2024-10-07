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

    # current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    # recipes_list = '\n'.join(
    #     [f'{index}. {recipe}' for index, recipe in enumerate(recipes, start=1)]
    # )
    # ingredients_list = '\n'.join(
    #     [
    #         f'{index}. {ingredient["name"].capitalize()}: '
    #         f'{ingredient["amount"]} {ingredient["measurement"]}'
    #         for index, ingredient in enumerate(ingredients, start=1)
    #     ]
    # )
    # shopping_list = (
    #     f'Список покупок от {current_date}\n\n'
    #     'Рецепты:\n'
    #     f'{recipes_list}\n\n'
    #     'Продукты:\n'
    #     f'{ingredients_list}'
    # )

    # return shopping_list

    # return '\n'.join(
    #     [
    #         f'Список покупок от {current_date}\n',
    #         'Рецепты:',
    #         *[f'{index}. {recipe}' for index, recipe in enumerate(
    #             recipes, start=1
    #         )],
    #         '\nПродукты:',
    #         *[
    #             f'{index}. {ingredient["name"].capitalize()}: '
    #             f'{ingredient["amount"]} {ingredient["measurement"]}'
    #             for index, ingredient in enumerate(ingredients, start=1)
    #         ]
    #     ]
    # )
