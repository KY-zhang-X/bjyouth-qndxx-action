
import os
import traceback
from qndxx import QnDxx
from push import ServerChan

def main():
    username = os.environ.get('BJYOUTH_USERNAME')
    password = os.environ.get('BJYOUTH_PASSWORD')
    sct_key = os.environ.get('SERVERCHAN_KEY')

    if not (username and password):
        print("没有用户名或密码")
        exit(-1)

    dxx = QnDxx()
    if sct_key:
        sct = ServerChan(sct_key)
    else:
        sct = None

    try:
        title = dxx.run(username, password)
        if title and sct:
            sct.push("学习成功 [qndxx]", f"课程标题：{title}")
        return 0
    except Exception as exc:
        if sct:
            sct.push("学习失败 [qndxx]", repr(exc))
        traceback.print_exc()
        exit(-1)

if __name__ == '__main__':
    main()
