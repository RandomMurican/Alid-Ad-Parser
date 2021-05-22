import selenium
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

STREET = '7051 Sleep Hollow Drive'
CITY = 'Southaven'
STATE = 'MS'
ZIPCODE = 38637


class Item:
    def __init__(self, name: str, price: str):
        self.name = name
        self.price = price

    def __str__(self):
        return self.name + ' @ ' + self.price


# Open the browser and go to Aldi's website
browser = webdriver.Chrome()
browser.get('https://www.aldi.us/en/weekly-specials/our-weekly-ads/')
info = []

# Search by zipcode
browser.switch_to.frame("shopLocalPlatformFrame")
element = browser.find_element_by_id("locationInput")
element.send_keys(ZIPCODE)
sleep(0.2)  # It hung on me once for some reason, so just to be safe
element.send_keys(Keys.ENTER)
sleep(2)

# Click on the specified result
found = False
stores = browser.find_elements_by_class_name("nuepselectstorebtns")
for store in stores:
    if store.get_attribute("aria-label") == f'Select Aldi at {STREET} {CITY}, {STATE}':
        store.click()
        found = True
        break
if not found:
    raise ValueError('Store not found.')

# Go to the current ad
for element in browser.find_elements_by_tag_name("div"):
    if element.get_attribute("aria-label") == "Weekly Ad":
        element.click()
        break
sleep(2)

# Find all the items on each page
mapcount = len(browser.find_elements_by_tag_name("map"))
print(f'{mapcount} pages found')
for m in range(mapcount):
    currentmap = browser.find_elements_by_tag_name("map")[m]
    areacount = len(currentmap.find_elements_by_tag_name("area"))
    print(f'Page {m + 1} has {areacount} items on it.')
    for a in range(areacount):
        areas = browser.find_elements_by_tag_name("map")[m].find_elements_by_tag_name("area")
        outside_label = areas[a].get_attribute("aria-label")
        print(f' Working on {outside_label}', end='')
        # Click item picture to force a popup
        while True:
            print('.', end="")
            try:
                areas[a].click()
                break
            except:
                sleep(1)

        # Click on item details button in the popup
        while True:
            print(',', end="")
            try:
                browser.find_element_by_id("RO_MoreInfo").click()
                break
            except:
                sleep(1)

        # Scrape data
        while True:
            print('.', end="")
            try:
                text = browser.find_element_by_id("Information").text
                break
            except:
                sleep(1)
        print()
        sleep(1)

        # Check that the text is appropriate
        text = text.split('\n')
        if text[0] != outside_label:
            raise ValueError(f'Expected {outside_label}, but got {text[0]}.')

        # Close out of the popup if its there.
        for element in browser.find_elements_by_tag_name("div"):
            if element.get_attribute("aria-label") == "close":
                element.click()
                break

        # Parse out the price into dollar format
        cost = ''
        for word in text[1].split(' '):
            if '¢' in word:
                cost = '$0.' + word[:-1]
            elif '$' in word:
                cost = word + ('.00', '')['.' in word]
        info.append(Item(text[0], cost))
        print(info[-1])
        sleep(1)

    # Flip the page
    for element in browser.find_elements_by_tag_name("button"):
        if element.get_attribute("aria-label") and "Go to next page" in element.get_attribute("aria-label"):
            print(f'Flipping page to {element.get_attribute("aria-label").split(" ")[-1]}')
            element.click()
            sleep(2)
            break

print(f'  {len(info)} items gathered.\n\n')
browser.close()
