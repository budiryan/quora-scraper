from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import urllib
import time
import json
import re
import os


# Put your email and password in these variables, make sure to have the quotation marks around them
YOUR_EMAIL_ADDRESS = "bbudihaha@gmail.com"
YOUR_PASSWORD = "budihaha12345"

# Base URL
BASE_URL = 'https://www.quora.com'

# File path
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
FILE_DIRECTORY = os.path.join(PROJECT_ROOT, 'user_links.json')
USER_OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'users.json')
ANSWER_OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'answers.json')


users_result = []
answers_result = []


def login(driver):
    wait = WebDriverWait(driver, 30)
    # Find sign-in by Google button and click it
    elem = driver.find_element_by_class_name("google_button")
    elem.click()
    time.sleep(5)
    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]

    # Switch to login popup
    time.sleep(2)
    driver.switch_to_window(window_after)

    # Enter Email address and submit
    emailInput = driver.find_element_by_xpath("//input[@id='Email']")
    print('Entering email...')
    emailInput.send_keys(YOUR_EMAIL_ADDRESS)
    emailSubmit = driver.find_element_by_class_name("rc-button-submit").click()
    time.sleep(4)

    wait.until(EC.presence_of_element_located((By.ID, "Passwd")))

    # Enter Password and submit
    pwInput = driver.find_element_by_xpath("//input[@id='Passwd']")
    print('Entering password...')
    try:
        pwInput.send_keys(YOUR_PASSWORD)
    except:
        print("FAIL")
    time.sleep(4)

    pwSubmit = driver.find_element_by_id("signIn").click()

    time.sleep(5)

    # need to switch to first window again
    driver.switch_to_window(window_before)


def process_user(driver, writer_url):
    url = urllib.parse.urljoin(BASE_URL, writer_url)
    driver.get(url)
    # have to scroll until the end of page
    current_html = driver.find_element_by_class_name('ContentWrapper')
    current_html = current_html.get_attribute('innerHTML')
    stuck_value = 0

    while(True):
        prev_html = current_html
        # scroll to the end of page and set some delay --> to get the questions
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        current_html = driver.find_element_by_class_name('ContentWrapper')
        current_html = current_html.get_attribute("innerHTML")
        time.sleep(5)

        if stuck_value > 3:
            break

        if prev_html == current_html:
            # if after scrolling nothing changes, that means it is stuck
            stuck_value += 1

        print('stuck_value: ', stuck_value)

    # have to get the info of each user
    name_and_signature = driver.find_element_by_class_name('ProfileNameAndSig')
    name = name_and_signature.find_element_by_class_name('user').text
    try:
        description = name_and_signature.find_element_by_class_name('UserCredential').text
    except:
        description = ''
    credentials_and_highlights = driver.find_element_by_class_name('AboutSection')
    try:
        education = credentials_and_highlights.find_element_by_class_name('SchoolCredentialListItem')
        education = re.sub(r'Studied at', '', education.find_element_by_class_name('UserCredential').text).strip()
    except:
        education = ''
    try:
        lives_in = credentials_and_highlights.find_element_by_class_name('LocationCredentialListItem')
        lives_in = re.sub(r'Lives in', '', lives_in.find_element_by_class_name('UserCredential').text).strip()
    except:
        lives_in = ''
    try:
        work = credentials_and_highlights.find_element_by_class_name('WorkCredentialListItem')
        work = work.find_element_by_class_name('UserCredential')
    except:
        work = ''

    num_answers = int(re.sub(',', '', driver.find_element_by_class_name('AnswersNavItem').find_element_by_class_name('list_count').text))
    num_questions = int(re.sub(',', '', driver.find_element_by_class_name('QuestionsNavItem').find_element_by_class_name('list_count').text))
    num_posts = int(re.sub(',', '', driver.find_element_by_class_name('PostsNavItem').find_element_by_class_name('list_count').text))
    num_blogs = int(re.sub(',', '', driver.find_element_by_class_name('BlogsNavItem').find_element_by_class_name('list_count').text))
    num_followers = int(re.sub(',', '', driver.find_element_by_class_name('FollowersNavItem').find_element_by_class_name('list_count').text))
    num_following = int(re.sub(',', '', driver.find_element_by_class_name('FollowingNavItem').find_element_by_class_name('list_count').text))
    num_topics = int(re.sub(',', '', driver.find_element_by_class_name('TopicsNavItem').find_element_by_class_name('list_count').text))

    users_result.append({
        'author_name': name,
        'auhtor_url': url,
        'description': description,
        'education': education,
        'lives_in': lives_in,
        'num_answers': num_answers,
        'num_questions': num_questions,
        'num_posts': num_posts,
        'num_blogs': num_blogs,
        'num_followers': num_followers,
        'num_following': num_following,
        'num_topics': num_topics
    })
    with open(USER_OUTPUT_FILE, 'w') as f:
        json.dump(users_result, f, indent=4)

    answers = driver.find_element_by_class_name('layout_3col_center')

    answer_links = answers.find_elements_by_class_name('answer_text')
    # no answer at all, no need to collect anything
    if len(answer_links) == 0:
        return
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    for answer_link in answer_links:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(5)
        answer_link.find_element_by_class_name('more_link').click()
        time.sleep(5)
        the_modal = driver.find_element_by_xpath("//*[@class='modal_overlay feed_desktop_modal']")
        the_modal_soup = BeautifulSoup(the_modal.get_attribute('innerHTML').encode('utf-8'), 'html.parser')

        # Collect the question string and the link
        try:
            answer_title_link = urllib.parse.urljoin(BASE_URL, the_modal_soup.find('a', class_='question_link')['href'])
        except:
            print(the_modal.get_attribute('innerHTML'))

        answer_title = the_modal_soup.find('span', class_='question_text').text

        # Collect the answer
        answer = ''
        answer_html = the_modal_soup.find_all('p', class_='qtext_para')
        for a in answer_html:
            answer += a.text

        # Find the number of upvote for this answer
        num_upvote = int(the_modal_soup.find('span', class_='count').text)

        close_button = the_modal.find_element_by_class_name('modal_fixed_close')
        close_button.click()
        answers_result.append({
            'title': answer_title,
            'title_url': answer_title_link,
            'author_url': url,
            'answer': answer,
            'num upvote': num_upvote
        })
        with open(ANSWER_OUTPUT_FILE, 'w') as f:
            json.dump(answers_result, f, indent=4)


def main():
    # Initialize webdriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://www.quora.com/')

    # Login to Quora to scrape more information
    login(driver)

    # load a list of top writers on Quora for scraping
    list_of_top_writers = json.load(open(FILE_DIRECTORY))

    # Loop through all popular writers
    for writer_url in list_of_top_writers:
        process_user(driver, writer_url)

    # finish operation
    driver.close()


if __name__ == '__main__':
    main()
