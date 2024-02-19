from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .dto import CriteriaDTO
from .interfaces import ResumeSearcherInterface

SALARY = {
    None: "0",
    1: "1",
    2000: "2",
    3000: "3",
    4000: "4",
    5000: "5",
    6000: "6",
    7000: "7",
    8000: "8",
    9000: "9",
    10000: "10",
    15000: "11",
    20000: "12",
    25000: "13",
    30000: "14",
    40000: "15",
    50000: "16",
    100000: "17",
}


class WorkUaResumeSearcher(ResumeSearcherInterface):
    """
    Class for searching resumes on work.ua website.

    Attributes:
        browser (WebDriver): Instance of Selenium WebDriver.

    Methods:

    - __init__(): Initializes the WebDriver and navigates to the work.ua resumes page.
    - set_params(params: CriteriaDTO): Sets the search parameters for searching resumes.
    - set_position_and_location(self, position: str, location: str = None) -> None: Set the position and
      location parameters, and search resume.
    - set_experience(experience: float | None) -> None: Sets the experience filter for searching resumes.
    - set_salary(salary_from: int | None, salary_to: int | None) -> None: Sets
      the experience filter for searching resumes.
    - get_resume_links(self) -> None: Gets a link to all found resumes.
    """

    def __init__(self):
        """
        Initializes the WebDriver and navigates to the work.ua resumes page.
        """

        super().__init__()
        self.browser.get("https://www.work.ua/resumes/")
        sleep(2)

    def set_params(self, params: CriteriaDTO):
        """
        Sets the search parameters for searching resumes.

        Args:
            params (CriteriaDTO): Criteria data transfer object containing search parameters.
        """

        self.set_position_and_location(params.position, params.location)

        self.set_salary(params.salary_from, params.salary_to)
        sleep(1)

        self.set_experience(params.experience)
        sleep(1)

        self.get_resume_links()
        self.browser.quit()

    def set_position_and_location(self, position: str, location: str = None) -> None:
        """
        Set the position and location parameters, and search resume.

        Args:
            position (str): The position or job title to search for.
            location (str, optional): The location where the job is based. Defaults to None.
        """

        position_input = self.browser.find_element(By.XPATH, "//*[@id='search']")
        position_input.send_keys(position)

        location_input = self.browser.find_element(By.XPATH, "//*[@id='searchform']/div/div/div[2]/input[1]")
        self.browser.execute_script("arguments[0].value = '';", location_input)
        location_input.send_keys(location)

        search_candidates_button = self.browser.find_element(By.XPATH, "//*[@id='sm-but']")
        search_candidates_button.click()
        sleep(3)

    def set_experience(self, experience: float | None) -> None:
        """
        Sets the experience filter for searching resumes.

        Args:
            experience (float | None): The experience level to filter resumes. If None, no filter is applied.
        """

        if experience is None:
            return
        if experience == 0:
            self._try_find_element_by_xpath("//*[@id='experience_selection']/div[1]/label/input").click()
        if 0 < experience <= 1:
            self._try_find_element_by_xpath("//*[@id='experience_selection']/div[2]/label/input").click()
        sleep(1)
        if 1 <= experience <= 2:
            self._try_find_element_by_xpath("//*[@id='experience_selection']/div[3]/label/input").click()
        sleep(1)
        if 2 <= experience <= 5:
            self._try_find_element_by_xpath("//*[@id='experience_selection']/div[4]/label/input").click()
        sleep(1)
        if experience >= 5:
            self._try_find_element_by_xpath("//*[@id='experience_selection']/div[5]/label/input").click()

    def set_salary(self, salary_from: int | None, salary_to: int | None) -> None:
        """
        Sets the salary filter for searching resumes.

        Args:
            salary_from (int | None): The minimum salary range.
            salary_to (int | None): The maximum salary range.
        """

        select_salary_from = Select(self._try_find_element_by_xpath("//*[@id='salaryfrom_selection']"))

        self._try_select_by_value(select=select_salary_from, value=SALARY[salary_from])
        sleep(1)

        select_salary_to = Select(self._try_find_element_by_xpath("//*[@id='salaryto_selection']"))

        self._try_select_by_value(select=select_salary_to, value=SALARY[salary_to])

    def get_resume_links(self) -> None:
        """
        Gets a link to all found resumes.

        This method iterates through the resume cards on the page and extracts the links to the resumes.
        It also handles pagination by clicking on the next page link until no more resumes are available.
        """

        while True:
            resume_cards = self._try_find_element_by_xpath("//*[@id='pjax-resume-list']").find_elements(
                By.CLASS_NAME, "resume-link"
            )
            for card in resume_cards:
                self._resume_links.append(card.find_element(By.TAG_NAME, "a").get_attribute("href"))

            pagination = self.browser.find_element(By.XPATH, "//*[@id='pjax-resume-list']/nav/ul[1]")
            try:
                pagination.find_element(By.CLASS_NAME, "add-left-default").find_element(By.TAG_NAME, "a").click()
            except NoSuchElementException:
                return
            sleep(1)
