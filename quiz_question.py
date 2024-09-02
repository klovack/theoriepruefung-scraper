from typing import Optional, Literal

ResourceType = Literal["image", "video"]

class QuizQuestionResource:
    def __init__(self, url: str, type: ResourceType):
        self.url = url
        self.type = type

class QuizQuestion:
    def __init__(self, question: str, options: list[str], correct_options: list[int], score: int, sub_question: Optional[str] = None, resources: Optional[QuizQuestionResource] = None):
        self.question = question
        self.options = options
        self.correct_options = correct_options
        self.score = score
        self.resources = resources
        self.sub_question = sub_question
