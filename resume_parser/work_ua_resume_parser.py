from typing import Union

import requests
from bs4 import BeautifulSoup

from .constants import ResumeStatus
from .dto import CriteriaDTO
from .interfaces import ResumeParserInterface


class WorkUaResumeParser(ResumeParserInterface):
    """
    Class for parsing resumes on work.ua website.

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
            If the resume is uploaded as a file, it only extracts the position and matching keywords.
        """

        for resume_link in resume_links:
            resume_page = requests.get(url=resume_link, headers={"user-agent": self.user_agent.random})
            if resume_page.status_code != 200:
                continue
            resume = BeautifulSoup(resume_page.content, "lxml")
            is_file = self._get_resume_is_file(resume)
            if is_file:
                self.resume_results[resume_link] = {
                    "position": self._get_position(resume),
                    "matching_keywords": self._match_keywords(resume, params.skills_and_keywords),
                    "is_file": bool(is_file),
                }
            else:
                self.resume_results[resume_link] = {
                    "position": self._get_position(resume),
                    "matching_skills": self._match_skills(resume, params.skills_and_keywords),
                    "matching_keywords": self._match_keywords(resume, params.skills_and_keywords),
                    "experience": self._check_experience(resume),
                    "education": self._check_education(resume),
                    "is_file": bool(is_file),
                }

            self.resume_results[resume_link]["points"] = self._get_resume_points(self.resume_results[resume_link])

    @staticmethod
    def _get_resume_is_file(resume: BeautifulSoup):
        """
        Checks if the resume is uploaded as a file.

        Args:
            resume (BeautifulSoup): The parsed resume page.

        Returns:
            Tag: The tag indicating if the resume is uploaded as a file.
        """

        is_file = resume.find("div", class_="flex").find("span", class_="label-violet-light")
        return is_file

    @staticmethod
    def _get_position(resume: BeautifulSoup) -> str:
        """
        Extracts the position from the resume.

        Args:
            resume (BeautifulSoup): The parsed resume page.

        Returns:
            str: The position extracted from the resume.
        """

        position = resume.find("h2").text.replace("\xa0", "")
        return position

    @staticmethod
    def _match_skills(resume: BeautifulSoup, required_skills: list[str] = None) -> Union[str, set]:
        """
        Matches required skills with skills listed in the resume.

        Args:
            resume (BeautifulSoup): The parsed resume page.
            required_skills (list[str]): List of required skills.

        Returns:
            Union[str, set]: Matching skills found in the resume.
        """

        if not required_skills:
            return ResumeStatus.KEYWORDS_NOT_PROVIDED
        try:
            skills_elements = (
                resume.find("div", class_="wordwrap")
                .find_all("div", recursive=False)[3]
                .find_all("span", recursive=False)
            )
        except (IndexError, AttributeError):
            return ResumeStatus.SKILLS_SECTION_EMPTY
        if not skills_elements:
            return ResumeStatus.RESUME_AS_FILE

        skills = [skills_element.text.strip().lower() for skills_element in skills_elements]
        matching_skills = set()
        for required_skill in required_skills:
            for skill_in_resume in skills:
                if required_skill in skill_in_resume:
                    matching_skills.add(skill_in_resume)
        if len(matching_skills):
            return matching_skills
        return ResumeStatus.NO_SKILL_MATCHES

    @staticmethod
    def _match_keywords(resume: BeautifulSoup, required_keywords: list[str] = None) -> Union[str, set]:
        """
        Matches required keywords with text blocks in the resume.

        Args:
            resume (BeautifulSoup): The parsed resume page.
            required_keywords (list[str]): List of required keywords.

        Returns:
            Union[str, set]: Matching keywords found in the resume.
        """

        if not required_keywords:
            return ResumeStatus.KEYWORDS_NOT_PROVIDED
        try:
            resume_blocks = (
                resume.find("div", class_="wordwrap").find_all("div", recursive=False)[2].find_next_siblings()
            )
        except IndexError:
            return ResumeStatus.RESUME_NOT_FILLED
        if not resume_blocks:
            return ResumeStatus.RESUME_NOT_FILLED

        resume_text = [block.text.strip().lower() for block in resume_blocks]
        matching_keywords = set()
        for required_keyword in required_keywords:
            for text in resume_text:
                if required_keyword in text:
                    matching_keywords.add(required_keyword)
        if len(matching_keywords):
            return matching_keywords
        return ResumeStatus.NO_KEYWORD_MATCHES

    @staticmethod
    def _check_experience(resume: BeautifulSoup):
        """
        Checks if experience is mentioned in the resume.

        Args:
            resume (BeautifulSoup): The parsed resume page.

        Returns:
            str: Indicates if experience is mentioned in the resume.

        """

        experience = resume.find(text="Досвід роботи")
        return ResumeStatus.EXPERIENCE_PROVIDED if experience else ResumeStatus.EXPERIENCE_NOT_PROVIDED

    @staticmethod
    def _check_education(resume: BeautifulSoup):
        """
        Checks if education is mentioned in the resume.

        Args:
            resume (BeautifulSoup): The parsed resume page.

        Returns:
            str: Indicates if education is mentioned in the resume.
        """

        education = resume.find(text="Освіта")
        return ResumeStatus.EDUCATION_PROVIDED if education else ResumeStatus.EDUCATION_NOT_PROVIDED
