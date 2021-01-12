class Judge:
    PAPER_LIMIT = 7

    def __init__(
        self,
        judge_id,
        first,
        last,
        email,
        phone,
        preferred_categories,
        is_paper_reviewer,
        presentation_availability,
    ):
        self.judge_id = judge_id  # int
        self.first = first  # str
        self.last = last  # str
        self.email = email  # str
        self.phone = phone  # str
        self.preferred_categories = preferred_categories  # list of int
        self.is_paper_reviewer = is_paper_reviewer  # bool
        self.presentation_availability = presentation_availability  # list of float

        self.presentation_slots = len(self.presentation_availability)  # int

        self.assigned_presentations = []  # list of Student
        self.assigned_times = []  # list of float
        self.assigned_papers = []  # list of Student

    def __eq__(self, other):
        return self.judge_id == other.judge_id

    def assign_presentation(self, student, time_index=None):
        if not self.presentation_slots:
            raise Exception("No slots available")
        if len(student.presentation_judges) >= 2:
            raise Exception("Too many presentation judges")
        if (
            len(student.presentation_judges) == 1
            and student.presentation_judges[0] == self
        ):
            raise Exception("Trying to add same judge twice")
        self.presentation_slots -= 1
        self.assigned_presentations.append(student)
        if not time_index:
            time_index = self.presentation_availability[self.presentation_slots]
        self.assigned_times.append(time_index)
        student.presentation_judges.append(self)
        student.presentation_time = time_index

    def assign_paper(self, student):
        # if len(self.assigned_papers) >= self.PAPER_LIMIT:
        #     raise Exception("Paper limit reached")
        if len(student.paper_judges) >= 2:
            raise Exception("Too many paper judges")
        if len(student.paper_judges) == 1 and student.paper_judges[0] == self:
            raise Exception("Trying to add same judge twice")
        self.assigned_papers.append(student)
        student.paper_judges.append(self)

    def __str__(self):
        return f"{self.first} {self.last}"
        # return "\n".join(
        #     [f"{field}: {value}" for field, value in self.__dict__.items()]
        # )
