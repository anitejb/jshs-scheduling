"""Functions that were abandoned for the final deliverable, but may prove useful for further development."""


def get_cat_time_judges(judge_roster, paper_reviewers):
    # Data structure explanation/template
    # cat_time_judges = {
    #     0: {
    #         0: [judge1, judge2, judge3,],
    #         0.5: [judge2, judge3,],
    #         ...,
    #         59.5: [judge1, judge7, judge9,],
    #     },
    #     1: {
    #         0: [judge4, judge7,],
    #         0.5: [judge4, judge7, judge8,],
    #         ...
    #     },
    #     ...
    # }
    cat_time_judges = dict()
    for judge in judge_roster:
        # TODO: remove paper_reviewer as an arg?
        # if judge.is_paper_reviewer != paper_reviewers:
        #     continue
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
    return cat_time_judges


def assign_papers_ignoring_category(judge_roster, student_roster):
    # Aggregate all students who still need papers reviewed
    students = []
    for student in student_roster:
        if student.is_paper and len(student.paper_judges) < 2:
            students.append(student)

    total_num_paper_assignments = 2 * len(
        [student for student in student_roster if student.is_paper]
    )
    total_num_paper_reviewers = len(
        [judge for judge in judge_roster if judge.is_paper_reviewer]
    )
    threshold = math.ceil(total_num_paper_assignments / total_num_paper_reviewers)
    # Maybe modify threshold calculations so that judges who do both poster + paper get less papers (using a lower threshold)?

    # Aggregate all judges who are paper reviewers
    judges = [
        judge
        for judge in judge_roster
        if judge.is_paper_reviewer and len(judge.assigned_papers) < threshold
    ]

    # Sort first by ascending number of papers, second by ascending number of presentations
    judges.sort(
        key=lambda judge: (
            len(judge.assigned_papers),
            len(judge.assigned_presentations),
        )
    )

    judge_index = 0
    for student in students:
        while len(student.paper_judges) < 2:
            # if judges:
            #     judge_index %= len(judges)
            # else:
            #     break
            judge_index %= len(judges)

            judge = judges[judge_index]
            judge.assign_paper(student)
            if len(judge.assigned_papers) >= threshold:
                judges.remove(judge)
            else:
                judge_index += 1


def assign_presentations_old(judge_roster, student_roster):
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

    judges_schedule = get_cat_time_judges(judge_roster, paper_reviewers=True)

    for cat in sorted(
        judges_schedule, key=lambda category: len(category_judges[category])
    ):
        availability = list(judges_schedule[cat].keys())
        availability.sort(key=lambda time_index: len(judges_schedule[cat][time_index]))

        students = set(students_by_cat[cat])

        # for each category:
        # starting with assigned_yet=0, iterate through all timeslots. assign pairs of judges if both have <=i presentations
        # assigned and remove those pairs from the timeslot they are assigned from.
        # increment assigned_yet and repeat until all of this category's students' presentations are assigned
        # or there are no time slots left for the category with at least two judges

        assigned_yet = 0
        while students and judges_schedule[cat]:
            for time_index in availability:
                if time_index not in judges_schedule[cat]:
                    continue
                judges = [
                    judge
                    for judge in judges_schedule[cat][time_index]
                    if len(judge.assigned_presentations) <= assigned_yet
                    and judge.presentation_slots
                ]
                judges.sort(
                    key=lambda judge: len(judge.assigned_presentations), reverse=True
                )

                while len(judges) >= 2 and students:
                    student = students.pop()
                    for _ in range(2):
                        judge = judges.pop()
                        judge.assign_presentation(student, time_index)
                        if judge.is_paper_reviewer and student.is_paper:
                            judge.assign_paper(student)
                        judges_schedule[cat][time_index].remove(judge)

                if len(judges_schedule[cat][time_index]) <= 1:
                    del judges_schedule[cat][time_index]
            assigned_yet += 1

        # Should print nothing if all students were assigned
        # for student in students:
        #     print(student.student_id)

    # TODO: Edge cases (leftover students)
