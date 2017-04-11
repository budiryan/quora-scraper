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


def login(driver):
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

            if stuck_value > 5:
                break

            if prev_html == current_html:
                # if after scrolling nothing changes, that means it is stuck
                stuck_value += 1

            print('stuck_value: ', stuck_value)

    driver.close()

    # # find total number of questions
    # numberOfQuestionsDiv = driver.find_element_by_class_name('TopicQuestionsStatsRow').get_attribute("innerHTML")
    # numberOfQuestionsSoup = BeautifulSoup(numberOfQuestionsDiv, 'html.parser').strong.text
    # numberOfQuestions = HTMLNumberToPlain(numberOfQuestionsSoup)

    # # get div with all questions
    # questionDiv = driver.find_element_by_class_name('layout_2col_main')
    # questionHTML = questionDiv.get_attribute("innerHTML")
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # # Allow time to update page
    # time.sleep(5)

    # # get questions again
    # questionDiv = driver.find_element_by_class_name('layout_2col_main')
    # newQuestionHTML = questionDiv.get_attribute("innerHTML")

    # if newQuestionHTML == questionHTML:
    #     questionsScrapedSoFar = numberOfQuestions
    # else:
    #     soup = BeautifulSoup(newQuestionHTML.encode("utf-8"), 'html.parser')
    #     questionsScrapedSoFarSoup = soup.find_all('a', class_= 'question_link')
    #     questionsScrapedSoFar=0
    #     for q in questionsScrapedSoFarSoup:
    #         questionsScrapedSoFar+=1

    # repeatCount = 0
    # # Keep checking if there are new questions after scrolling down
    # while (questionsScrapedSoFar < numberOfQuestionsToScrape):
    # # while (True):
    #     questionHTML = newQuestionHTML
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     time.sleep(5)
    #     questionDiv = driver.find_element_by_class_name('layout_2col_main')
    #     newQuestionHTML = questionDiv.get_attribute("innerHTML")

    #     if newQuestionHTML != questionHTML:
    #         # Each time you scroll down, 20 more are added
    #         questionsScrapedSoFar += 20
    #         repeatCount = 0
    #     else:
    #         # print("STALLING!")
    #         repeatCount += 1

    #     if questionsScrapedSoFar % 100 == 0:
    #         print("Questions scraped: ", questionsScrapedSoFar)

    #     # if repeatCount > 40:
    #     #     print("Quora stalled after scraping " + str(questionsScrapedSoFar) + " questions")
    #     #     break


    # finalQuestions = questionDiv.get_attribute("innerHTML").encode("utf-8")

    # # Get questions as strings
    # soup = BeautifulSoup(finalQuestions, 'html.parser')
    # questions = soup.find_all('a', class_= 'question_link')
    # questionLinks = []
    # for q in questions:
    #     questionLinks.append(q['href'])

    # print("NUMBER OF QUESTIONS DISCOVERED: ", len(questionLinks))
    # # Visit each question page to get stats
    # questionStats = []
    # questionsScrapedSoFar = 0

    # print("parsing each question...")
    # repeatCount = 0
    # for qLink in questionLinks:
    #     driver.get('https://www.quora.com' + qLink)
    #     try:
    #         oldAnsHtml = driver.find_element_by_class_name('content_page_feed_offset')
    #     except:
    #         # either no answer yet, the link is broken, just get the question text
    #         # Get question text
    #         try:
    #             questionsText = driver.find_element_by_class_name('rendered_qtext').text.encode("utf-8")
    #         except:
    #             questionsText = None
    #         try:
    #             # Get number of followers
    #             numFollowers = int(driver.find_element_by_class_name('FollowerListModalLink').text.split(" ")[0])
    #         except:
    #             numFollowers = 0
    #         try:
    #             # Get number of views
    #             numViews = int(driver.find_element_by_class_name('ViewsRow').text.split(" ")[0].replace(",",""))
    #         except: 
    #             numViews = 0
    #         questionStats.append(
    #             {
    #                 "Answer": None,
    #                 "Answer author": None,
    #                 "Author link": None,
    #                 "Answer views": None,
    #                 "Answer upvotes": None,
    #                 "Question": questionsText,
    #                 "Question link": 'https://www.quora.com' + qLink,
    #                 "Question Followers": numFollowers,
    #                 "Question views": numViews  
    #             })
    #         continue

    #     # loop here first until getting all the possible
    #     while(True):
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         time.sleep(3)
    #         newAnsHtml = driver.find_element_by_class_name('content_page_feed_offset')
    #         if oldAnsHtml == newAnsHtml:
    #             repeatCount += 1
    #         else:
    #             repeatCount = 0
    #             oldAnsHtml = newAnsHtml
    #         if repeatCount > 2:
    #             # Finish scrolling down
    #             # print("Finished scrolling down: ", qLink)
    #             break

    #     answers = driver.find_element_by_class_name('AnswerListDiv')
        
    #     # Get question text
    #     questionsText = driver.find_element_by_class_name('rendered_qtext').text.encode("utf-8")  
    #     # Get number of followers of this question
    #     numFollowers = int(driver.find_element_by_class_name('FollowerListModalLink').text.split(" ")[0])
    #     # Get number of views for this question
    #     numViews = int(driver.find_element_by_class_name('ViewsRow').text.split(" ")[0].replace(",",""))
    #     # Get number of answers
    #     numOfAnswers = 0

    #     # Need to get number of answers
    #     # try:
    #     #     numberOfAnswersText = driver.find_element_by_class_name('answer_count').text.split(" ")[0].replace(',','').replace('+', '')
    #     # except:
    #     #     numberOfAnswersText = 1

    #     if answers is not None:
    #         newQuestionHTML = answers.get_attribute("innerHTML")
    #         soup = BeautifulSoup(newQuestionHTML, 'html.parser')
    #         answer_divs = soup.find_all('div', class_='Answer')
    #         answer_count = 0
    #         for answer_div in answer_divs:
    #             # TODO: Continue
    #             try:
    #                 answer_author_object = answer_div.find('a', class_='user')
    #                 answer_author_link = 'https://www.quora.com' + answer_author_object['href']
    #                 answer_author = answer_div.find('a', class_='user')
    #                 answer_author = answer_author_object.get_text()
    #                 the_answer = '' 
    #                 answers_p = answer_div.find_all('p', class_='qtext_para')
    #                 for answer in answers_p:
    #                     the_answer += answer.get_text()
    #                 answer_views = answer_div.find('span', class_='meta_num').get_text()
    #                 if 'k' in answer_views:
    #                     answer_views = answer_views[0:len(answer_views)-1]
    #                     answer_views = float(answer_views) * 1000
    #                 answer_views = int(answer_views)
    #                 # Get the number of upvotes of each answer
    #                 answer_upvotes = answer_div.find('span', class_='count').get_text()
    #                 if 'k' in answer_upvotes:
    #                     answer_upvotes = answer_upvotes[0:len(answer_upvotes)-1]
    #                     answer_upvotes = float(answer_upvotes) * 1000
    #                 answer_upvotes = int(answer_upvotes)
    #                 questionStats.append({
    #                     "Answer": the_answer,
    #                     "Answer author": answer_author,
    #                     "Author link": answer_author_link,
    #                     "Answer views": answer_views,
    #                     "Answer upvotes": answer_upvotes,
    #                     "Question": str(questionsText), 
    #                     "Question link": 'https://www.quora.com' + qLink,
    #                     "Question Followers": numFollowers,
    #                     "Question views": numViews  
    #                     })
    #                 answer_count += 1
    #             except:
    #                 continue
    #         # print("num of answers for: ", qLink," is: ", answer_count)
    #     # No answer yet
    #     else:
    #         questionStats.append(
    #             {
    #                 "Answer": None,
    #                 "Answer author": None,
    #                 "Author link": None,
    #                 "Answer views": None,
    #                 "Answer upvotes": None,
    #                 "Question": questionsText, 
    #                 "Question link": 'https://www.quora.com' + qLink,
    #                 "Question Followers": numFollowers,
    #                 "Question views": numViews
    #             })


    #     questionsScrapedSoFar += 1
    #     if questionsScrapedSoFar % 20 == 0:
    #         print("Processed questions: ", questionsScrapedSoFar)
    #         print("Saving to file...")
    #         with open('result2.json', 'w') as file:
    #             json.dump(questionStats, file, indent=0)


    # # Close the window, finished operation
    # driver.close()


if __name__ == '__main__':
    main()