from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from random import random


def main():
    SPEED_FACTOR = 0.5
    url = r'https://www.facebook.com/messages/t'
    driver = webdriver.Chrome()
    driver.get(url)

    print('Please log in to your account')
    print("Press enter to continue")
    input()

    print('Please scroll down or press end key to reach the bottom of the list')
    print("Press enter to start removing all friends")
    input()

    # elements = driver.find_elements(by=By.CSS_SELECTOR, value='[aria-label=Chats]>*>*>*>*>.x1n2onr6>.html-div.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd:not([role])')
    elements = driver.find_elements(by=By.CSS_SELECTOR, value='[aria-label="Archived chats"]>*>*>*>*>.x1n2onr6>.html-div.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd:not([role])')[50:]
    total = len(elements)
    print(f'Removing {total} chats')
    count = 0
    for element in elements:
        try:
            sleep(random() * 2 * SPEED_FACTOR)
            driver.execute_script("arguments[0].scrollIntoView();", element)
            sleep(random() * 1 * SPEED_FACTOR)
            webdriver.ActionChains(driver).move_to_element(element).perform()
            sleep(random() * 1 * SPEED_FACTOR)

            btn = element.find_elements(by=By.CSS_SELECTOR, value='[aria-label=Menu]')[0]
            if not btn:
                continue
            webdriver.ActionChains(driver).move_to_element(btn).click(btn).perform()
            sleep(random() * 1 * SPEED_FACTOR)

            btn = driver.find_elements(by=By.XPATH, value="//*[text()='Delete chat']")[0]
            if not btn:
                continue
            webdriver.ActionChains(driver).move_to_element(btn).click(btn).perform()
            sleep(random() * 1 * SPEED_FACTOR)

            btn = driver.find_elements(by=By.CSS_SELECTOR, value='[aria-label="Delete chat"]')[2]
            if not btn:
                continue
            webdriver.ActionChains(driver).move_to_element(btn).click(btn).perform()
            sleep(random() * 1 * SPEED_FACTOR)

            count += 1
            print(f'{count}/{total} removed')
        except Exception as e:
            print(e)
    print('Done')


if __name__ == '__main__':
    main()
