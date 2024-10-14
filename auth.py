# Author: Erick Ruh Cardozo  (W1SD00M) - <erickruhcardozo98@gmail.com>
# Date: Jul 15, 2024 - 10:25 AM
# Description: This module attempts to log-in a user on the NPR System.
#              Uppon success, returns a session object with the authenticated user.

from dataclasses import dataclass
from requests import Session
from urllib.parse import urlparse
from json import JSONDecoder


MAX_ATTEMPTS = 3


@dataclass
class User:
    name: str
    ssn: str
    password: str


class UserDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if 'name' not in dct or 'ssn' not in dct or 'password' not in dct:
            return dct
        return User(dct['name'], dct['ssn'], dct['password'])


def login(user: User) -> bool | Session:
    session = Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    payload = {'attribute': user.ssn, 'password': user.password}
    attempts = 0
    
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        response = session.get('https://notaparana.pr.gov.br/nfprweb/ContaCorrente')
        url = urlparse(response.url) # Get the step param from the system
        response = session.post('https://authz.identidadedigital.pr.gov.br/cidadao_authz/api/v1/authorize', params=url.query, data=payload)

        if response.status_code != 200:
            return False

        if 'Ops!' in response.text:
            session.get('https://notaparana.pr.gov.br/nfprweb/publico/sair')
        elif 'MINHA CONTA CORRENTE' in response.text:
            return session
    
    return False