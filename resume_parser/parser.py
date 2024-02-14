from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from .dto import CriteriaDTO
from .exceptions import ResumeNotFoundError


class Parser(metaclass=ABCMeta):
    """
    Abstract base class for parsing resumes.

    Attributes:
    - browser (WebDriver): Instance of Selenium WebDriver.

    Methods:

    - __init__(): Initializes the WebDriver.
    - set_params(params: CriteriaDTO): Abstract method to set the search parameters for searching resumes.
    - set_experience(experience: float | None) -> None: Abstract method to set
      the experience filter for searching resumes.
    - set_salary(salary_from: int | None, salary_to: int | None) -> None: Abstract method to set
      the salary filter for searching resumes.
    - _try_find_element_by_xpath(xpath: str) -> WebElement: Tries to find an element on the page by XPath.
    - _try_select_by_value(select: Select, value: str) -> None: Tries to select an option by value from a dropdown menu.
    """

    def __init__(self):
        """
        Initializes the WebDriver.
        """

        self.browser = webdriver.Chrome()
        self.browser.maximize_window()

    @abstractmethod
    def set_params(self, params: CriteriaDTO):
        """
        Abstract method to set the search parameters for searching resumes.

        Args:
            params (CriteriaDTO): Criteria data transfer object containing search parameters.
        """
        pass

    @abstractmethod
    def set_experience(self, experience: float | None) -> None:
        """
        Abstract method to set the experience filter for searching resumes.

        Args:
            experience (float | None): The experience level to filter resumes. If None, no filter is applied.
        """
        pass

    @abstractmethod
    def set_salary(self, salary_from: int | None, salary_to: int | None) -> None:
        """
        Abstract method to set the salary filter for searching resumes.

        Args:
            salary_from (int | None): The minimum salary range. If None, no filter is applied.
            salary_to (int | None): The maximum salary range. If None, no filter is applied.
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
