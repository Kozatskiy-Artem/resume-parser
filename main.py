from resume_parser.dto import CriteriaDTO
from resume_parser.exceptions import ResumeNotFoundError
from resume_parser.robota_ua_resume_searcher import RobotaUaResumeSearcher
from resume_parser.work_ua_resume_parser import WorkUaResumeParser
from resume_parser.work_ua_resume_searcher import WorkUaResumeSearcher

if __name__ == "__main__":
    criteria = CriteriaDTO(
        position="Developer",
        location="Харків",
        salary_from=10000,
        salary_to=100000,
        experience=2,
        skills_and_keywords=["python", "selenium", "rpa", "git", "php", "html", "angular", "react", "css", "ajax"],
    )

    work_ua_searcher = WorkUaResumeSearcher()
    robota_ua_searcher = RobotaUaResumeSearcher()

    try:
        work_ua_searcher.set_params(criteria)
        robota_ua_searcher.set_params(criteria)
    except ResumeNotFoundError:
        print("Резюме кандидатів за заданими параметрами не знайдено!")

    work_ua_resume_parser = WorkUaResumeParser()
    work_ua_resume_parser.pars_resumes(work_ua_searcher.resume_links, criteria)
