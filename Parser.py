import selenium
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

ZIPCODE = 38637
STORE = 0


class Item:
    def __init__(self, name: str, price: str):
        self.name = name
        self.price = price

    def __str__(self):
        return self.name + ' @ ' + self.price


# Open the browser and go to Aldi
browser = webdriver.Chrome()
browser.get('https://www.aldi.us/en/weekly-specials/our-weekly-ads/')
info = []

# Find the store
browser.switch_to.frame("shopLocalPlatformFrame")
element = browser.find_element_by_id("locationInput")
element.send_keys("38637")
sleep(0.2)  # It hung on me once for some reason, so just to be safe
element.send_keys(Keys.ENTER)
sleep(2)
element = browser.find_elements_by_class_name("nuepselectstorebtns")[0]
element.click()

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
        while True:
            print('.', end="")
            try:
                areas[a].click()
                break
            except:
                sleep(1)
        sleep(2)
        while True:
            print(',', end="")
            try:
                browser.find_element_by_id("RO_MoreInfo").click()
                break
            except:
                sleep(1)
        sleep(2)
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
        t = text.split('\n')
        if t[0] != outside_label:
            raise ValueError(f'{t[0]} does not match {outside_label}.')

        # Close out of the popup if its there.
        for element in browser.find_elements_by_tag_name("div"):
            if element.get_attribute("aria-label") == "close":
                element.click()
                break

        # Parse out the price into dollar format
        price = ''
        for word in t[1].split(' '):
            if '¢' in word:
                price = '$0.' + word[:-1]
            elif '$' in word:
                price = word + ('.00', '')['.' in word]
        i = Item(t[0], price)
        info.append(i)
        print(f' - {i}')
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
