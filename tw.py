import csv
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions


def get_tweet_data(card):
    username = card.find_element_by_xpath('.//span').text
    handle = card.find_element_by_xpath('.//span[contains(text(),"@")]').text
    try:
        postdate = card.find_element_by_xpath(
            './/time').get_attribute('datetime')
    except NoSuchElementException:
        return
    comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    text = comment + responding
    tweet = (username, handle, postdate, text)
    return tweet


options = EdgeOptions()
options.use_chromium = True
driver = Edge(options=options)

driver.get('https://www.twitter.com/login')
driver.implicitly_wait(30)


username = driver.find_element_by_xpath(
    '//input[@name="session[username_or_email]"]')
username.send_keys('mahippruthi@gmail.com')
my_password = getpass()

password = driver.find_element_by_xpath('//input[@name="session[password]"]')
password.send_keys(my_password)
password.send_keys(Keys.RETURN)

search_input = driver.find_element_by_xpath(
    '//input[@aria-label="Search query"]')
search_input.send_keys('#Urgent_help_required')
search_input.send_keys(Keys.RETURN)

driver.find_element_by_link_text('Latest').click()

data = []
tweet_ids = set()
last_position = driver.execute_script("return window.pageYOffset;")
scrolling = True

while scrolling:
    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for card in page_cards[-15:]:
        tweet = get_tweet_data(card)
        if tweet:
            tweet_id = ''.join(tweet)
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                data.append(tweet)
    scroll_attempt = 0
    while True:
        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        sleep(1)
        curr_position = driver.execute_script("return window.pageYOffset;")
        if last_position == curr_position:
            scroll_attempt += 1
            if scroll_attempt >= 3:
                scrolling = False
                break
            else:
                sleep(2)
        else:
            last_position = curr_position
            break


with open('tweetscovid.csv', 'w', newline='', encoding='utf-8') as f:
    header = ['UserName', 'Handle', 'Timestamp', 'Text']
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)
