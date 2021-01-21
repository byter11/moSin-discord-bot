import requests
import json
import urllib.parse
import socket
hostname = socket.gethostname()

class ValorantAPI(object):
  access_token = None
  cookies = None
  entitlements_token = None

  def __init__(self, username, password, region):
    self.username = username
    self.password = password
    self.region = region
    self.client_ip = socket.gethostbyname(hostname)

    self.cookies = self.get_cookies()

    self.access_token = self.get_access_token()

    self.entitlements_token = self.get_entitlements_token()

    self.user_info, self.game_name = self.get_user_info()

  def get_cookies(self):
    data = {
    'client_id': 'play-valorant-web-prod',
    'nonce': '1',
    'redirect_uri': 'https://playvalorant.com/',
    'response_type': 'token id_token',
    'scope': 'account openid',
    }
    headers = {
      'X-Forwarded-For': self.client_ip
    }
    r = requests.post('https://auth.riotgames.com/api/v1/authorization', headers=headers, json=data)

    cookies = r.cookies

    return cookies

  def get_access_token(self):
    data = {
      'type': 'auth',
      'username': self.username,
      'password': self.password
    }
    headers = {
      'X-Forwarded-For': self.client_ip
    }
    r = requests.put('https://auth.riotgames.com/api/v1/authorization', headers=headers, json=data, cookies=self.cookies)
    uri = r.json()['response']['parameters']['uri']
    jsonUri = urllib.parse.parse_qs(uri)

    access_token = jsonUri['https://playvalorant.com/#access_token'][0]

    return access_token

  def get_entitlements_token(self):
    headers = {
      'Authorization': f'Bearer {self.access_token}',
      'X-Forwarded-For': self.client_ip
    }
    r = requests.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}, cookies=self.cookies)

    entitlements_token = r.json()['entitlements_token']

    return entitlements_token

  def get_user_info(self):
    headers = {
      'Authorization': f'Bearer {self.access_token}',
      'X-Forwarded-For': self.client_ip
    }
    r = requests.post('https://auth.riotgames.com/userinfo', headers=headers, json={}, cookies=self.cookies)
    jsonData = r.json()
    user_info = jsonData['sub']
    name = jsonData['acct']['game_name']
    tag  = jsonData['acct']['tag_line']
    game_name = name + ' #' +  tag

    return user_info, game_name

  def get_match_history(self, userinf = None, qty=10):
    headers = {
      'Authorization': f'Bearer {self.access_token}',
      'X-Riot-Entitlements-JWT': f'{self.entitlements_token}',
      'X-Forwarded-For': self.client_ip,
      'X-Riot-ClientPlatform' : 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'
    }
    if userinf is None: 
      userinf = self.user_info
    r = requests.get(f'https://pd.{self.region}.a.pvp.net/mmr/v1/players/{userinf}/competitiveupdates?startIndex=0&endIndex={qty}', headers=headers, cookies=self.cookies)

    jsonData = r.json()
    return jsonData

