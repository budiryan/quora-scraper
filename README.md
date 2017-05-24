# Quora Scraper
Easily gather answers from Quora. UROP1100 Project @ HKUST

## Features
- Crawl the answers of 1 specific user 
- Crawl the answers of a list of users (specified in txt file)
- Crawl the answers of the users which he / she follows

## Dependencies
- Python 3
- PhantomJS Webdriver
- Selenium
- BeautifulSoup

## Installation Guide (For Ubuntu 16.04 only)
- Update your system
```
sudo apt-get update
```
- Install various Linux dependencies:
```
sudo apt-get install build-essential libssl-dev libffi-dev python3-pip python3-dev
```
- Install __PhantomJS__ webdriver, follow the instructions <a href="https://gist.github.com/julionc/7476620">Click the link</a> 
- Git clone the repo
```
git clone https://github.com/budiryan/quora-scraper.git
```
- Go to the project folder
```
cd quora-scraper
```
- Create a virtual environment
```
virtualenv -p python3 env --no-site-packages
```
- Switch to a virtual environment
```
source env/bin/activate
```
- Install the Python dependencies
```
pip install -r requirements.txt
```

## Full Usage
Assuming all dependencies are installed and the you are in a python's virtual environment
```
Full usage: scrape.py [-h] (-u USERNAME | -v FILE CONTAINING USERNAMES) [-f]
```

## Examples
- Get the answers of username `Chris-Voss-6`
```
python scrape.py -u Chriss-Voss-6
```
- Get the answers of username `Chriss-Voss-6` together with other users that he follows
```
python scrape.py -u Chriss-Voss-6 -f
```
- Get the answers of usernames stored in `user_links.json`
```
python scrape.py -v user_links.json 
```
- Get the answers of usernames stored in `user_links.json` together with the users that they follow
```
python scrape.py -v user_links.json -f
```

## Getting the crawled data
All the crawled data are stored in: `result_answers.json` for answers and `results_users.json` for users.
