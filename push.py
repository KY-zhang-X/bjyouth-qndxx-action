import requests

class ServerChan(object):

    def __init__(self, sct_key) -> None:
        self.sct_url = f"https://sctapi.ftqq.com/{sct_key}.send"

    def push(self, title, description=''):
        try:
            res = requests.post(url=self.sct_url, data={
                "title": title,
                "desp": description
            })
            res_json = res.json()
            if res_json['code'] == 0:
                return True
            else:
                return False
        except Exception:
            return False

