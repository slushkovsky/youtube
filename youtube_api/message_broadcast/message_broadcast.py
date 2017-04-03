from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _login(driver: WebDriver, username, password):
    driver.get(
        'https://accounts.google.com/ServiceLogin'
        '?uilel=3&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fhl%3Den%26feature%3Dsign_in_button%26app%3Ddesktop%26action_handle_signin%3Dtrue%26next%3D%252F&service=youtube&passive=true&hl=en#identifier'
    )

    driver.find_element_by_id('Email').send_keys(username)
    driver.find_element_by_id('next').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "Passwd"))
    ).send_keys(password)
    driver.find_element_by_id('signIn').click()


def _send_message(driver, channel_url, message_text):
    if not channel_url.endswith('/about'):
        channel_url += '/about'

    driver.get(channel_url)

    try:
        send_message_btn = driver.find_element_by_css_selector(
            '#action-buttons > ytd-button-renderer:nth-child(2)')
    except NoSuchElementException:
        print('Messages are not available or the old YouTube design')
        return False

    send_message_btn.click()

    text_input = driver.find_element_by_css_selector(
        '#input > paper-input-container > div.input-content.label-is-floating.style-scope.paper-input-container input')
    text_input.send_keys(message_text)

    driver.execute_script(
        '''
            document.querySelector('#buttons > ytd-button-renderer.style-scope.ytd-form-popup-renderer.style-brand > a').click();
        '''.format(message_text))

    return True


class MessageBroadcaster(object):
    def __init__(self, driver, login, password):
        self._driver = driver
        self._login = login
        self._password = password
        self._logined = False

    def do_login(self):
        if not self._logined:
            _login(self._driver, self._login, self._password)

    def broadcast_message(self, channel_ids, message_text):
        if not isinstance(channel_ids, list):
            channel_ids = [channel_ids]

        for cid in channel_ids:
            _send_message(self._driver, cid, message_text)
