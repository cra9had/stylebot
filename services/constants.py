ENTER_PROMPT_TEMPLATE = "ENTER_PROMPT_TEMPLATE"
GOOD_ANSWER_PROMPT_TEMPLATE = "GOOD_ANSWER_PROMPT_TEMPLATE"
INVALID_ANSWERS = "INVALID_ANSWERS"


class Constants:
    PROMPT_TEMPLATES = {
        ENTER_PROMPT_TEMPLATE:
            """
                    Ты бот-стилист. Запрос: "{user_prompt}". Если в запросе в кавычках есть задача подобрать образ и перечислена
                    одежда и стиль, выведи следующее: {{clothes: ["Одежда_1", "Одежда_2", ...], "style": стиль из запроса}}.
                    Если в запросе нет стиля, сформируй его сам. Если запрос не выглядит как просьба подобрать образ в каком-то стиле, выведи BadClothes.
                """,

        GOOD_ANSWER_PROMPT_TEMPLATE:
            "Грамотный стилист, сочетающий одежду, стиль и цвет. Помогите выбрать одежду из {gpt_answer}. Извлеките стиль и одежду по ключу style, подберите сочетающиеся цвета для каждой одежды, сгенерируйте случайные комбинации одежды и цвета. Если цвета нет в названии одежды, добавьте его. Представьте комбинации одежды с цветом поочередно, разделяя запятыми. Без нумерации, приамбул и точки в конце. Выберите лучшую комбинацию."
    }

    INVALID_ANSWERS = ["NoClothes", "NoClothes."]