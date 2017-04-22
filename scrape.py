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
# this is a dummy account
YOUR_EMAIL_ADDRESS = "bbudihaha@gmail.com"
YOUR_PASSWORD = "budihaha12345"

# Base URL
BASE_URL = 'https://www.quora.com'

# File paths
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
FILE_DIRECTORY = os.path.join(PROJECT_ROOT, 'user_links.json')
USER_OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'users.json')
ANSWER_OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'answers.json')


users_result = []
answers_result = []
following_list = []
# load a list of top writers on Quora for scraping
list_of_top_writers = json.load(open(FILE_DIRECTORY))


def login(driver):
    '''
    - Input: webdriver
    - desc: login to quora
    - Output: void
    '''
    wait = WebDriverWait(driver, 30)
    # Find sign-in by Google button and click it
    elem = driver.find_element_by_class_name("google_button")
    elem.click()
    time.sleep(8)
    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]

    # Switch to login popup
    time.sleep(2)
    driver.switch_to_window(window_after)

    # Enter Email address and submit
    emailInput = driver.find_element_by_xpath("//input[@id='Email']")
    print('Entering email...')
    emailInput.send_keys(YOUR_EMAIL_ADDRESS)
    driver.find_element_by_class_name("rc-button-submit").click()
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
    '''
    - input: webdriver, the writer's url
    - desc: Processes each user's credential and their answers to questions.
            Adding them to users.json and answers.json
    - output: void
    '''
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

    # have to get the info of each user
    try:
        name_and_signature = driver.find_element_by_class_name('ProfileNameAndSig')
        name = name_and_signature.find_element_by_class_name('user').text
        description = name_and_signature.find_element_by_class_name('UserCredential').text
        description = ''
        credentials_and_highlights = driver.find_element_by_class_name('AboutSection')
        education = credentials_and_highlights.find_element_by_class_name('SchoolCredentialListItem')
        education = re.sub(r'Studied at', '', education.find_element_by_class_name('UserCredential').text).strip()
        education = ''
        lives_in = credentials_and_highlights.find_element_by_class_name('LocationCredentialListItem')
        lives_in = re.sub(r'Lives in', '', lives_in.find_element_by_class_name('UserCredential').text).strip()
        lives_in = ''
        work = credentials_and_highlights.find_element_by_class_name('WorkCredentialListItem')
        work = work.find_element_by_class_name('UserCredential')
        work = ''

        num_answers = int(re.sub('\D', '', driver.find_element_by_class_name('AnswersNavItem').find_element_by_class_name('list_count').text))
        num_questions = int(re.sub('\D', '', driver.find_element_by_class_name('QuestionsNavItem').find_element_by_class_name('list_count').text))
        num_posts = int(re.sub('\D', '', driver.find_element_by_class_name('PostsNavItem').find_element_by_class_name('list_count').text))
        num_blogs = int(re.sub('\D', '', driver.find_element_by_class_name('BlogsNavItem').find_element_by_class_name('list_count').text))
        num_followers = int(re.sub('\D', '', driver.find_element_by_class_name('FollowersNavItem').find_element_by_class_name('list_count').text))
        num_following = int(re.sub('\D', '', driver.find_element_by_class_name('FollowingNavItem').find_element_by_class_name('list_count').text))
        num_topics = int(re.sub('\D', '', driver.find_element_by_class_name('TopicsNavItem').find_element_by_class_name('list_count').text))
    except:
        return

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
        print('AUTHOR ADDED: ', name)

    try:
        answers = driver.find_element_by_class_name('layout_3col_center')
        answers_soup = BeautifulSoup(answers.get_attribute("innerHTML").encode("utf-8"), 'html.parser')
        answers_links = answers_soup.find_all('a', class_='question_link')
        answers_links_href = []
    except:
        return

    for a in answers_links:
        answers_links_href.append(a['href'])
    # no answer at all, no need to collect anything
    if len(answers_links) == 0:
        return

    for a in answers_links_href:
        driver.get(urllib.parse.urljoin(BASE_URL, a))
        flag = 0
        t = time.time()
        while flag == 0:
            # Get question text
            # Process each answer, if an answer with the original author is found, break and finish
            try:
                answers = driver.find_element_by_class_name('AnswerListDiv')
            except:
                break
            try:
                question_text = driver.find_element_by_class_name('rendered_qtext').text.encode("utf-8")
                answers_html = answers.get_attribute("innerHTML").encode("utf-8")
                answers_soup = BeautifulSoup(answers_html, 'html.parser')
                answer_divs = answers_soup.find_all('div', class_='Answer')
            except:
                continue
            for answer_div in answer_divs:
                answer_author_object = answer_div.find('a', class_='user')
                if answer_author_object is None:
                    continue
                answer_author_link = 'https://www.quora.com' + answer_author_object['href']
                if answer_author_link == url:
                    answer_author = answer_div.find('a', class_='user')
                    answer_author = answer_author_object.get_text()
                    the_answer = answer_div.find('span', class_='rendered_qtext').get_text()
                    try:
                        answer_views = answer_div.find('span', class_='meta_num').get_text()
                        if 'k' in answer_views:
                            answer_views = re.sub(r'\D', '', answer_views)
                            answer_views = float(answer_views) * 1000
                        else:
                            answer_views = re.sub(r'\D', '', answer_views)
                        answer_views = int(answer_views)
                    except:
                        answer_views = 0
                    try:
                        # Get the number of upvotes of each answer
                        answer_upvotes = answer_div.find('span', class_='count').get_text()
                    except:
                        answer_upvotes = 0
                    if 'k' in answer_upvotes:
                        # answer_upvotes = answer_upvotes[0:len(answer_upvotes) - 1]
                        answer_upvotes = re.sub(r'\D', '', answer_upvotes)
                        answer_upvotes = float(answer_upvotes) * 1000
                    else:
                        answer_upvotes = re.sub(r'\D', '', answer_upvotes)
                    answer_upvotes = int(answer_upvotes)
                    # save to file
                    answers_result.append({
                        "answer": the_answer,
                        "author": answer_author,
                        "author_link": answer_author_link,
                        "views": answer_views,
                        "upvotes": answer_upvotes,
                        "question_title": question_text.decode("utf-8"),
                        "question_link": urllib.parse.urljoin(BASE_URL, a),
                    })
                    with open(ANSWER_OUTPUT_FILE, 'w') as f:
                        json.dump(answers_result, f, indent=4)
                        print('ANSWER ADDED: ', question_text.decode("utf-8"))
                        flag = 1
                    break
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            if (time.time() - t) > 20:
                print('PROCESSED TOOK TOO LONG, BREAK!')
                break	


def process_following(driver, writer_url):
    '''
    - Input: webdriver and a writer's url
    - Desc: Get all the users that a user follow and add it to the list
    - Output: void
    '''
    print('now processing following...')
    url = urllib.parse.urljoin(BASE_URL, writer_url + '/following')
    driver.get(url)
    # do infinite scrolling to get all the followers
    stuck_value = 0
    # have to scroll until the end of page
    try:
        current_html = driver.find_element_by_class_name('ContentWrapper')
    except:
        # user has no follower! just break
        break
    current_html = current_html.get_attribute('innerHTML')

    while(True):
        prev_html = current_html
        # scroll to the end of page and set some delay --> to get the users in the following section
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        current_html = driver.find_element_by_class_name('ContentWrapper')
        current_html = current_html.get_attribute("innerHTML")
        time.sleep(3)

        if stuck_value > 3:
            break

        if prev_html == current_html:
            # if after scrolling nothing changes, that means it is stuck
            stuck_value += 1
            print('stuck value: ', stuck_value)

    users = driver.find_element_by_class_name('layout_3col_center')
    users_soup = BeautifulSoup(users.get_attribute("innerHTML").encode("utf-8"), 'html.parser')
    users_links = users_soup.find_all('a', class_='user')
    for a in users_links:
        if (a not in list_of_top_writers) and (a not in following_list):
            following_list.append(a['href'])


def main():
    # Initialize webdriver
    driver = webdriver.PhantomJS()
    driver.maximize_window()
    driver.get('https://www.quora.com/')

    # Login to Quora to scrape more information
    login(driver)

    count_author = 0
    # Loop through all popular writers
    for writer_url in list_of_top_writers:
        process_user(driver, writer_url)
        process_following(driver, writer_url)
        count_author += 1
        print('Authors processed so far: ', count_author)

    print('now processing what is inside the following_list')
    # Loop through all the following list
    for writer_url in following_list:
        process_user(driver, writer_url)

    # finish operation
    driver.close()


if __name__ == '__main__':
    main()
