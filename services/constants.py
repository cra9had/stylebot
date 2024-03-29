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
            """
                    Ты стилист, хорошо разбирающийся в одежде, стиле и подборе цвета. Запрос в виде словаря: "{chat_answer}". 
                    По ключу 'style' извлеки стиль и подбери цвета, которые будут гармонировать друг с другом. Составь случайные комбинации цвета
                    и одежды, из тех, что ты выбрал, и добавь в название одежды выбранный цвет. Верни измененный словарь и больше ничего не пиши.
            """
    }

    INVALID_ANSWERS = ["NoClothes", "NoClothes."]
