from abc import ABCMeta, abstractmethod

import fake_useragent
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
    - _try_find_element_by_xpath(xpath: str) -> WebElement: Tries to find an element on the page by XPath.
    - _try_select_by_value(select: Select, value: str) -> None: Tries to select an option by value from a dropdown menu.
    """

    def __init__(self):
        """
        Initializes the WebDriver.
        """

        self.resume_links = []
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()
        self.user_agent = fake_useragent.UserAgent()
        self.resume_results = {}

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
