import json
from typing import Union

import requests

from .dto import CriteriaDTO
from .interfaces import ResumeParserInterface


class RobotaUaResumeParser(ResumeParserInterface):
    """
    Class for parsing resumes on robota.ua website.

    Methods:

    - pars_resumes(resume_links: list[str], params: CriteriaDTO) -> None: Parses resumes from the provided list of
      resume links and extracts relevant information.
    """

    def pars_resumes(self, resume_links: list[str], params: CriteriaDTO) -> None:
        """
        Parses resumes from the provided list of resume links and extracts relevant information.

        Args:
            resume_links (list[str]): A list of URLs pointing to resumes to be parsed.
            params (CriteriaDTO): An instance of the CriteriaDTO class containing search parameters.

        Returns:
            None: The method does not return a value directly, but populates the 'resume_results' dictionary.

        Note:
            If a resume page is not accessible (status code other than 200), it skips to the next resume link.
        """

        for resume_link in resume_links:
            resume_page = requests.get(
                url=f"https://employer-api.robota.ua/resume/{resume_link.split('/')[-1]}?markView=true",
                headers={"user-agent": self.user_agent.random},
            )
            if resume_page.status_code != 200:
                continue

            resume_data = json.loads(resume_page.content)

            self.resume_results[resume_link] = {
                "position": self._get_position(resume_data),
                "matching_keywords": self._match_keywords(resume_data, params.skills_and_keywords),
                "experience": self._check_experience(resume_data),
                "education": self._check_education(resume_data),
            }

    @staticmethod
    def _get_position(resume: dict) -> str:
        """
        Get the position from the resume data.

        Args:
            resume (dict): Resume data in dictionary format.

        Returns:
            str: The position extracted from the resume.
        """

        position = resume["speciality"]
        salary = resume["salary"]
        if int(salary):
            position += ", " + salary + resume["currencySign"]
        return position

    def _match_keywords(self, resume: dict, required_keywords: list[str]) -> Union[str, set]:
        """
        Matches required keywords with text blocks in the resume.

        Args:
            resume (dict): Resume data in dictionary format.
            required_keywords (list[str]): List of required keywords.

        Returns:
            Union[str, set]: Matching keywords found in the resume or a message indicating no matches found.
        """

        resume_text = self._get_description_resume(resume).lower()
        matching_keywords = set()

        for required_keyword in required_keywords:
            if required_keyword in resume_text:
                matching_keywords.add(required_keyword)
        if len(matching_keywords):
            return matching_keywords
        return "Збігів з ключовими словами у резюме не знайдено"

    @staticmethod
    def _get_description_resume(resume: dict) -> str:
        """
        Get the description sections of the resume.

        Args:
        - resume (dict): Resume data in dictionary format.

        Returns:
        - str: Text in the description sections of the resume.
        """

        resume_description = ""

        key_information = resume.get("skills")
        if key_information:
            resume_description += key_information[0].get("description")

        experiences = resume.get("experiences")
        for experience in experiences:
            resume_description += " " + experience.get("description")

        educations = resume.get("educations")
        for education in educations:
            resume_description += " " + education.get("comment")

        additionals = resume.get("additionals")
        for additional in additionals:
            resume_description += " " + additional.get("description")

        return resume_description

    @staticmethod
    def _check_experience(resume: dict):
        """
        Checks if experience is mentioned in the resume.

        Args:
            resume (dict): Resume data in dictionary format.

        Returns:
            str: Indicates if experience is mentioned in the resume.

        """

        experience = resume.get("experiences")
        return "Досвід роботи вказаний" if experience else "Досвід роботи не вказаний"

    @staticmethod
    def _check_education(resume: dict):
        """
        Checks if education is mentioned in the resume.

        Args:
            resume (dict): Resume data in dictionary format.

        Returns:
            str: Indicates if education is mentioned in the resume.
        """

        education = resume.get("educations")
        return "Освіта вказана" if education else "Освіта не вказана"
