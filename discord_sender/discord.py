import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEyMy4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEyMy4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIzLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6Imh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vIiwicmVmZXJyaW5nX2RvbWFpbiI6Ind3dy5nb29nbGUuY29tIiwic2VhcmNoX2VuZ2luZSI6Imdvb2dsZSIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNjQ5MTMsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9',
    'X-Fingerprint': '1205865286134145075.ooL9YeriQ9B_56fJkPSo7nNrbvw',
    'X-Discord-Locale': 'en-US',
    'X-Discord-Timezone': 'America/New_York',
    'X-Debug-Options': 'bugReporterEnabled',
    'Origin': 'https://discord.com',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://discord.com/login',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

DATA = {
    'login': 'xxxxx@gmail.com',
    'password': 'xxxxx',
    'undelete': False,
    'login_source': None,
    'gift_code_sku_id': None,
}


def login_with_credentials(username: str, password: str):
    sess = requests.Session()
    sess.get("https://discord.com/login")  # Get required cookie
    creds = DATA
    creds['login'] = username
    creds['password'] = password.replace('\\', '\\\\')
    response = sess.post('https://discord.com/api/v9/auth/login', headers=HEADERS, json=creds)
    pass


def login_with_token(token):
    pass


def login_with_cookie(cookie):
    pass