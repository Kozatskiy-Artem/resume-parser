from resume_parser.dto import CriteriaDTO
from resume_parser.exceptions import ResumeNotFoundError
from resume_parser.work_ua_parser import WorkUaParser

if __name__ == "__main__":
    criteria = CriteriaDTO(
        position="Developer",
        location="Харків",
        salary_from=15000,
        salary_to=40000,
        experience=0.6,
        skills_and_keywords="python, selenium, rpa",
    )

    parser = WorkUaParser()

    try:
        parser.set_params(criteria)
    except ResumeNotFoundError:
        print("Резюме кандидатів за заданими параметрами не знайдено!")
