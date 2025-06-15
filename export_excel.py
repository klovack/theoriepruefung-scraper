import json
import os
import shutil
from typing import Literal
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.drawing.image import Image
from openpyxl.cell.cell import Cell
from fire import Fire


def process_data_item(item):
    PY_OBJECT = "py/object"
    if PY_OBJECT in item:
        del item[PY_OBJECT]
    if "resource" in item and item["resource"] is not None:
        if PY_OBJECT in item["resource"]:
            del item["resource"][PY_OBJECT]

        # Flatten the resource details into the main dictionary
        for key in item["resource"]:
            item["resource_" + key] = item["resource"][key]
    del item["resource"]  # Remove the nested dictionary

    # Handle the 'options' list
    if "options" in item and item["options"] is not None:
        for idx, option in enumerate(item["options"]):
            item[f"option {idx}"] = option
        del item["options"]  # Remove the original options list
    return item


def handle_resources(data, sheet: Worksheet, excel_dir: str):
    sheet["A1"].value = "resource"
    sheet["A1"].alignment = Alignment(horizontal="center", vertical="center")
    sheet["A1"].font = sheet["A1"].font.copy(bold=True)

    for index, item in enumerate(
        data, start=2
    ):  # Start from row 2, assuming headers are in row 1
        if (
            "resource_url" in item
            and "resource_type" in item
            and item["resource_url"] is not None
            and os.path.exists(item["resource_url"])
        ):
            if item["resource_type"] == "image":

                img_path = item["resource_url"]

                try:
                    img = Image(img_path)
                    img.width = img.width * 0.5  # Adjust width as needed
                    img.height = img.height * 0.5  # Adjust height as needed
                    img.anchor = f"A{index}"  # Adjust cell as needed
                    sheet.row_dimensions[index].height = img.height - img.height / 5
                    sheet.column_dimensions["A"].width = img.width / 8
                    sheet.column_dimensions["A"].alignment = Alignment(
                        horizontal="left", vertical="top"
                    )
                    
                    sheet.add_image(img, f"A{index}")
                    # Set the height of the row where the image is inserted
                    print(f"Image successfully added at {index} on '{sheet.title}'")
                except Exception as e:
                    print(f"Error adding image: {e}")
                    
            elif item["resource_type"] == "video":
                video_path = os.path.join(
                    os.path.basename(
                        os.path.dirname(item["resource_url"])
                    ), 
                    os.path.basename(item["resource_url"])
                )

                # Add a hyperlink to the video file
                sheet[f"A{index}"].hyperlink = video_path
                sheet[f"A{index}"].value = "Video Link"
                sheet[f"A{index}"].alignment = Alignment(
                    horizontal="center", vertical="center"
                )
                
                video_location = os.path.join(excel_dir, video_path)
                os.makedirs(
                    os.path.dirname(video_location), exist_ok=True
                )
                shutil.copy(os.path.abspath(item["resource_url"]), video_location)
                print(f"Video link added at {index} on '{sheet.title}'")


def json_to_excel_with_resources(json_file_path: str, excel_file_path: str, sheet_name: str):
    # Load JSON data
    with open(json_file_path, "r") as file:
        data = json.load(file)

    # Filter out unnecessary keys and prepare data for DataFrame
    processed_data = [process_data_item(item) for item in data]

    # Convert to DataFrame
    df = pd.DataFrame(processed_data)

    # Make sure the directory exists
    os.path.exists(os.path.dirname(excel_file_path)) or os.makedirs(
        os.path.dirname(excel_file_path), exist_ok=True
    )

    if os.path.exists(excel_file_path):
        mode = "a"
    else:
        mode = "w"

    # Create Excel file with pandas and save
    with pd.ExcelWriter(
        excel_file_path,
        engine="openpyxl",
        mode=mode,
        if_sheet_exists="replace" if mode == "a" else None,
    ) as writer:
        df.to_excel(
            writer,
            index=False,
            engine="openpyxl",
            startcol=1,
            sheet_name=sheet_name,
        )

    # Now handle resources using openpyxl
    workbook = load_workbook(excel_file_path)
    sheet: Worksheet = workbook[sheet_name]

    # Set text wrapping for all cells and find max length in each column
    adjust_cell_width(sheet)

    # Handle resources
    handle_resources(data, sheet, os.path.dirname(excel_file_path))

    # Save the workbook with the images
    workbook.save(excel_file_path)


def adjust_cell_width(sheet):
    column_widths = {}
    for row in sheet.iter_rows():
        for cell in row:
            # Set wrap text style
            adjust_cell_style(column_widths, cell)

    # Set the column widths (a simple character width approximation)
    for col, width in column_widths.items():
        sheet.column_dimensions[col].width = (
            width  # Adjust multiplication factor as needed
        )


def adjust_cell_style(column_widths, cell: Cell):
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Calculate column width
    if cell.value:
        length = len(str(cell.value))
        if cell.column_letter in column_widths:
            if length > column_widths[cell.column_letter]:
                column_widths[cell.column_letter] = min(length, 80)
        else:
            column_widths[cell.column_letter] = min(length, 80)


# Example usage
# json_to_excel_with_resources(
#     "scraped/Vorfahrt, Vorrang/no-sub-category/data.json",
#     "excel/Vorfahrt, Vorrang.xlsx",
#     "Deutsch",
# )

# json_to_excel_with_resources(
#     "translated/id/Vorfahrt, Vorrang/no-sub-category/data.json",
#     "excel/Vorfahrt, Vorrang.xlsx",
#     "Bahasa Indonesia",
# )

# json_to_excel_with_resources(
#     "translated/id/Vorfahrt, Vorrang/no-sub-category/data.json",
#     "excel/Vorfahrt, Vorrang.xlsx",
#     "English",
# )

languages_names = {
    "de": "Deutsch",
    "en": "English",
    "id": "Bahasa Indonesia",
}


def export_categories_to_excel(
    files: list[str],
    languages: list[Literal["de", "en", "id"]] = ["de", "en", "id"],
    output_files: list[str] = None,
    folder_prefixes: dict[str, str] = {
        "de": "scraped",
        "en": "translated/en",
        "id": "translated/id",
    },
):
    """
    Export categories from JSON files to Excel files.
    
    :param languages: List of languages to export.
    :param files: List of category names in which the data.json file is located (e.g., ["Vorfahrt, Vorrang/no-sub-category", "Gefahrenlehre/Überholen"]).
    :param output_files: List of output Excel file paths (optional, when left empty it will try to mimic the category name in files).
    :param folder_prefixes: Dictionary mapping languages to their respective folder prefixes.
    :raises ValueError: If no languages or files are specified, or if an unsupported language is provided.
    """
    if languages is None or len(languages) == 0:
        raise ValueError("At least one language must be specified.")
    if files is None or len(files) == 0:
        raise ValueError("At least one category must be specified.")

    if output_files is None or len(output_files) == 0:
        print("No output file specified, using default: excel/<file>.xlsx")
        output_files = [
            f"excel/{file}.xlsx" for file in files
        ]
    
    for language in languages:
        if language not in folder_prefixes:
            raise ValueError(f"Unsupported language: {language}")
        
        for index, file in enumerate(files):
            folder_prefix = folder_prefixes[language]
            json_file_path = f"{folder_prefix}/{file}/data.json"
            excel_file_path = output_files[index] if len(output_files) > index else f"excel/translated_categories_{index}.xlsx"
            sheet_name = languages_names.get(language, "Unknown Language")
            print(f"Processing {json_file_path} to {excel_file_path} in {sheet_name} for {language}")
            json_to_excel_with_resources(
                json_file_path, excel_file_path, sheet_name
            )


if __name__ == "__main__":
    Fire(export_categories_to_excel)
