###########################################
#### Please fill in EXACT column names ####
###########################################

################ Judges ################

# Judge hourly availability question column name format, where "{date_name}"
# will take on the date name values in JUDGE_AVAILABILITY_DATE_NAMES
JUDGE_AVAILABILITY_QUESTION_FORMAT = "Availability for Poster and/or Oral Evaluation for Monday, January 18-Friday, January 22, 8:00am - 8:00pm. (Please select  a minimum of 2, but more is appriciated.) [{date_name}]"

# Judge availability column date name format. For this setting, weekday names,
# month names, and dates can be referred to as "{Weekday}", "{Month}", and "{Date}", respectively.
JUDGE_AVAILABILITY_DATE_NAME_FORMAT = "{Weekday}, {Month} {Date}"

# Days that judges can choose to judge, as written in the form availability questions
_JUDGE_AVAILABILITY_DATE_NAMES = (
    "Monday, January 18",
    "Tuesday, January 19",
    "Wednesday, January 20",
    "Thursday, January 21",
    "Friday, January 22",
)

# Judge availability time slot format. For this setting, hour numbers and am/pm values for
# the start and end times of a given time slot can be referred to as "{Hour}", "{AM_or_PM}",
# "{am_or_pm}", "{Hour_Plus_1}", "{Plus_1_AM_or_PM}", and "{Plus_1_am_or_pm}" (different AM
# and PM references are available for capitalization purposes).
JUDGE_AVAILABILITY_TIME_SLOT_FORMAT = (
    "{Hour}:00 {am_or_pm} - {Hour_Plus_1}:00 {Plus_1_am_or_pm}"
)

# This class holds all of the judge data column names that are used.
class JudgeColumnNames:
    FIRST_NAME = "First Name"
    LAST_NAME = "Last Name"
    EMAIL = "Email Address"
    PHONE = "Cell Phone Number"
    PREFERRED_CATEGORIES = "What categories would you would prefer to review and/or judge?"
    IS_PAPER_REVIEWER = "Would you like to volunteer as a paper reviewer?"

    # Do not edit, this generates judge availability column names
    JUDGE_AVAILABILITY_COLUMN_NAMES = tuple(
        JUDGE_AVAILABILITY_QUESTION_FORMAT.format(date_name=date_name)
        for date_name in _JUDGE_AVAILABILITY_DATE_NAMES
    )


################ Students ################

class StudentColumnNames:
    SUBMISSION_NUMBER = "Submission Number"
    PARTICIPATION_TYPE = "Participation Type"
    CATEGORY = "Research Category of Competition. Please note: your chosen category is not guaranteed."
    POSTER_PDF_UPLOAD = "Upload Digital Poster as PDF."
    PAPER_PDF_UPLOAD = "Upload Full Paper as PDF."


################ Submission categories ################

# These two objects should contain the possible category strings that
# judges and students could choose from. The judge category strings and
# the student category strings should respectively map to the same category number.
# For now this should be done manually.

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

# The mapped-to values in this object should be whichever human-readable versions of
# the category names are preferred, as long as they match the category numbers above.
CATEGORY_NUMBERS_TO_LABELS = {
    0: "Medicine & Health/Behavioral Sci",
    1: "Life Sciences",
    2: "Engineering & Technology",
    3: "Environmental Sciences",
    4: "Chemistry",
    5: "Mathematics & Computer Science",
    6: "Physical Sciences",
    7: "Biomedical Sciences",
}

CATEGORY_NUMBERS_TO_LABELS_JUDGES = {
    0: "Medicine and Health; Behavioral and Social Sciences",
    1: "Life sciences (general biology—animal sciences, plant sci, ecology; cellular and molecular bio, genetics, immunology, bio)",
    2: "Engineering; technology (including renewable energies, robotics)",
    3: "Environmental science (pollution and impact upon ecosystems, environmental management, bioremediation, climatology, weather)",
    4: "Chemistry (including chemistry-physical, organic, inorganic; earth science-geochemistry; materials science, alternative fuels)",
    5: "Mathematics and Computer science/computer engineering; applied mathematics-theoretical computer science",
    6: "Physical Sciences – physics; computational astronomy; theoretical mathematics",
    7: "Biomedical Sciences, Molecular/Cellular",
}

################ Event info ################

YEAR = 2021
START_DATE = "2021-01-18"
# Using 24-hour time, integers only
START_TIME = 8
END_TIME = 20

################ Input/output ################

INPUT_FOLDER_PATH = "input"
OUTPUT_FOLDER_PATH = "output"
STUDENT_DATA = "student_data.csv"
JUDGE_DATA = "judge_data.csv"
ERROR_FILE = "error.txt"
