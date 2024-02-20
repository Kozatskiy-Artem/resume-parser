from abc import ABCMeta, abstractmethod

import fake_useragent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from .constants import ResumeStatus
from .dto import CriteriaDTO
from .exceptions import ResumeNotFoundError


class ResumeSearcherInterface(metaclass=ABCMeta):
    """
    Abstract base class for searching resumes.

    Attributes:
    - browser (WebDriver): Instance of Selenium WebDriver.

    Methods:

    - __init__(): Initializes the WebDriver.
    - set_params(params: CriteriaDTO): Abstract method to set the search parameters for searching resumes.
    - _try_find_element_by_xpath(xpath: str) -> WebElement: Tries to find an element on the page by XPath.
    - _try_select_by_value(select: Select, value: str) -> None: Tries to select an option by value from a dropdown menu.
    """

    def __init__(self):
        """
        Initializes the WebDriver.
        """

        self._resume_links = []
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()

    @property
    def resume_links(self):
        return self._resume_links

    @abstractmethod
    def set_params(self, params: CriteriaDTO):
        """
        Abstract method to set the search parameters for searching resumes.

        Args:
            params (CriteriaDTO): Criteria data transfer object containing search parameters.
        """
        pass

    def _try_find_element_by_xpath(self, xpath: str) -> WebElement:
        """
        Tries to find an element on the page by XPath.

        Args:
            xpath (str): XPath expression to locate the element.

        Returns:
            WebElement: The located web element.

        Raises:
            ResumeNotFoundError: If the element is not found or not enabled.
        """
        try:
            element = self.browser.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            raise ResumeNotFoundError()
        else:
            if not element.is_enabled():
                raise ResumeNotFoundError()
            return element

    @staticmethod
    def _try_select_by_value(select: Select, value: str) -> None:
        """
        Tries to select an option by value from a dropdown menu.

        Args:
            select (Select): The dropdown menu element.
            value (str): The value to select from the dropdown menu.

        Raises:
            ResumeNotFoundError: If the option is not found.
        """
        try:
            select.select_by_value(value)
        except NoSuchElementException:
            raise ResumeNotFoundError()


class ResumeParserInterface(metaclass=ABCMeta):
    """
    An abstract base class for parsing resumes.

    Attributes:
        user_agent (fake_useragent.UserAgent): An instance of the UserAgent class for generating random user agents.
        resume_results (dict): A dictionary to store parsed resume results.

    Methods:
        __init__(): Initializes the ResumeParserInterface class.
        pars_resumes(resume_links: list[str], params: CriteriaDTO) -> None: Abstract method to parse resumes.
    """

    def __init__(self):
        self.user_agent = fake_useragent.UserAgent()
        self.resume_results = {}

    @abstractmethod
    def pars_resumes(self, resume_links: list[str], params: CriteriaDTO) -> None:
        """
        Abstract method to parse resumes.

        Args:
            resume_links (list[str]): A list of URLs pointing to resumes to be parsed.
            params (CriteriaDTO): An instance of the CriteriaDTO class containing search parameters.

        This method should be implemented by subclasses to parse resumes and extract relevant information.
        """
        pass

    @staticmethod
    def _get_resume_points(resume: dict):
        """
        Simple system for evaluating relevant resumes.
        Calculate the points of a resume based on matching keywords, experience, and education.

        Args:
            resume (dict): The resume data dictionary.

        Returns:
            int: The total points calculated for the resume.
        """

        points = 0
        if isinstance(resume["matching_keywords"], set):
            points = len(resume["matching_keywords"])
        if resume.get("experience") == ResumeStatus.EXPERIENCE_PROVIDED:
            points += 1
        if resume.get("education") == ResumeStatus.EDUCATION_PROVIDED:
            points += 1
        return points

    def get_relevant_resumes(self, max_count: int):
        """
        Retrieves the most relevant resumes based on their points.

        Args:
            max_count (int): The maximum number of relevant resumes to retrieve.

        Returns:
            dict: A dictionary containing the top relevant resumes and their corresponding
            information, sorted by relevance.
            If the maximum count is greater than or equal to the total number of resumes,
            the function returns all sorted resumes. Otherwise, it returns only the top resumes.
        """

        sorted_resume_results = sorted(self.resume_results.items(), key=lambda x: x[1]['points'], reverse=True)

        if max_count >= len(sorted_resume_results):
            return dict(sorted_resume_results)
        return dict(sorted_resume_results[:max_count])
