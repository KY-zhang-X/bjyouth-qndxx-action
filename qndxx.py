import re
import base64
import requests
import ddddocr
import time
from typing import Tuple
from io import BytesIO
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from PIL import Image

class QnDxx(object):

    bjyouth_login_url = "https://m.bjyouth.net/site/login"
    bjyouth_dxx_index_url = "https://m.bjyouth.net/dxx/index"
    bjyouth_dxx_record_url = "https://m.bjyouth.net/dxx/my-study"
    bjyouth_dxx_detail_url = "https://m.bjyouth.net/dxx/course-detail"
    bjyouth_dxx_league_url = "https://m.bjyouth.net/dxx/is-league"
    bjyouth_dxx_check_url = "https://m.bjyouth.net/dxx/check"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    
    def run(self, username: str, password: str) -> str:
        '''
        脚本入口, 执行一次学习
        '''
        # 登录bjyouth
        retry = 0
        while retry < 4:    # 重试最多4次
            print(f"尝试登录...{retry}")
            if self.login(username, password):
                break
            else:           # 验证码错误
                print("验证码错误")
                retry += 1
        else:
            print("尝试4次登录均出错, 脚本退出")
            return None
        # 获取最新课程ID和课程标题
        print("尝试获取最新课程信息")
        course_id, course_title = self.get_course()
        # 根据课程标题判断课程是否已经学习过
        print("判断课程是否学习过")
        if self.is_checked(course_title):
            print("课程已经学习过, 脚本退出")
            return None
        # 获取组织ID
        print("获取组织ID")
        org_id = self.get_org_id()
        # 课程学习打卡
        print("尝试学习打卡")
        if self.check(course_id, org_id):
            print("学习打卡成功")
            return course_title
        else:
            print("学习打卡失败")
            return None
            


    def login(self, username: str, password: str) -> bool:
        '''
        登录bjyouth
        '''
        pubkey = \
            '-----BEGIN PUBLIC KEY-----\n' + \
            'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD5uIDebA2qU746e/NVPiQSBA0Q3J8/G23zfrwMz4qoip1vuKaVZykuMtsAkCJFZhEcmuaOVl8nAor7cz/KZe8ZCNInbXp2kUQNjJiOPwEhkGiVvxvU5V5vCK4mzGZhhawF5cI/pw2GJDSKbXK05YHXVtOAmg17zB1iJf+ie28TbwIDAQAB\n' + \
            '-----END PUBLIC KEY-----'
        captcha = self.get_captcha()
        captcha_code = self.parse_captcha_code(self.denoise(captcha))
        # captcha_code = 'e4u2'
        res = self.session.post(url=self.bjyouth_login_url, verify=False, data={
            '_csrf_mobile': self.session.cookies.get_dict()['_csrf_mobile'],
            'Login[username]': self.js_encrypt(username, pubkey),
            'Login[password]': self.js_encrypt(password, pubkey),
            'Login[verifyCode]': captcha_code
        })
        res_json = res.json()
        if res_json == 8:
            return False
        else:
            rs = res_json['rs']
            if rs == 'fail':
                raise Exception('用户名或密码错误')
            elif rs == 'url':
                return True
            else:
                raise Exception('出现未知的登录错误')

    def get_captcha(self) -> bytes:
        '''
        获取登录页面的验证码
        '''
        res = self.session.get(url=self.bjyouth_login_url, verify=False)
        src = re.findall(r'<img id="verifyCode-image" src="(.+)" alt=".+">', res.text)[0]
        url = "https://m.bjyouth.net" + src
        captcha = self.session.get(url, verify=False).content
        return captcha

    def denoise(self, captcha) -> bytes:
        '''
        验证码图片降噪
        '''
        WHITE_PIXEL = (250, 250, 250)
        img = Image.open(BytesIO(captcha))
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for y in range(img.height):
            for x in range(img.width):
                pix = img.getpixel((x, y))
                count = 0
                if pix == WHITE_PIXEL:
                    continue
                for dir in dirs:
                    if 0 <= x+dir[0] < img.width and 0 <= y+dir[1] < img.height:
                        if img.getpixel((x+dir[0], y+dir[1])) == WHITE_PIXEL:
                            count += 1
                    else:
                        count += 1
                if count >= 5:
                    img.putpixel((x, y), WHITE_PIXEL)
        buf = BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def parse_captcha_code(self, captcha) -> str:
        '''
        验证码识别
        '''
        captcha_code = ddddocr.DdddOcr().classification(img=captcha)
        return captcha_code.replace('l', '1')

    def js_encrypt(self, message: str, pubkey: str) -> str:
        '''
        实现javascript中JsEncrypt函数类似的功能
        '''
        rsakey = RSA.import_key(pubkey)
        cipher = PKCS1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(message.encode()))
        value = cipher_text.decode()
        return value

    def get_course(self) -> Tuple[int, str]:
        '''
        获取最新课程id和标题
        '''
        res = self.session.get(url=self.bjyouth_dxx_index_url, verify=False)
        res_json = res.json()
        course_id = res_json['newCourse']['id']
        course_title = res_json['newCourse']['title']
        return (course_id, course_title)

    def is_checked(self, course_title: str) -> bool:
        '''
        根据课程标题检查是否学习过该课程
        '''
        res = self.session.get(url=self.bjyouth_dxx_record_url, verify=False, params={
            'page': 1,
            'limit': 15,
            'year': time.localtime(time.time()).tm_year
        })
        res_json = res.json()
        records = res_json['data']
        for record in records:
            if course_title in record['text']:
                return True
        return False

    def get_org_id(self) -> int:
        '''
        获取当前组织ID
        '''
        res = self.session.get(url=self.bjyouth_dxx_league_url, verify=False)
        org_id = int(res.text)
        return org_id
        

    def check(self, course_id: int, org_id: int) -> bool:
        '''
        打卡
        '''
        json = {
            'id': course_id,
            'org_id': org_id,
        }
        res = self.session.post(url=self.bjyouth_dxx_check_url, verify=False, json=json)
        if res.text == '':
            return True
        else:
            raise Exception("打卡失败")
