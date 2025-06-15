from typing import Literal
from pydantic import BaseModel

class TranslationTarget(BaseModel):
    folder_prefix: str
    language_code: Literal["en-US", "id"]
    
class TranslationTargets(BaseModel):
    english: TranslationTarget
    indonesian: TranslationTarget
    
translation_targets = TranslationTargets(
    english=TranslationTarget(folder_prefix="translated/en", language_code="en-US"),
    indonesian=TranslationTarget(folder_prefix="translated/id", language_code="id"),
)

scrape_folder_prefix = 'scraped'
translation_folder_prefix = translation_targets.indonesian.folder_prefix
target_language = translation_targets.indonesian.language_code

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
    # "Gefahrenlehre": {
    #     "Grundformen des Verkehrsverhaltens": "no-resource",
    #     "Überholen": "all",
    #     # "Verhalten gegenüber Fußgängern": "all",
    #     "Autobahn": "all",
    # },
    # "Verhalten im Straßenverkehr": {
    #     "Halten und Parken": "all",
    #     "Blaues Blinklicht und gelbes Blinklicht": [5],
    #     "Besondere Verkehrslagen": "all",
    #     "Straßenbenutzung": "all",
    # },
    # "Verkehrszeichen": {
    #     "Vorschriftzeichen": "all",
    # },
    "Verhalten im Straßenverkehr": {
        "Abstand": "all",
    },
}
