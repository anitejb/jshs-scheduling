###########################################
#### Please fill in EXACT column names ####
###########################################

################ Judges ################

# Days that judges can choose to judge, as written in the form availability questions
_JUDGE_AVAILABILITY_DAYS = (
    "Monday, January 18",
    "Tuesday, January 19",
    "Wednesday, January 20",
    "Thursday, January 21",
    "Friday, January 22",
)

# Judge hourly availability question column name format, where "{day}"
# will take on the day values in _JUDGE_AVAILABILITY_DAYS
_JUDGE_AVAILABILITY_QUESTION_FORMAT = "Availability for Poster and/or Oral Evaluation for Monday, January 18-Friday, January 22, 8:00am - 8:00pm. (Please select  a minimum of 2, but more is appriciated.) [{day}]"

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
        _JUDGE_AVAILABILITY_QUESTION_FORMAT.format(day=day)
        for day in _JUDGE_AVAILABILITY_DAYS
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
