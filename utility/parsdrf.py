import requests
import fake_useragent
from bs4 import BeautifulSoup
import json


class ParsingDRF:

    def __init__(self, auth_host, login, password):
        self.auth_host = auth_host
        self.login = login
        self.password = password
        # return (self, auth_host, login, password)

    def __auth_write_cookies(self):
        session = requests.Session()
        login_response = session.get(self.auth_host)
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        data = {
            'user-agent': fake_useragent.UserAgent().random,
            'csrfmiddlewaretoken': csrf_token,
            'username': self.login,
            'password': self.password
        }
        response = session.post(self.auth_host, data=data)
        if response.status_code == 200:
            cookies_dict = [
                {"domain": key.domain, "name": key.name, "path": key.path, "value": key.value}
                for key in session.cookies
            ]
            with open('cookies_auth.json', 'w', encoding='utf-8') as fj:
                json.dump(cookies_dict, fj, ensure_ascii=False)
            return cookies_dict
        else:
            print("Failed to login")

    @classmethod
    def __set_session(cls, cookies_dict):
        session2 = requests.Session()
        for cookies in cookies_dict:
            session2.cookies.set(**cookies)
        return session2

    def __load_cookies(self):
        try:
            with open('cookies_auth.json') as fjson:
                str_file = fjson.read()
                if len(str_file) != 0:
                    cookies_dict = json.loads(str_file)
                else:
                    cookies_dict = self.__auth_write_cookies()
        except FileNotFoundError:
            cookies_dict = self.__auth_write_cookies()
        return self.__set_session(cookies_dict)

    @classmethod
    def __error_403(cls):
        with open('cookies_auth.json', 'w', encoding='utf-8') as fj:
            fj.write('')

    def get_data_db(self, info_page):
        """authorization and receiving data from drf"""
        for retry_count in range(2):
            session2 = self.__load_cookies()
            info_response = session2.get(info_page)
            if info_response.status_code == 200:
                return info_response.text
            elif info_response.status_code == 403:
                self.__error_403()
            else:
                return info_response.status_code

    def write_data_db(self, info_page, data: dict):
        """authorization and data recording using drf"""
        for retry_count in range(2):
            session2 = self.__load_cookies()
            headers = {
                'Content-Type': 'application/json',
                'Content-Length': 'auto',
                'X-CSRFToken': session2.cookies['csrftoken']
            }
            info_response = session2.patch(url=info_page, headers=headers, json=data)
            if info_response.ok:
                return info_response.text
            elif info_response.status_code == 403:
                self.__error_403()
            else:
                return info_response.status_code
