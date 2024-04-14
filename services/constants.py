ENTER_PROMPT_TEMPLATE = "ENTER_PROMPT_TEMPLATE"
GOOD_ANSWER_PROMPT_TEMPLATE = "GOOD_ANSWER_PROMPT_TEMPLATE"
INVALID_ANSWERS = "INVALID_ANSWERS"


class Constants:
    PROMPT_TEMPLATES = {
        ENTER_PROMPT_TEMPLATE: """Ты бот-стилист. Запрос: "{user_prompt}". Если в запросе в кавычках перечислена
одежда, выведи следующее: {{"clothes": ["Одежда_1", "Одежда_2", ...], "style": стиль из запроса}},
Где по ключу clothes вся перечисленная одежда, а в style стиль одежды. Если в запрос не указана одежда, выведи BadClothes.""",
        GOOD_ANSWER_PROMPT_TEMPLATE: """Ты стилист, хорошо разбирающийся в одежде, стиле и подборе цвета. Запрос в виде словаря: "{chat_answer}". Если по ключу clothes не указаны 
цвета для одежды, то по ключу 'style' извлеки стиль и подбери цвета, которые будут гармонировать друг с другом, если они ещё не указаны. Составь 
случайные комбинации цвета и одежды, из тех, что указаны, и добавь в название одежды выбранный цвет. Не добавляй лишней одежды, только та, что в словаре. Верни 
измененный словарь и больше ничего не пиши.""",
    }

    INVALID_ANSWERS = ["NoClothes", "NoClothes.", "BadClothes", "BadClothes."]
