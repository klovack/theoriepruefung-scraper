from typing import Literal

scrape_folder_prefix = 'scraped'
translation_folder_prefix = 'translated'

# start_from inclusive
start_from = 7
# end_at exclusive
end_at = None

merge_all = False
headless = True

use_existing = True

categories_to_translate: dict[
    str,
    dict[str, list[int | str] | Literal["all", "no-image", "no-video", "no-resource"]],
] = {
    "Gefahrenlehre": {
        "Grundformen des Verkehrsverhaltens": "no-resource",
        "Überholen": "no-resource",
        "Verhalten gegenüber Fußgängern": "no-resource",
        # 'Autobahn': [0]
    }
}
