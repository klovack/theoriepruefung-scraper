from dotenv import load_dotenv
import deepl
import os
import config
import jsonpickle
from pathlib import Path
from typing import Literal
from quiz_question import QuizQuestion

load_dotenv()
jsonpickle.set_preferred_backend("json")
jsonpickle.set_encoder_options("json", ensure_ascii=False)


class TranslationService:
    def __init__(self):
        self.translator = deepl.Translator(auth_key=os.getenv("DEEPL_API_KEY"))

    def translate(
        self,
        text: list[str],
        target_lang: str,
        context: str = "Führerschein Theorie lernen.",
    ):
        return self.translator.translate_text(
            text, source_lang="DE", target_lang=target_lang, context=context
        )


def get_questions_from_disk(
    category: str, subcategory: str, questions: list[int | str] | Literal["all"] = "all"
):
    print(f"Reading questions from disk: {category} -> {subcategory}")

    if not Path(f"{config.scrape_folder_prefix}/{category}/{subcategory}").exists():
        return None

    # read data.json from the subcategory folder
    with open(
        f"{config.scrape_folder_prefix}/{category}/{subcategory}/data.json",
        "r",
        encoding="utf-8",
    ) as f:
        questions_data: list[QuizQuestion] = jsonpickle.decode(f.read())

    if questions == "all":
        return questions_data

    if questions == "no-image":
        questions_data = [
            q
            for q in questions_data
            if q.resource is not None and q.resource.type != "image"
        ]
        return questions_data

    if questions == "no-video":
        questions_data = [
            q
            for q in questions_data
            if q.resource is not None and q.resource.type != "video"
        ]
        return questions_data

    if questions == "no-resource":
        questions_data = [q for q in questions_data if q.resource is None]
        return questions_data

    # if element in the list is a string 1-5, transform it to an integer 1, 2, 3, 4, 5
    iterate_questions = []
    for i, q in enumerate(questions):
        if isinstance(q, str):
            # split the string by '-' and convert the elements to integers
            # and fill the array with the first until the end element
            iterate_questions.extend(
                list(range(int(q.split("-")[0]), int(q.split("-")[1]) + 1))
            )
            questions.pop(i)
    questions.extend(iterate_questions)

    # filter questions_data by the questions list
    questions_data = [q for i, q in enumerate(questions_data) if i in questions]

    return questions_data


def get_translated_question(
    question: QuizQuestion, translation_service: TranslationService
):
    print("Translating question: ", question.question)
    text = [question.question, *question.options]
    if question.sub_question is not None and len(question.sub_question) > 0:
        print(f"append sub question, {question.sub_question}")
        text.append(question.sub_question)

    translated_question_texts = translation_service.translate(text, "ID")
    translated_options = [
        to.text
        for to in translated_question_texts[
            1 : (
                -1
                if question.sub_question is not None and len(question.sub_question) > 0
                else None
            )
        ]
    ]
    translated_sub_question = (
        translated_question_texts[-1].text
        if question.sub_question is not None and len(question.sub_question) > 0
        else None
    )
    print(f"Translating: {question.question} -> {translated_question_texts[0].text}")

    translated_question = QuizQuestion(
        translated_question_texts[0].text,
        translated_options,
        question.correct_options,
        int(question.score),
        translated_sub_question,
        question.resource,
    )

    return translated_question


def translate_questions():
    print("Translating...")

    translation_service = TranslationService()

    categories_to_translate = config.categories_to_translate
    all_translated_questions: dict[str, dict[str, list[QuizQuestion]]] = {}

    for category, subcategories in categories_to_translate.items():
        if category not in all_translated_questions:
            all_translated_questions[category] = {}
        for subcategory, questions in subcategories.items():
            if subcategory not in all_translated_questions[category]:
                all_translated_questions[category][subcategory] = []
            list_of_questions = get_questions_from_disk(
                category, subcategory, questions
            )

            if list_of_questions is None:
                print(
                    "No questions found for category: ",
                    category,
                    " and subcategory: ",
                    subcategory,
                )
                continue

            print(
                f"Retrieved {len(list_of_questions)} questions for {category} -> {subcategory}"
            )

            for question in list_of_questions:
                translated_question = get_translated_question(
                    question, translation_service
                )
                all_translated_questions[category][subcategory].append(
                    translated_question
                )

            save_sub_category_to_file(all_translated_questions, category, subcategory)

        save_category_to_file(all_translated_questions, category)

    if config.merge_all:
        all_translated_questions_file_name = (
            f"{config.translation_folder_prefix}/data.json"
        )
        rename_old_file(all_translated_questions_file_name)
        with open(all_translated_questions_file_name, "w", encoding="utf-8") as f:
            f.write(jsonpickle.encode(all_translated_questions, indent=2))

    print("Translation complete!")


def rename_old_file(file_name):
    # if the file already exists, rename it to old.<filename>
    if Path(file_name).exists():
        os.renames(file_name, f"{file_name}.old")


def save_category_to_file(all_translated_questions, category):
    category_file_name = f"{config.translation_folder_prefix}/{category}/data.json"
    rename_old_file(category_file_name)

    Path(os.path.dirname(category_file_name)).mkdir(parents=True, exist_ok=True)
    with open(category_file_name, "w", encoding="utf-8") as f:
        f.write(jsonpickle.encode(all_translated_questions[category], indent=2))


def save_sub_category_to_file(all_translated_questions, category, subcategory):
    sub_category_file_name = (
        f"{config.translation_folder_prefix}/{category}/{subcategory}/data.json"
    )

    # if the file already exists, rename it to old.<filename>
    rename_old_file(sub_category_file_name)

    Path(os.path.dirname(sub_category_file_name)).mkdir(parents=True, exist_ok=True)

    with open(sub_category_file_name, "w", encoding="utf-8") as f:
        f.write(
            jsonpickle.encode(all_translated_questions[category][subcategory], indent=2)
        )


if __name__ == "__main__":
    translate_questions()
