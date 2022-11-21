import re
import execjs
import requests
import json
from requests.utils import add_dict_to_cookiejar
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import hashlib


# 关闭ssl验证提示
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
}
url = 'https://www.mafengwo.cn/i/23869886.html'
# 使用session保持会话
session = requests.session()


def get_parameter(response):
    # 提取js代码
    js_clearance = re.findall('cookie=(.*?);location', response.text)[0]
    # 执行后获得cookie参数js_clearance
    result = execjs.eval(js_clearance).split(';')[0].split('=')[1]
    # 添加cookie
    add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': result})
    # 第二次请求
    response = session.get(url, headers=header, verify=False)
    # 提取参数并转字典
    go = json.loads(re.findall(r';go\((.*?)\)', response.text)[0])

    return go


def get_cookie(go):
    # 判断加密方式
    for i in range(len(go['chars'])):
        for j in range(len(go['chars'])):
            values = go['bts'][0] + go['chars'][i] + go['chars'][j] + go['bts'][1]
            if go['ha'] == 'md5':
                ha = hashlib.md5(values.encode()).hexdigest()
            elif go['ha'] == 'sha1':
                ha = hashlib.sha1(values.encode()).hexdigest()
            elif go['ha'] == 'sha256':
                ha = hashlib.sha256(values.encode()).hexdigest()
            if ha == go['ct']:
                __jsl_clearance_s = values
    return __jsl_clearance_s


def run():
    # 第一次请求
    response = session.get(url, headers=header, verify=False)
    # 获取参数及加密方式
    parameter = get_parameter(response)
    # 获取cookie
    clearance = get_cookie(parameter)
    print(clearance)
    # 修改cookie
    add_dict_to_cookiejar(session.cookies, {'__jsl_clearance_s': clearance})
    # 第三次请求
    html = session.get(url, headers=header, verify=False)
    #print(html.cookies)
    #print(html.content.decode())
    
    return html
    
page = run()
data_url = re.findall(r'data-url="(.*?)type=.m3u8', page.text)[0]  + "type=.m3u8"
response =requests.get(data_url, headers=header, allow_redirects=False)
m3u8addr =response.headers["Location"]
print("m3u8addr", m3u8addr)

