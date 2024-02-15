from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .dto import CriteriaDTO
from .exceptions import ResumeNotFoundError
from .parser import Parser


class RobotaUaParser(Parser):
    """
    Class for parsing resumes on robota.ua website.

    Attributes:
        browser (WebDriver): Instance of Selenium WebDriver.

    Methods:

    - __init__(): Initializes the WebDriver and navigates to the robota.ua resumes page.
    - set_params(params: CriteriaDTO): Sets the search parameters for searching resumes.
    - set_experience(experience: float | None) -> None: Sets the experience filter for searching resumes.
    - set_salary(salary_from: int | None, salary_to: int | None) -> None: Sets
      the experience filter for searching resumes.
    """

    def __init__(self):
        """
        Initializes the WebDriver and navigates to the robota.ua resumes page.
        """

        super().__init__()
        self.browser.get("https://robota.ua/employer/")
        sleep(5)

    def set_params(self, params: CriteriaDTO):
        """
        Sets the search parameters for searching resumes.

        Args:
            params (CriteriaDTO): Criteria data transfer object containing search parameters.

        Raises:
            ResumeNotFoundError: If the resume is not found.
        """

        search_elements_xpath = (
            "/html/body/app-root/div/alliance-employer-home-page/div/main/div[2]/"
            "alliance-employer-home-page-growth/alliance-employer-home-page-search/section/"
        )

        position_input = self.browser.find_element(
            By.XPATH, search_elements_xpath + "santa-suggest-input/santa-drop-down/div/div[1]/santa-input/div/input"
        )
        position_input.send_keys(params.position)
        sleep(1)

        if params.location:
            self.browser.find_element(
                By.XPATH,
                search_elements_xpath + "santa-suggest-input/santa-drop-down/div/div[1]/"
                "santa-input/div/div[2]/alliance-employer-home-page-filter-city/santa-drop-down",
            ).click()
            sleep(1)
            location_input = self.browser.find_element(
                By.XPATH,
                search_elements_xpath + "santa-suggest-input/santa-drop-down/div/div[1]/santa-input/div/div[2]/"
                "alliance-employer-home-page-filter-city/santa-drop-down/div/div[2]/div/div[1]/santa-input/div/input",
            )
            location_input.send_keys(params.location)
            sleep(1)
            self._try_find_element_by_xpath(
                search_elements_xpath + "santa-suggest-input/santa-drop-down/div/div[1]/santa-input/"
                "div/div[2]/alliance-employer-home-page-filter-city/santa-drop-down/div/div[2]/div/div[2]/div/ul/li[1]"
            ).click()

        search_candidates_button = self.browser.find_element(By.XPATH, search_elements_xpath + "santa-button")
        search_candidates_button.click()
        sleep(5)

        if not self._is_resume_found():
            raise ResumeNotFoundError

        self._is_resume_found()

        self.set_experience(params.experience)

        self.set_salary(params.salary_from, params.salary_to)

        self.browser.find_element(
            By.XPATH,
            "/html/body/div/div[3]/div/div/alliance-employer-cvdb-header-filters/section/div/"
            "alliance-employer-cvdb-desktop-filter-keyword/santa-suggest-input/santa-drop-down/"
            "div/div[1]/santa-input/div/div[2]/div/santa-button/button",
        ).click()
        sleep(2)

        self.get_resume_links()
        sleep(5)

    def set_experience(self, experience: float | None) -> None:
        """
        Sets the experience filter for searching resumes.

        Args:
            experience (float | None): The experience level to filter resumes. If None, no filter is applied.
        """

        experience_checkbox_xpath = (
            "/html/body/app-root/div/alliance-cv-list-page/main/article/div[2]/"
            "alliance-employer-cvdb-vertical-filters-sidebar/div/"
            "alliance-employer-cvdb-vertical-filters-panel/div/div[5]/div[2]/"
            "alliance-employer-cvdb-simple-experience/lib-checkbox-recursive-list/"
        )

        if experience is None:
            return

        self.browser.execute_script("window.scrollTo(0, 1000);")
        sleep(1)

        if experience == 0:
            self._try_find_element_by_xpath(experience_checkbox_xpath + "div[1]/santa-checkbox").click()
        if 0 < experience <= 1:
            self._try_find_element_by_xpath(experience_checkbox_xpath + "div[2]/santa-checkbox").click()
        sleep(1)
        if 1 <= experience <= 2:
            self._try_find_element_by_xpath(experience_checkbox_xpath + "div[3]/santa-checkbox").click()
        sleep(1)
        if 2 <= experience <= 5:
            self._try_find_element_by_xpath(experience_checkbox_xpath + "div[4]/santa-checkbox").click()
        sleep(1)
        if 5 <= experience <= 10:
            self._try_find_element_by_xpath(experience_checkbox_xpath + "div[5]/santa-checkbox").click()
        sleep(1)
        if experience >= 10:
            self._try_find_element_by_xpath(experience_checkbox_xpath + "div[6]/santa-checkbox").click()

        sleep(1)

    def set_salary(self, salary_from: int | None, salary_to: int | None) -> None:
        """
        Sets the salary filter for searching resumes.

        Args:
            salary_from (int | None): The minimum salary range.
            salary_to (int | None): The maximum salary range.
        """

        salary_inputs_xpath = (
            "/html/body/app-root/div/alliance-cv-list-page/main/article/div[2]/"
            "alliance-employer-cvdb-vertical-filters-sidebar/div/"
            "alliance-employer-cvdb-vertical-filters-panel/div/div[4]/"
            "alliance-employer-cvdb-simple-salary/lib-input-range/div/"
        )

        if salary_from:
            input_salary_from = self._try_find_element_by_xpath(salary_inputs_xpath + "div[1]/santa-input/div/input")
            input_salary_from.send_keys(salary_from)
            sleep(1)

        if salary_to:
            input_salary_to = self._try_find_element_by_xpath(salary_inputs_xpath + "div[2]/santa-input/div/input")
            input_salary_to.click()
            input_salary_to.send_keys(salary_to)

        sleep(1)

    def _is_resume_found(self) -> bool:
        """
        Checks if resumes are found based on the count displayed on the page.

        Returns:
        - bool: True if resumes are found, False otherwise.
        """

        resume_count = int(
            self.browser.find_element(
                By.XPATH,
                "/html/body/app-root/div/alliance-cv-list-page/main/article/div[1]/"
                "alliance-employer-cvdb-search-header/section/div/p/span",
            ).text
        )

        if resume_count:
            return True
        return False

    def get_resume_links(self) -> None:
        """
        Gets a link to all found resumes.

        This method iterates through the resume cards on the page and extracts the links to the resumes.
        It also handles pagination by clicking on the next page link until no more resumes are available.
        """

        cv_list_xpath = (
            "/html/body/app-root/div/alliance-cv-list-page/main/article/div[1]/div/alliance-employer-cvdb-cv-list/div/"
        )

        while True:
            resume_cards = self._try_find_element_by_xpath(cv_list_xpath + "div").find_elements(
                By.TAG_NAME, "alliance-employer-cvdb-cv-list-card"
            )
            for card in resume_cards:
                self.resume_links.append(card.find_element(By.TAG_NAME, "a").get_attribute("href"))

            pagination = self.browser.find_element(By.XPATH, cv_list_xpath + "nav/santa-pagination-with-links/div")
            current_page_number = int(pagination.find_element(By.CLASS_NAME, "active").text)
            try:
                pagination.find_element(By.LINK_TEXT, f"{current_page_number + 1}").click()
            except NoSuchElementException:
                return
            sleep(1)
