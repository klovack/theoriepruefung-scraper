from playwright.async_api import (
    async_playwright,
    Playwright,
    Page,
    Locator,
    BrowserContext,
)
from typing import Optional
from quiz_question import QuizQuestion, QuizQuestionResource, ResourceType
import asyncio
import jsonpickle
import requests
import config
from os import makedirs, path

jsonpickle.set_preferred_backend("json")
jsonpickle.set_encoder_options("json", ensure_ascii=False)

folder_prefix = config.scrape_folder_prefix
no_category_name = "no-category"
no_sub_category_name = "no-sub-category"
all_categories: dict[str, dict[str, list[QuizQuestion]]] = {}


def get_file_name(
    category: str, sub_category: str, resource_src: str, resource_type: ResourceType
) -> str:
    return f'{folder_prefix}/{category}/{sub_category}/{resource_type}/{resource_src.split("/")[-1].split("#")[0]}'


async def get_list_of_questions(
    page: Page,
    context: BrowserContext,
    questions_list: list[QuizQuestion],
    category_name: str,
    sub_category_name: str,
):
    print(f"get_list_of_questions in {category_name} -> {sub_category_name}")
    questions: list[Locator] = await page.locator("ul.teaser-list-questions li").all()

    for i, question in enumerate(questions):
        await save_question(
            context, questions_list, category_name, sub_category_name, question
        )


async def save_question(
    context, questions_list, category_name, sub_category_name, question
):
    question_a_tag: Locator = question.locator("a")
    question_link = await question_a_tag.get_attribute("href")
    question_text = await question_a_tag.inner_text()
    question_text = question_text.split("\n")[1]

    print(f'save_question in {category_name} -> {sub_category_name}: "{question_text}"')

    question_page = await context.new_page()

    await question_page.goto(question_link)
    await question_page.wait_for_timeout(1000)

    body_locator: Locator = question_page.locator("div.body")

    sub_question = await body_locator.locator("div.subtitle").inner_text()
    points = int((await body_locator.locator("div.points").inner_text()).split(" ")[1])
    question_locator: Locator = question_page.locator("div.question")

    resource_src: Optional[str] = None
    resource_type: Optional[ResourceType] = None

    has_video = await question_locator.locator("video").count() > 0
    if has_video:
        resource_src = await question_locator.locator("video").get_attribute("src")
        resource_type = "video"

    has_image = await question_locator.locator("div.image img").count() > 0
    if has_image:
        resource_src = await question_locator.locator("div.image img").get_attribute(
            "src"
        )
        resource_type = "image"

    if (resource_src and resource_type) is not None:
        content = requests.get(resource_src).content
        file_name = get_file_name(
            category_name, sub_category_name, resource_src, resource_type
        )

        if not path.exists(file_name):
            makedirs(path.dirname(file_name), exist_ok=True)
            with open(f"{file_name}", "wb") as f:
                f.write(content)

    question_options: list[Locator] = await question_page.locator(
        "div.body > ul.options li"
    ).all()
    options: list[str] = []
    correct_options: list[int] = []
    for i, question_option in enumerate(question_options):
        option_text: str = await question_option.locator("span.option-box").inner_text()
        options.append(option_text)
        if await question_option.get_attribute("data-result") == "true":
            correct_options.append(i)
    questions_list.append(
        QuizQuestion(
            question_text,
            options,
            correct_options,
            points,
            sub_question,
            (
                QuizQuestionResource(
                    get_file_name(
                        category_name, sub_category_name, resource_src, resource_type
                    ),
                    resource_type,
                )
                if resource_src
                else None
            ),
        )
    )

    await question_page.close()


async def get_subcategories(
    page: Page,
    context: BrowserContext,
    sub_categories_dict: dict[str, list[QuizQuestion]],
    category_name: str,
):
    print(f"get_subcategories in {category_name}")
    sub_categories: list[Locator] = await page.locator(
        "ul.teaser-list-chapters li"
    ).all()

    for sub_category in sub_categories:
        sub_category_a_tag: Locator = sub_category.locator("a")
        sub_category_name = await sub_category_a_tag.inner_text()

        if sub_category_name not in sub_categories_dict:
            sub_categories_dict[sub_category_name] = []

        sub_category_link = await sub_category_a_tag.get_attribute("href")
        sub_category_page = await context.new_page()
        await sub_category_page.goto(sub_category_link)
        await sub_category_page.wait_for_timeout(1000)
        await get_list_of_questions(
            sub_category_page,
            context,
            sub_categories_dict[sub_category_name],
            category_name,
            sub_category_name,
        )
        json_dump = jsonpickle.encode(sub_categories_dict[sub_category_name], indent=2)

        # Save Subcategory data to file
        file_name = f"{folder_prefix}/{category_name}/{sub_category_name}/data.json"
        makedirs(path.dirname(file_name), exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as f:
            print(json_dump, file=f)

        await sub_category_page.close()

    if len(sub_categories) == 0:
        if no_sub_category_name not in sub_categories_dict:
            sub_categories_dict[no_sub_category_name] = []

        await get_list_of_questions(
            page,
            context,
            sub_categories_dict[no_sub_category_name],
            category_name,
            no_sub_category_name,
        )


async def scrape_autovio(page: Page, context: BrowserContext):
    await page.get_by_text("Einverstanden").click()
    categories: list[Locator] = await page.locator("ul.teaser-list-chapters li").all()

    for index, category in enumerate(categories):
        if index < config.start_from:
            continue
        if config.end_at is not None and index >= config.end_at:
            break
        category_a_tag: Locator = category.locator("a")
        category_text = await category_a_tag.inner_text()

        if config.use_existing:
            existing_file_name = f"{folder_prefix}/{category_text}/data.json"
            if path.exists(existing_file_name):
                with open(existing_file_name, "r", encoding="utf-8") as f:
                    all_categories[category_text] = jsonpickle.decode(f.read())

        if category_text not in all_categories:
            all_categories[category_text] = {}

        category_link = await category_a_tag.get_attribute("href")
        category_page = await context.new_page()
        print(f"Scraping {category_text}")
        await category_page.goto(category_link)
        await category_page.wait_for_timeout(1000)
        await get_subcategories(
            category_page, context, all_categories[category_text], category_text
        )

        json_dump = jsonpickle.encode(all_categories[category_text], indent=2)

        # Save each Category data to file
        file_name = f"{folder_prefix}/{category_text}/data.json"
        makedirs(path.dirname(file_name), exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as f:
            print(json_dump, file=f)

        await category_page.close()


async def run(p: Playwright):
    browser = await p.chromium.launch(headless=config.headless)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://autovio.de/fuer-fahrschueler/fuehrerschein-theorie-lernen")
    await page.wait_for_timeout(1000)

    await scrape_autovio(page, context)

    await page.close()
    await browser.close()


async def main():
    async with async_playwright() as p:
        await run(p)


if __name__ == "__main__":
    asyncio.run(main())

    if config.merge_all:
        json_dump = jsonpickle.encode(all_categories, indent=2)
        makedirs(path.dirname(f"{folder_prefix}"), exist_ok=True)
        with open(f"{folder_prefix}/all-data.json", "w", encoding="utf-8") as f:
            print(json_dump, file=f)
