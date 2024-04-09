from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import re


class EasyApplyLinkedin:

    def __init__(self, data):
        """Parameter Initialization"""

        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Chrome(data['driver_path'])

    def login_linkedin(self):
        """Function to login into Linkedin page"""
        # make driver open linkedin page
        self.driver.get("https://ca.linkedin.com/")
        time.sleep(2)
        # make driver type login credentials and press enter
        login_email = self.driver.find_element_by_name("session_key")
        login_email.clear()
        login_email.send_keys(self.email)
        login_password = self.driver.find_element_by_name("session_password")
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)

    def job_search(self):
        """Function to click on Job key and search based on Job title"""
        time.sleep(5)
        search_box = self.driver.find_element_by_id("global-nav-search")
        search_box.click()  # 1. Click on the search element to activate the next element state of text input
        time.sleep(2)
        search_box = self.driver.find_element_by_class_name("search-global-typeahead__input")
        search_box.send_keys(self.keywords)
        search_box.send_keys(Keys.RETURN)  # 2. Enter the keyword " job title "

    def filter(self):
        """Function filters the jobs based on easy apply feature"""
        time.sleep(5)
        jobs_button_click = self.driver.find_element_by_xpath('//button[text()="Jobs"]')
        jobs_button_click.click()

        time.sleep(3)
        all_filters_button = self.driver.find_element_by_xpath('//button[text()="All filters"]')
        all_filters_button.click()

        time.sleep(1)
        location_halifax = self.driver.find_element_by_xpath('//label[@for="advanced-filter-populatedPlace-101728226"]')
        location_halifax.click()

        time.sleep(1)
        easy_apply_button = self.driver.find_element_by_class_name('search-reusables__advanced-filters-binary-toggle')
        easy_apply_button.click()

        time.sleep(1)
        experience_level = self.driver.find_element_by_xpath('//label[@for="advanced-filter-experience-2"]')
        experience_level.click()

        time.sleep(1)
        show_results = self.driver.find_element_by_xpath(
            '//button[starts-with(@class,"reusable-search-filters-buttons")]')
        show_results.click()

    def find_offers(self):
        time.sleep(3)

        """find total no of jobs if there is more than 24"""
        total_results = self.driver.find_element_by_class_name("jobs-search-results-list__subtitle")
        total_results_int = int(total_results.text.split(' ', 1)[0].replace(',', ''))
        print(total_results_int)

        time.sleep(2)
        current_page = self.driver.current_url
        results = self.driver.find_elements_by_class_name(
            'ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item')

        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements_by_class_name(
                'full-width.artdeco-entity-lockup__title.ember-view')
            for title in titles:
                self.submit_apply(title)

        # if there is more than 1 page
        if total_results_int > 24:
            time.sleep(2)

            # find the last page and construct the url of each page based on the total amount of pages
            find_pages = self.driver.find_elements_by_class_name(
                'artdeco-pagination__indicator.artdeco-pagination__indicator--number.ember-view')
            total_pages = find_pages[len(find_pages) - 1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            time.sleep(2)
            get_last_page = self.driver.find_element_by_xpath(
                '//button[@aria-label="Page '+str(total_pages_int)+'"]')
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split("start=", 1)[1])

            # go through all the jobs and apply
            for page_number in range(25, total_jobs + 25, 25):
                self.driver.get(current_page + "&start=" + str(page_number))
                time.sleep(2)
                results_ext = self.driver.find_elements_by_class_name(
                    'ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item')
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements_by_class_name(
                        'full-width.artdeco-entity-lockup__title.ember-view')
                    for title_ext in titles_ext:
                        self.submit_apply(title_ext)
        else:
            self.close_session()

    def submit_apply(self, job_ad):
        """This function submits application for each job clicked with no extra questions asked"""
        print("You are applying to the position of:", job_ad.text)
        job_ad.click()
        time.sleep(2)

        # click on the easy apply button, skip if already applied
        try:
            in_apply = self.driver.find_element_by_class_name('jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view')
            in_apply.click()
        except NoSuchElementException:
            print("You've already to this position, moving to next one...")
            pass
        time.sleep(1)

        # try to submit the application
        try:
            submit = self.driver.find_element_by_xpath('//button[@aria-label="Submit application"]')
            submit.send_keys(Keys.RETURN)
        except NoSuchElementException:
            print("Not direct application, going to next one....")
            try:
                discard = self.driver.find_element_by_xpath('//button[@data-test-modal-close-btn]')
                discard.click()
                time.sleep(1)
                discard_confirm = self.driver.find_element_by_xpath('//button[@data-test-dialog-secondary-btn]')
                discard_confirm.click()
            except NoSuchElementException:
                pass
            time.sleep(1)

    def close_session(self):
        """Close the session"""

        print("End of the session, see you later....")
        self.driver.close()

    def apply(self):

        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(2)
        self.find_offers()
        time.sleep(2)
        # self.close_session()


if __name__ == "__main__":
    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.apply()
