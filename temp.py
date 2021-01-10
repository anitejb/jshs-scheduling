from itertools import chain
import csv

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
    "Biomedical Sciences, Molecular/Cellular": 7
}
STUDENT_CATEGORIES = {
    "Medicine & Health/Behavioral Sci": 0,
    "Life Sciences": 1,
    "Engineering & Technology": 2,
    "Environmental Sciences": 3,
    "Chemistry": 4,
    "Mathematics & Computer Science": 5,
    "Physical Sciences": 6,
    "Biomedical Sciences": 7
}

class Judge:
    PAPER_LIMIT = 7
    def __init__(self, judge_id, first, last, email, phone, preferred_categories, paper_reviewer, presentation_availability):
        self.judge_id = judge_id # int
        self.first = first # str
        self.last = last # str
        self.email = email # str
        self.phone = phone # str
        self.preferred_categories = preferred_categories # list of int
        self.paper_reviewer = paper_reviewer # bool
        self.presentation_availability = presentation_availability # dict of (str, list of str)

        # 30 min slots, 2 slots per hour (multiply total slots by factor of 2)
        self.presentation_slots = sum(len(day) for day in presentation_availability.values()) * 2 # int

        self.assigned_presentations = [] # list of Student
        self.assigned_papers = [] # list of Student

    def assign_presentation(self, student):
        if not self.presentation_slots:
            raise Exception("No slots available")
        if student.presentation_judge is not None:
            raise Exception("Attempting to reassign")
        self.presentation_slots -= 1
        self.assigned_presentations.append(student)
        student.presentation_judge = self

    def assign_presentation2(self, student):
        if not self.presentation_slots:
            raise Exception("No slots available")
        if student.presentation_judge2 is not None:
            raise Exception("Attempting to reassign")
        self.presentation_slots -= 1
        self.assigned_presentations.append(student)
        student.presentation_judge2 = self

    def assign_paper(self, student):
        if student.paper_judge is not None:
            raise Exception("Attempting to reassign")
        if len(self.assigned_papers) >= self.PAPER_LIMIT:
            raise Exception("Paper limit reached")
        self.assigned_papers.append(student)
        student.paper_judge = self

    def __str__(self):
        return "\n".join([f"{field}: {value}" for field, value in self.__dict__.items()])


class Student:
    def __init__(self, student_id, paper_and_oral, poster, category):
        self.student_id = student_id # int
        self.paper_and_oral = paper_and_oral # bool
        self.poster = poster # bool
        self.category = category # int

        self.presentation_judge = None # Judge
        self.presentation_judge2 = None # Judge
        self.paper_judge = None # Judge

    def __str__(self):
        return "\n".join([f"{field}: {value}" for field, value in self.__dict__.items()])


def create_judge_roster(csv_filename):
    with open(csv_filename, encoding="utf-8") as csvfile:
        judge_roster = list()
        csvreader = csv.DictReader(csvfile)

        # Create an entry in the roster for each judge with their contact details, preferred categories, and availability
        for row in csvreader:
            new_judge = Judge(
                csvreader.line_num,
                row["First Name"],
                row["Last Name"],
                row["Email Address"],
                row["Cell Phone Number"],
                [JUDGE_CATEGORIES[category] for category in JUDGE_CATEGORIES if row["What categories would you would prefer to review and/or judge?"].find(category) != -1],
                row["Would you like to volunteer as a paper reviewer?"] == "Yes",
                {
                    column_name: [time.strip() for time in times_selected.split(",")]
                    for column_name, times_selected in row.items()
                    if column_name in JUDGE_AVAILABILITY_COLUMN_NAMES and times_selected
                }
            )
            judge_roster.append(new_judge)

    return judge_roster


def create_student_roster(csv_filename):
    with open(csv_filename, encoding="utf-8") as csvfile:
        student_roster = []

        csvreader = csv.DictReader(csvfile)
        # Create an entry in the roster for each student
        for row in csvreader:
            new_student = Student(
                row["Student Number"],
                "Oral" in row["Participation Type"],
                "Poster" in row["Participation Type"],
                STUDENT_CATEGORIES[row[
                    "Research Category of Competition. Please note: your chosen category is not guaranteed."
                ]]
            )
            student_roster.append(new_student)

    return student_roster


def assign_presentations(judge_roster, student_roster):
    category_judges = {category: [] for category in JUDGE_CATEGORIES.values()}
    for judge in judge_roster:
        # Filter out judges who only review papers
        if not judge.presentation_slots:
            continue
        for category in judge.preferred_categories:
            category_judges[category].append(judge)

    category_students = {category: [] for category in STUDENT_CATEGORIES.values()}
    for student in student_roster:
        # if student.paper_and_oral:
        category_students[student.category].append(student)
        if student.poster:
            category_students[student.category].append(student)

    # Assign to first subqueue as if it is what we currently have as the queue, then once 
    # len(assigned_pres) for the judges in that subqueue == that of the next, merge the two subqueues and repeat
    ##########################################

    for category, judges in sorted(category_judges.items(), key=lambda x: len(x[1])):
        # First split queue into subqueues by amount of already assigned presentations
        judges.sort(key=lambda judge: len(judge.assigned_presentations))
        queue = [[]]
        amt_assigned_split = 0
        for judge in judges:
            if len(judge.assigned_presentations) > amt_assigned_split:
                amt_assigned_split = len(judge.assigned_presentations)
                queue.append([])
            queue[-1].append(judge)
        # Sort subqueues so that judges reviewing only presentations go first
        for subqueue in queue:
            subqueue.sort(key=lambda judge: judge.paper_reviewer)
        # # Join the queue together
        # queue = list(chain(*queue))
        for student in category_students[category]:
            front_queue = queue[0]

            if student.poster and student.presentation_judge:
                front_queue[0].assign_presentation2(student)
            else:
                front_queue[0].assign_presentation(student)

            if front_queue[0].paper_reviewer and len(front_queue[0].assigned_papers) < front_queue[0].PAPER_LIMIT and student.paper_judge is None:
                front_queue[0].assign_paper(student)

            judge = front_queue.pop(0)
            if len(front_queue) == 0:
                if len(queue) == 1 and judge.presentation_slots:
                    queue = [[judge]]
                    continue
                queue.pop(0)
            if judge.presentation_slots:
                lesser_i = None
                for i, subqueue in enumerate(queue):
                    if len(judge.assigned_presentations) == len(subqueue[0].assigned_presentations):
                        subqueue.append(judge)
                        subqueue.sort(key=lambda judge: judge.paper_reviewer)
                        break
                    elif len(judge.assigned_presentations) > len(subqueue[0].assigned_presentations):
                        if i == len(queue) - 1:
                            queue.append([judge])
                            break
                        lesser_i = i
                    else:
                        if lesser_i is not None:
                            queue.insert(lesser_i, [judge])
                            break
                # queue.append(judge)
        # print("\n".join([str(judge) + f"\nAssigned pres number: {len(judge.assigned_presentations)}\nAssigned papers number: {len(judge.assigned_papers)}\n\n" for judge in judges]))


def output(judge_roster, student_roster):
    out = []
    for judge in judge_roster:
        out.append(f"{judge.first} {judge.last}:"
            f" {len(judge.assigned_presentations)}, {len(judge.assigned_papers)}"
        )

    for student in student_roster:
        if student.paper_and_oral:
            out.append(f"{student.student_id}: "
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
    # print("Judge roster:\n", "\n".join([str(judge) for judge in judge_roster]))
    assign_presentations(judge_roster, student_roster)
    output(judge_roster, student_roster)


if __name__ == "__main__":
    main()



def old_assign_papers():
    judge_index = 0
    unassigned_students = []
    for student_index, student in enumerate(students):
        if len(judges[judge_index].assigned_papers) == threshold:
            judge_index += 1
            if judge_index == len(judges):
                unassigned_students += students[student_index:]
                break
        try:
            judges[judge_index].assign_paper(student)
        except Exception as e:
            if e == "Trying to add same judge twice":
                unassigned_students.append(student)

    # Handle collisions
    collision_judges = [
        judge for judge in judges if len(judge.assigned_papers) < threshold
    ]
    collision_judges.sort(key=lambda judge: len(judge.assigned_papers))
    judge_index = 0
    for student in unassigned_students:
        unassigned = True
        while unassigned:
            # do something with judge index
            if student.paper_judges[0] != collision_judges[judge_index]:
                collision_judges[judge_index].assign_paper(student)
                unassigned = False