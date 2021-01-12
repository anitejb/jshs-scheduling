class Student:
    def __init__(
        self,
        student_id,
        is_paper,
        is_poster,
        category,
        poster_pdf,
        full_paper_pdf,
    ):
        self.student_id = student_id  # int
        self.is_paper = is_paper  # bool
        self.is_poster = is_poster  # bool
        self.category = category  # int

        self.paper_judges = []  # list of Judge
        self.presentation_judges = []  # list of Judge
        self.presentation_time = None  # float

        self.poster_pdf = poster_pdf
        self.full_paper_pdf = full_paper_pdf

    def __eq__(self, other):
        return self.student_id == other.student_id

    def __hash__(self):
        return self.student_id

    def __str__(self):
        return "\n".join(
            [f"{field}: {value}" for field, value in self.__dict__.items()]
        )
