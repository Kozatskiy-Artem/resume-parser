from resume_parser.dto import CriteriaDTO
from resume_parser.exceptions import ResumeNotFoundError
from resume_parser.robota_ua_parser import RobotaUaParser
from resume_parser.work_ua_parser import WorkUaParser

if __name__ == "__main__":
    criteria = CriteriaDTO(
        position="Developer",
        location="Харків",
        salary_from=10000,
        salary_to=100000,
        experience=2,
        skills_and_keywords="python, selenium, rpa",
    )

    work_ua_parser = WorkUaParser()
    robota_ua_parser = RobotaUaParser()

    try:
        work_ua_parser.set_params(criteria)
        print("*" * 30)
        robota_ua_parser.set_params(criteria)
    except ResumeNotFoundError:
        print("Резюме кандидатів за заданими параметрами не знайдено!")
