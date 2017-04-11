from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time
import json

# Put your email and password in these variables, make sure to have the quotation marks around them
yourEmailAddress = "budiryan@gmail.com"
yourPassword = "Bud1ry@n"

driver = webdriver.Chrome()

driver.get('https://www.quora.com/Can-someone-with-a-BTech-get-a-job-in-petroleum')
answers = driver.find_element_by_class_name('AnswerListDiv')
newQuestionHTML = answers.get_attribute("innerHTML")
soup = BeautifulSoup(newQuestionHTML, 'html.parser')
answer_divs = soup.find_all('div', class_='Answer')
for answer_div in answer_divs:
    print(answer_div)
    print('user is: ', answer_div.find('a', class_='user')['href'])
    the_answer = '' 
    answers_p = answer_div.find_all('p', class_='qtext_para')
    for answer in answers_p:
        the_answer += answer.get_text()
    print('answer is: ', the_answer)
    print('answer views: ', answer_div.find('span', class_='meta_num').get_text())
# get the answer itself
driver.close()


