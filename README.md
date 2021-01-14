# JSHS Scheduling

## Overview
A script for efficiently scheduling judges to review papers and poster presentations for the 2021 New Jersey [Junior Science & Humanities Symposium](https://soe.rutgers.edu/jshs) at Rutgers University.

Built with pure [Python](https://www.python.org) and <3.

## Usage

### Initial Setup
0. Download Python (recommended v3.9, at least v3.7+) from [here](https://www.python.org/downloads).
0. Download the repository as a ZIP file by clicking [here](https://github.com/anitejb/jshs-scheduling/archive/master.zip).
0. Extract the contents of the ZIP file into a folder on your computer.

### Student Data
0. Ensure that all of the student records are on the same sheet (combine them onto the same sheet if necessary).
0. Ensure that there is nothing else in the sheet (remove any notes/comments after the last row of student data).
0. Ensure that the column names match the column names described under `class StudentColumnNames` in `config.py`.
    > Helpful tip: You can view `config.py` by opening it using Notepad or a similar text editor.
0. From Google Sheets or Excel, download the file with a `.csv` extension.
    * On Google Sheets, this can be done by clicking `File` > `Download` > `Comma-separated values (.csv, current sheet)`.
    * Name this file `student_data.csv` and place it in the `input` folder.

### Judge Data
0. Ensure that all of the judge records are on the same sheet (combine them onto the same sheet if necessary).
0. Ensure that there is nothing else in the sheet (remove any notes/comments after the last row of judge data).
0. Ensure that all of the actual data is consistent with any formatting that may have been applied.
    * For example, if a single time slot in a cell detailing a judge's availability is struck through (like ~~9:00 am - 10:00 am~~), it will still be interpreted as a valid time. To fix this, simply delete the time slot from the cell.
    * Any data that should not be considered **must be deleted from the sheet**.
0. Ensure that the column names match the column names described under `class JudgeColumnNames` in `config.py`.
0. From Google Sheets or Excel, download the file with a `.csv` extension.
    * On Google Sheets, this can be done by clicking `File` > `Download` > `Comma-separated values (.csv, current sheet)`.
    * Name this file `judge_data.csv` and place it in the `input` folder.

### Running the Scheduler
* On Windows only: Execute `run.bat` in the folder containing the program (from Windows File Explorer, you can do this by opening the file from the folder directly).
* On Windows or Mac/Linux: open a terminal in the folder containing the program and run the program with the command `py main.py` or `python main.py`, respectively.


### Working with the Output
The program will generate five output CSV files:
* `judges.csv`: each row holds all of the scheduling info that the named judge needs to see, including:
    * The judge's first and last name, email, and phone number,
    * that judge's poster presentation assignments (if they signed up to judge poster presentations),
    * that judge's paper assignments (if they signed up to review papers).
* `paper_judges.csv`: each row represents the assignment of a paper to a judge, including:
    * The assigned-to judge's first and last name, email, and phone number,
    * the submission number of the student whose paper was assigned,
    * a link to the PDF of the student's paper.
* `poster_judges.csv`: each row represents the assignment of a poster presentation to a judge, including:
    * The assigned-to judge's first and last name, email, and phone number,
    * the submission number of the student whose poster was assigned,
    * the date and time of the poster presentation,
    * a link to the PDF of the student's poster.
* `presentation_schedule.csv`: each row represents a presentation occurring at the given date and time, including:
    * The date and time in question,
    * a student presenting at this time,
    * that student's judge's first and last name, email, and phone number.
* `students.csv`: each row holds all of the scheduling info that the named student needs to see, including:
    * The student's submission number,
    * whether they are submitting a paper and oral presentation or not,
    * whether they are submitting a poster or not,
    * the student's submission category,
    * the student's paper judges' names (if the student is submitting a paper and oral presentation),
    * the student's poster judge's name (if the student is submitting a poster),
    * the student's poster presentation date and time (if the student is submitting a poster).

If for some reason the program runs into an error, a text file with the error message will be generated in the output folder and no CSV files will be generated.

## Authors

This project was developed in equal part by Anitej Biradar ([@anitejb](https://github.com/anitejb)) and [@mmatlin](https://github.com/mmatlin).

## License

Copyright (c) 2021 Anitej Biradar ([@anitejb](https://github.com/anitejb)) and [@mmatlin](https://github.com/mmatlin). Released under the MIT License. See [LICENSE](LICENSE) for details.
