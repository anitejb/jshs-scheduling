import csv
from pathlib import Path
import shutil
import itertools

from judge import Judge
from student import Student
from util import (
    PresentationAssignmentError,
    time_slot_to_time,
    column_name_to_date,
    date_and_time_to_index,
    index_to_datetime,
    value_to_excel_csv_string,
)
from config import (
    JudgeColumnNames,
    StudentColumnNames,
    JUDGE_CATEGORIES,
    STUDENT_CATEGORIES,
    CATEGORY_NUMBERS_TO_LABELS,
    INPUT_FOLDER_PATH,
    OUTPUT_FOLDER_PATH,
    STUDENT_DATA,
    JUDGE_DATA,
    ERROR_FILE,
)


def create_judge_roster(csv_filename):
    with open(csv_filename, encoding="utf-8") as csvfile:
        judge_roster = list()
        csvreader = csv.DictReader(csvfile)

        # Create an entry in the roster for each judge with their contact details, preferred categories, and availability
        for row in csvreader:
            if not any(row.values()):
                continue

            new_presentation_availability = list()
            for column_name, times_selected in row.items():
                if column_name not in JudgeColumnNames.JUDGE_AVAILABILITY_COLUMN_NAMES:
                    continue
                column_date = column_name_to_date(column_name)
                if times_selected:
                    for time_slot in times_selected.split(","):
                        if not time_slot:
                            continue
                        index_at_00_min = date_and_time_to_index(
                            column_date,
                            time_slot_to_time(time_slot),
                        )
                        new_presentation_availability.append(index_at_00_min)
                        new_presentation_availability.append(index_at_00_min + 0.5)

            new_judge = Judge(
                judge_id=csvreader.line_num,  # using the line number as a sequential ID field for each judge
                first=row[JudgeColumnNames.FIRST_NAME],
                last=row[JudgeColumnNames.LAST_NAME],
                email=row[JudgeColumnNames.EMAIL],
                phone=row[JudgeColumnNames.PHONE],
                preferred_categories=[
                    JUDGE_CATEGORIES[category]
                    for category in JUDGE_CATEGORIES
                    if row[JudgeColumnNames.PREFERRED_CATEGORIES].find(category) != -1
                ],
                is_paper_reviewer=row[JudgeColumnNames.IS_PAPER_REVIEWER] == "Yes",
                presentation_availability=new_presentation_availability,
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
                student_id=int(row[StudentColumnNames.SUBMISSION_NUMBER]),
                is_paper="Oral" in row[StudentColumnNames.PARTICIPATION_TYPE],
                is_poster="Poster" in row[StudentColumnNames.PARTICIPATION_TYPE],
                category=STUDENT_CATEGORIES[row[StudentColumnNames.CATEGORY]],
                poster_pdf=row[StudentColumnNames.POSTER_PDF_UPLOAD],
                full_paper_pdf=row[StudentColumnNames.PAPER_PDF_UPLOAD],
            )
            student_roster.append(new_student)

    return student_roster


def assign_presentations(judge_roster, student_roster):
    # Aggregate all students by category who will be poster presenters
    students_by_cat = {
        cat: [
            student
            for student in student_roster
            if student.is_poster and student.category == cat
        ]
        for cat in STUDENT_CATEGORIES.values()
    }

    category_judges = {category: [] for category in JUDGE_CATEGORIES.values()}
    for judge in judge_roster:
        # Filter out judges who only review papers
        if not judge.presentation_slots:
            continue
        for category in judge.preferred_categories:
            category_judges[category].append(judge)

    for cat in sorted(
        category_judges, key=lambda category: len(category_judges[category])
    ):
        students = students_by_cat[cat][:]

        assigned_yet = 0
        while students and assigned_yet <= len(students_by_cat[cat]):
            judges = [
                judge
                for judge in category_judges[cat]
                if len(judge.assigned_presentations) <= assigned_yet
                and judge.presentation_slots >= 1
            ]
            for judge in judges:
                if not students:
                    break
                student = students.pop()
                judge.assign_presentation(student)
                if judge.is_paper_reviewer and student.is_paper:
                    judge.assign_paper(student)

            assigned_yet += 1

        if students:
            error_message = (
                f"The category {CATEGORY_NUMBERS_TO_LABELS[cat]} did not have enough judges to evaluate all presentations.\n"
                "Either assign more judges to this category or transfer some students out of this category.\n"
                f"There are {len(students_by_cat[cat])} student(s) in this category who are presenting posters and {len(category_judges[category])} "
                "judge(s) who have submitted availability to evaluate poster presentations.\n"
            )
            raise PresentationAssignmentError(error_message)


def assign_papers(judge_roster, student_roster):
    # Aggregate all students by category who will be poster presenters
    students_by_cat = {
        cat: [
            student
            for student in student_roster
            if student.is_paper
            and len(student.paper_judges) < 2
            and student.category == cat
        ]
        for cat in STUDENT_CATEGORIES.values()
    }

    category_judges = {category: [] for category in JUDGE_CATEGORIES.values()}
    for judge in judge_roster:
        # Filter out judges who only do posters
        if not judge.is_paper_reviewer:
            continue
        for category in judge.preferred_categories:
            category_judges[category].append(judge)

    for cat in sorted(
        category_judges, key=lambda category: len(category_judges[category])
    ):
        students = students_by_cat[cat][:]
        conflict_students = []

        assigned_yet = 0
        while students:
            judges = [
                judge
                for judge in category_judges[cat]
                if len(judge.assigned_papers) <= assigned_yet
            ]

            for judge in judges:
                if not students:
                    break
                student = students.pop()
                if len(student.paper_judges) == 1 and student.paper_judges[0] == judge:
                    conflict_students.append(student)
                    break
                judge.assign_paper(student)
                if len(student.paper_judges) < 2:
                    students.append(student)

            assigned_yet += 1

        # Handle conflicts
        judges = category_judges[cat][:]
        for student in conflict_students:
            judges.sort(
                key=lambda judge: (
                    len(judge.assigned_papers),
                    len(judge.assigned_presentations),
                )
            )
            judge_iter = itertools.cycle(judges)
            while len(student.paper_judges) < 2:
                judge = next(judge_iter)
                if len(student.paper_judges) == 1 and student.paper_judges[0] == judge:
                    continue
                judge.assign_paper(student)


def output(judge_roster, student_roster, error=None):
    output_folder_path = Path(OUTPUT_FOLDER_PATH)
    if output_folder_path.exists():
        shutil.rmtree(output_folder_path)
    output_folder_path.mkdir()

    if error:
        error_path = output_folder_path / ERROR_FILE
        print(
            f"[Error]\n{error}\nCheck {str(error_path.resolve())} to review this error message."
        )
        with open(error_path, "w") as error_file:
            error_file.write(error)
        return

    out = []
    for judge in judge_roster:
        out.append(
            f"{judge.first} {judge.last}:"
            f" Posters: {len(judge.assigned_presentations)}, Papers: {len(judge.assigned_papers)}"
        )

    for student in student_roster:
        out.append(
            f"{student.student_id}: "
            f"{'Paper' if student.is_paper else ''}: {student.paper_judges[0] if len(student.paper_judges) else ''}, {student.paper_judges[1] if len(student.paper_judges) == 2 else ''}"
            " | "
            f"{'Poster' if student.is_poster else ''}: {student.presentation_judges[0] if len(student.presentation_judges) else ''}"
        )

    student_headers = [
        "Submission Number",
        "Oral/Paper",
        "Poster",
        "Category",
        "Paper Judge 1",
        "Paper Judge 2",
        "Poster Judge 1",
        "Poster Date",
        "Poster Time",
    ]
    paper_judges_headers = [
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "Assigned Student Number",
        "Paper PDF",
    ]
    poster_judges_headers = [
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "Assigned Student Number",
        "Date",
        "Time",
        "Poster PDF",
    ]
    judges_headers = [
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "Poster Assignments",
        "Paper Assignments",
    ]
    presentation_schedule_headers = [
        "Date",
        "Time",
        "Student Number",
        "Judge 1 First Name",
        "Judge 1 Last Name",
        "Judge 1 Email",
        "Judge 1 Phone",
    ]

    with open(output_folder_path / "students.csv", "w", newline="") as students_csv:
        student_writer = csv.writer(students_csv)
        student_writer.writerow(student_headers)
        for student in student_roster:
            poster_date, poster_time = "", ""
            if student.is_poster:
                poster_date, poster_time = index_to_datetime(student.presentation_time)
            student_row = [
                student.student_id,
                "Yes" if student.is_paper else "No",
                "Yes" if student.is_poster else "No",
                CATEGORY_NUMBERS_TO_LABELS[student.category],
                student.paper_judges[0] if student.is_paper else "",
                student.paper_judges[1] if student.is_paper else "",
                student.presentation_judges[0] if student.is_poster else "",
                poster_date,
                poster_time,
            ]
            student_writer.writerow(student_row)

    with open(
        output_folder_path / "paper_judges.csv", "w", newline=""
    ) as paper_judges_csv:
        paper_judges_writer = csv.writer(paper_judges_csv)
        paper_judges_writer.writerow(paper_judges_headers)
        for judge in judge_roster:
            if not judge.is_paper_reviewer:
                continue
            for student in judge.assigned_papers:
                paper_judge_row = [
                    judge.first,
                    judge.last,
                    judge.email,
                    judge.phone,
                    student.student_id,
                    student.full_paper_pdf,
                ]
                paper_judges_writer.writerow(paper_judge_row)

    with open(
        output_folder_path / "poster_judges.csv", "w", newline=""
    ) as poster_judges_csv:
        poster_judges_writer = csv.writer(poster_judges_csv)
        poster_judges_writer.writerow(poster_judges_headers)
        for judge in sorted(judge_roster, key=lambda judge: (judge.first, judge.last)):
            if not judge.presentation_availability:
                continue

            for student in sorted(
                judge.assigned_presentations,
                key=lambda student: student.presentation_time,
            ):
                poster_date, poster_time = index_to_datetime(student.presentation_time)
                poster_judge_row = [
                    judge.first,
                    judge.last,
                    judge.email,
                    judge.phone,
                    student.student_id,
                    poster_date,
                    poster_time,
                    student.poster_pdf,
                ]
                poster_judges_writer.writerow(poster_judge_row)

    with open(output_folder_path / "judges.csv", "w", newline="") as judges_csv:
        judges_writer = csv.writer(judges_csv)
        judges_writer.writerow(judges_headers)
        for judge in sorted(judge_roster, key=lambda judge: (judge.first, judge.last)):

            poster_assignment = []
            paper_assignment = []
            for student in sorted(
                judge.assigned_presentations,
                key=lambda student: student.presentation_time,
            ):
                poster_date, poster_time = index_to_datetime(student.presentation_time)
                poster_assignment.append(
                    f"Student {student.student_id}: {poster_date} {poster_time}"
                )

            for student in sorted(
                judge.assigned_papers, key=lambda student: student.student_id
            ):
                paper_assignment.append(f"Student {student.student_id}")

            judge_row = [
                judge.first,
                judge.last,
                judge.email,
                judge.phone,
                "\n".join(poster_assignment),
                "\n".join(paper_assignment),
            ]
            judges_writer.writerow(judge_row)

    with open(
        output_folder_path / "presentation_schedule.csv", "w", newline=""
    ) as presentation_schedule_csv:
        presentation_schedule_writer = csv.writer(presentation_schedule_csv)
        presentation_schedule_writer.writerow(presentation_schedule_headers)

        presentations = []
        for student in sorted(
            student_roster,
            key=lambda student: student.presentation_time
            if student.presentation_time is not None
            else 0,
        ):
            if not student.is_poster:
                continue
            presentations.append(
                [
                    *index_to_datetime(student.presentation_time),
                    student.student_id,
                    student.presentation_judges[0].first,
                    student.presentation_judges[0].last,
                    student.presentation_judges[0].email,
                    student.presentation_judges[0].phone,
                ]
            )

        presentation_schedule_writer.writerows(presentations)

    print(
        f"Scheduling successfully completed!\nOutput data can be found in {str(output_folder_path.resolve())}."
    )


def main():
    input_folder_path = Path(INPUT_FOLDER_PATH)
    input_judge_data_path = input_folder_path / JUDGE_DATA
    input_student_data_path = input_folder_path / STUDENT_DATA
    if not (
        input_folder_path.exists()
        and input_student_data_path.exists()
        and input_judge_data_path.exists()
    ):
        error_message = "The following files are missing."
        if not input_folder_path.exists():
            error_message += f'\n"{str(input_folder_path.resolve())}" (input folder)'
        if not input_student_data_path.exists():
            error_message += (
                f'\n"{str(input_student_data_path.resolve())}" (input student data)'
            )
        if not input_judge_data_path.exists():
            error_message += (
                f'\n"{str(input_judge_data_path.resolve())}" (input judge data)'
            )
        error_message += "\n"
        output(None, None, error=error_message)
        return

    judge_roster = create_judge_roster(input_judge_data_path)
    student_roster = create_student_roster(input_student_data_path)
    try:
        assign_presentations(judge_roster, student_roster)
    except PresentationAssignmentError as e:
        output(None, None, error=e.message)
        return
    assign_papers(judge_roster, student_roster)
    output(judge_roster, student_roster)


if __name__ == "__main__":
    main()
