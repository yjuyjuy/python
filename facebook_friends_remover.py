from selenium import webdriver


def main():
    url = r'https://m.facebook.com/friends/center/friends?locale=en_US'
    driver = webdriver.Chrome()
    driver.get(url)

    print('Please log in to your account')
    print("Press enter to continue")
    input()

    print('Please scroll down or press end key to reach the bottom of the list')
    print("Press enter to start removing all friends")
    input()

    elements = driver.find_elements_by_css_selector('._5s61._8-j9._5i2i._52we')
    total = len(elements)
    print(f'Removing {total} friends')
    count = 0
    for element in elements:
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()
        btn = driver.find_elements_by_css_selector(
            '._54k8._55i1._58a0.touchable')[1]
        webdriver.ActionChains(driver).move_to_element(
            btn).click(btn).perform()

        count += 1
        print(f'{count}/{total} removed')

    print('Done')


if __name__ == '__main__':
    main()
