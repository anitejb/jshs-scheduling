import csv
import math
import datetime
import re
from config import START_DATE, START_TIME, END_TIME, YEAR


JUDGE_AVAILABILITY_DAYS = (
    "Monday, January 18",
    "Tuesday, January 19",
    "Wednesday, January 20",
    "Thursday, January 21",
    "Friday, January 22",
)
JUDGE_AVAILABILITY_COLUMN_NAMES = tuple(
    f"Availability for Poster and/or Oral Evaluation for Monday, January 18-Friday, January 22, 8:00am - 8:00pm. (Please select  a minimum of 2, but more is appriciated.) [{day}]"
    for day in JUDGE_AVAILABILITY_DAYS
)
JUDGE_CATEGORIES = {
    "Medicine and Health; Behavioral and Social Sciences": 0,
    "Life sciences (general biology—animal sciences, plant sci, ecology; cellular and molecular bio, genetics, immunology, bio)": 1,
    "Engineering; technology (including renewable energies, robotics)": 2,
    "Environmental science (pollution and impact upon ecosystems, environmental management, bioremediation, climatology, weather)": 3,
    "Chemistry (including chemistry-physical, organic, inorganic; earth science-geochemistry; materials science, alternative fuels)": 4,
    "Mathematics and Computer science/computer engineering; applied mathematics-theoretical computer science": 5,
    "Physical Sciences – physics; computational astronomy; theoretical mathematics": 6,
    "Biomedical Sciences, Molecular/Cellular": 7,
}
STUDENT_CATEGORIES = {
    "Medicine & Health/Behavioral Sci": 0,
    "Life Sciences": 1,
    "Engineering & Technology": 2,
    "Environmental Sciences": 3,
    "Chemistry": 4,
    "Mathematics & Computer Science": 5,
    "Physical Sciences": 6,
    "Biomedical Sciences": 7,
}


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
        self.presentation_availability = (
            presentation_availability  # dict of (str: list of str)
        )

        # 30 min slots, 2 slots per hour (multiply total slots by factor of 2)
        self.presentation_slots = (
            sum(len(day) for day in presentation_availability.values()) * 2
        )  # int

        self.assigned_presentations = []  # list of Student
        self.assigned_papers = []  # list of Student

    def __eq__(self, other):
        return self.judge_id == other.judge_id

    def assign_presentation(self, student):
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
        student.presentation_judges.append(self)

    def assign_paper(self, student):
        if len(self.assigned_papers) >= self.PAPER_LIMIT:
            raise Exception("Paper limit reached")
        if len(student.paper_judges) >= 2:
            raise Exception("Too many paper judges")
        if len(student.paper_judges) == 1 and student.paper_judges[0] == self:
            raise Exception("Trying to add same judge twice")
        self.assigned_papers.append(student)
        student.paper_judges.append(self)

    def __str__(self):
        return "\n".join(
            [f"{field}: {value}" for field, value in self.__dict__.items()]
        )


class Student:
    def __init__(self, student_id, is_paper, is_poster, category):
        self.student_id = student_id  # int
        self.is_paper = is_paper  # bool
        self.is_poster = is_poster  # bool
        self.category = category  # int

        self.paper_judges = []  # list of Judge
        self.presentation_judges = []  # list of Judge

    def __eq__(self, other):
        return self.student_id == other.student_id

    def __str__(self):
        return "\n".join(
            [f"{field}: {value}" for field, value in self.__dict__.items()]
        )


def time_slot_to_time(time_slot_name):
    # 11:00 am - 12:00 pm
    pattern = r"(\d{1,2}):\d{2}\s*([ap])m"  # Minutes are not captured, but minutes are not assumed to be "00"
    hour, am_pm = re.search(pattern, column_name).group(1, 2)
    if am_pm == "p":
        hour += 12
    else:
        # TODO: remove assert
        assert am_pm == "a"
    return hour


def column_name_to_date(column_name):
    pattern = r"\[.*(\w+)\s+([0-3][0-9])\]"
    month, date_ = re.search(pattern, column_name).group(1, 2)
    return datetime.date(year=YEAR, month=month, day=date_)


def date_and_time_to_index(date_, time_):
    # Assumes that date_ is passed in as a datetime object, time_ is passed in as the hour number (an int)
    start_date = datetime.date.fromisoformat(START_DATE)
    day_num = (date_ - start_date).days
    return (time_ - START_TIME) + day_num * (END_TIME - START_TIME)


def create_judge_roster(csv_filename):
    with open(csv_filename, encoding="utf-8") as csvfile:
        judge_roster = list()
        csvreader = csv.DictReader(csvfile)

        # Create an entry in the roster for each judge with their contact details, preferred categories, and availability
        for row in csvreader:
            new_presentation_availability = set()
            for column_name, times_selected in row.items():
                if column_name not in JUDGE_AVAILABILITY_COLUMN_NAMES:
                    continue
                column_date = column_name_to_date(column_name)
                if times_selected:
                    for time_slot in times_selected.split(","):
                        index_at_00_min = date_and_time_to_index(
                            column_date,
                            time_slot_to_time(time_slot),
                        )
                        new_presentation_availability.add(index_at_00_min)
                        new_presentation_availability.add(index_at_00_min + 0.5)
            new_judge = Judge(
                judge_id=csvreader.line_num,  # using the line number as a sequential ID field for each judge
                first=row["First Name"],
                last=row["Last Name"],
                email=row["Email Address"],
                phone=row["Cell Phone Number"],
                preferred_categories=[
                    JUDGE_CATEGORIES[category]
                    for category in JUDGE_CATEGORIES
                    if row[
                        "What categories would you would prefer to review and/or judge?"
                    ].find(category)
                    != -1
                ],
                is_paper_reviewer=row[
                    "Would you like to volunteer as a paper reviewer?"
                ]
                == "Yes",
                # presentation_availability={
                #     # TODO: Hardcoded day name extraction, should be revised later on
                #     column_name.partition("[")[2].rpartition("]")[0]: [time.strip() for time in times_selected.split(",")]
                #     for column_name, times_selected in row.items()
                #     if column_name in JUDGE_AVAILABILITY_COLUMN_NAMES and times_selected
                # }
                presentation_availability=new_presentation_availability,
            )
            judge_roster.append(new_judge)

            # YYYY-MM-DDTHH:MM : 0
            # 2021-01-18T08:00 : 0

    return judge_roster


def create_student_roster(csv_filename):
    with open(csv_filename, encoding="utf-8") as csvfile:
        student_roster = []

        csvreader = csv.DictReader(csvfile)
        # Create an entry in the roster for each student
        for row in csvreader:
            new_student = Student(
                student_id=row["Student Number"],
                is_paper="Oral" in row["Participation Type"],
                is_poster="Poster" in row["Participation Type"],
                category=STUDENT_CATEGORIES[
                    row[
                        "Research Category of Competition. Please note: your chosen category is not guaranteed."
                    ]
                ],
            )
            student_roster.append(new_student)

    return student_roster


def get_cat_time_judges(judge_roster):
    # Data structure explanation/template
    # cat_time_judges = {
    #     0: {
    #         "Monday 8 am": [judge1, judge2, judge3,],
    #         "Monday 9 am": [judge2, judge3,],
    #         ...,
    #         "Friday 8 pm": [judge1, judge7, judge9,],
    #     },
    #     1: {
    #         "Monday 8 am": [judge4, judge7,],
    #         "Monday 9 am": [judge4, judge7, judge8,],
    #         ...
    #     },
    #     ...
    # }
    cat_time_judges = dict()
    for judge in judge_roster:
        for cat in judge.preferred_categories:
            for time_slot in judge.presentation_availability:
                if cat not in cat_time_judges:
                    cat_time_judges[cat] = dict()
                    cat_time_judges[cat][time_slot] = [judge]
                    continue
                if time_slot in cat_time_judges[cat]:
                    cat_time_judges[cat][time_slot].append(judge)
                else:
                    cat_time_judges[cat][time_slot] = [judge]


def assign_presentations(judge_roster, student_roster):
    pass


def assign_papers(judge_roster, student_roster):
    # Aggregate all students who still need papers reviewed
    students = []
    for student in student_roster:
        if student.is_paper and len(student.paper_judges) == 0:
            # Add student twice because they need two judges
            students.append(student)
            students.append(student)
        if student.is_paper and len(student.paper_judges) == 1:
            # Add student once because they need one judge
            students.append(student)
    # Randomly shuffle students so that the chances of getting assigned the same judge are minimized
    random.shuffle(students)

    # Aggregate all judges who are papers reviewers
    judges = [judge for judge in judge_roster if judge.is_paper_reviewer]

    # Sort first by ascending number of papers, second by ascending number of presentations
    judges.sort(
        key=lambda judge: (
            len(judge.assigned_papers),
            len(judge.assigned_presentations),
        )
    )

    # Number of assigned papers per judge (sorted in ascending order)
    judge_paper_vals = [len(judge.assigned_papers) for judge in judges]

    # Find threshold (max number of papers that one judge can be assigned)
    total_papers = sum(judge_paper_vals) + len(students)
    threshold = math.ceil(total_papers / len(judges))
    # Maybe modify threshold calculations so that judges who do both poster + paper get less papers?

    # TODO: Assign judges


def index_to_datetime(index):
    hour = index % (END_TIME - START_TIME) + START_TIME
    date_ = index // (END_TIME - START_TIME) + datetime.date.fromisoformat(START_DATE)
    return datetime.datetime(year=YEAR, month=date_.month, day=date_.day, hour=hour)


def output(judge_roster, student_roster):
    out = []
    for judge in judge_roster:
        out.append(
            f"{judge.first} {judge.last}:"
            f" {len(judge.assigned_presentations)}, {len(judge.assigned_papers)}"
        )

    for student in student_roster:
        if student.paper_and_oral:
            out.append(
                f"{student.student_id}: "
                f"{'Paper' if student.paper_and_oral else ''}"
                " | "
                f"{'Poster' if student.poster else ''}"
                " | "
                f"{student.presentation_judge.first if student.presentation_judge else ''}"
                f"{student.presentation_judge.last if student.presentation_judge else ''}"
                " | "
                f"{student.presentation_judge2.first if student.presentation_judge2 else ''}"
                f"{student.presentation_judge2.last if student.presentation_judge2 else ''}"
                " | "
                f"{student.paper_judge.first if student.paper_judge else ''}"
                f"{student.paper_judge.last if student.paper_judge else ''}"
            )

    print("\n".join(out))


def main():
    judge_data_path = "sample_judge_data.csv"
    student_data_path = "sample_student_data.csv"

    judge_roster = create_judge_roster(judge_data_path)
    student_roster = create_student_roster(student_data_path)
    assign_presentations(judge_roster, student_roster)
    assign_papers(judge_roster, student_roster)
    output(judge_roster, student_roster)


if __name__ == "__main__":
    main()
