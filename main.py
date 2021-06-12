from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import json
import time
import re


class EasyApplyLinkedin:

    def __init__(self, data):
        """Paramater Initilization"""
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Chrome()

    def login_linkedin(self):
        """This function logs onto your personal linkedin profile"""
        # make driver go to linkedin url
        self.driver.get("https://www.linkedin.com/login/")

        # introduce our email and password and hit enter
        login_email = self.driver.find_element_by_name("session_key")
        login_email.clear()
        login_email.send_keys(self.email)

        login_password = self.driver.find_element_by_name("session_password")
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)# its simply hitting enter.

    def job_search(self):
        """This function goes to the Jobs section and looks for all the jobs that matches  the keyword  and location."""

        # go to the jobs section
        jobs_link = self.driver.find_element_by_link_text('İş İlanları')
        jobs_link.click()
        time.sleep(1)
        # introduce our keyword and location and hit enter
        search_keyword = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-keyword-id')]")
        search_keyword.clear()
        search_keyword.send_keys    (self.keywords)
        time.sleep(1)

        search_location = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-location-id')]")
        search_location.clear()
        search_location.send_keys(self.location)
        search_location.send_keys(Keys.RETURN)

    def filter(self):
        """This function filters all job by using easy apply."""
        # select all filters, click on easy apply and apply the filter.
        all_filters_button = self.driver.find_element_by_xpath\
            ("//button[@class='artdeco-pill artdeco-pill--slate artdec"
             "o-pill--2 artdeco-pill--choice ember-view search-reusables__filter-pill-button']"
             "[@aria-label='Kolay Başvuru filtre.']")
        all_filters_button.click()

    def find_offers(self):
        """This func finds all the offers through all the pages result of the search and filtering"""
        # find the total amount of results

        total_results = self.driver.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))
        print(total_results_int)
        time.sleep(1)

        # get results for the first page
        current_page = self.driver.current_url
        results = self.driver.find_elements_by_xpath(
            "//ul[@class='jobs-search-results__list list-style-none']/li[@data-occludable-entity-urn]"
        )
        print(len(results))
        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            scrollers = result.find_elements_by_xpath(
                "//div[@class='job-card-container ']"
            )
            for scroll in scrollers:
                self.submit_apply(scroll)

        # for each job add, submits application if no questions asked
        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements_by_xpath(
                    "//div[@class='full-width artdeco-entity-lockup__title ember-view']/a[@data-control-id]"
                )
            i = 0
            print(len(titles))
            for title in titles:

                print(i)
                if i >= len(titles)-1:
                    break
                else:
                    i = i + 1
                    self.submit_apply(title)
            break

        print(total_results_int)
        if total_results_int > 24:
            time.sleep(1)
            find_pages = self.driver.find_elements_by_xpath(
                "//ul[@class='artdeco-pagination__pages artdeco-pagination__pages--number']/li"
            )
            total_pages = find_pages[len(find_pages)-1].text
            print(total_pages)
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            print(total_pages_int)
            get_last_page = self.driver.find_element_by_xpath(
                "//button[@aria-label='{}. Sayfa']".format(str(total_pages_int))
            )
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=', 1)[1])# start urlde sayfadan onceki

            # go through all available pages and job offers and apply
            for page_number in range(25, total_jobs+25, 25):
                self.driver.get(current_page + '&start=' + str(page_number))
                time.sleep(3)
                results_ext = self.driver.find_elements_by_xpath(
                    "//ul[@class='jobs-search-results__list list-style-none']/li[@data-occludable-entity-urn]"
                )
                print(len(results_ext))
                for result_ext in results_ext:
                    hover = ActionChains(self.driver).move_to_element(result_ext)
                    hover.perform()
                    scrollers_ext = result_ext.find_elements_by_xpath(
                        "//div[@class='job-card-container']"
                    )
                    for scroll_ext in scrollers_ext:
                        self.submit_apply(scroll_ext)

                # for each job add, submits application if no questions asked
                for result_ext in results_ext:
                    hover = ActionChains(self.driver).move_to_element(result_ext)
                    hover.perform()
                    titles_ext = result_ext.find_elements_by_xpath(
                        "//div[@class='full-width artdeco-entity-lockup__title ember-view']/a[@data-control-id]"
                    )
                    i = 0
                    for title_ext in titles_ext:
                        print(i)
                        if i >= len(titles_ext) - 1:
                            break
                        else:
                            i = i + 1
                            self.submit_apply(title_ext)
                    break
        else:
            self.close_session()

    def submit_apply(self, job_ad):
        """This function submit the application for the job ad found"""
        print("you are applying to the position of: ", job_ad.text)
        job_ad.click()
        time.sleep(1)

        # click on the easy apply button, skip if already applied to the position
        try:
            in_apply = self.driver.find_element_by_xpath(
                "//button[@class='jobs-apply-button artdeco-button artdeco-button--3 artdeco-button--primary ember-view']"
            )
            in_apply.click()
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            pass

        # try to submit application if the application available
        try:
            submit = self.driver.find_element_by_xpath(
                "//button[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view']"
                "[@aria-label='Başvuruyu gönder']")
            submit.send_keys(Keys.RETURN)
            time.sleep(1)
            close_button = self.driver.find_element_by_xpath(
                "//button[@class='artdeco-modal__dismiss artdeco-button artdeco-button-"
                "-circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view']"
            )
            time.sleep(1)
            close_button.send_keys(Keys.RETURN)
            close_not = self.driver.find_element_by_xpath(
                "//button[@class='artdeco-toast-item__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']"
            )
            close_not.send_keys(Keys.RETURN)

        except NoSuchElementException:
            print("not direct application, going to next...")
            try:
                discard = self.driver.find_element_by_xpath("//button[@data-test-modal-close-btn]")
                discard.send_keys(Keys.RETURN)
                discard_confirm = self.driver.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass


    def close_session(self):
        """This function closes the actual session"""
        print('End of the session see you later')
        self.driver.close()

    def apply(self):
        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        bot.job_search()
        time.sleep(2)
        bot.filter()
        time.sleep(2)
        bot.find_offers()
        time.sleep(5)
        bot.close_session()




if __name__=="__main__":

     with open('config.json') as config_file:
            data = json.load(config_file)
     bot = EasyApplyLinkedin(data)
     bot.apply()



