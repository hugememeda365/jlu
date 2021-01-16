import requests
from urllib import parse
from lxml import etree
import json
import time
import os
import random
import logging


class Logger:
    def __init__(self, log_filename, log_level, logger_name):
        # 创建一个logger
        self.__logger = logging.getLogger(logger_name)

        # 指定日志的最低输出级别，默认为WARN级别
        self.__logger.setLevel(log_level)
        # 定义handler的输出格式
        formatter = logging.Formatter('[%(asctime)s %(levelname)s]: %(message)s')
        
        # 创建一个handler用于写入日志文件
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8', delay=False)
        file_handler.setFormatter(formatter)
        self.__logger.addHandler(file_handler)
        
        # 创建一个handler用于输出控制台
        # console_handler = logging.StreamHandler()        
        # console_handler.setFormatter(formatter)        
        # self.__logger.addHandler(console_handler)

    def get_log(self):
        return self.__logger


class MsgException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def get_now_time():
    time_array = time.localtime()
    return time.strftime('%Y-%m-%d %H:%M:%S', time_array)


def get_int_timestamp():
    return int(time.time())


def is_json(str_res):
    if isinstance(str_res, str):
        try:
            json.loads(str_res)
        except (ValueError, Exception):
            return False
        return True
    else:
        return False


def read_config(_config_file):
    try:
        with open(_config_file, 'r', encoding='utf-8') as file_object:
            content = file_object.read()
            _info = json.loads(content)
    except Exception:
        _info = {}
    return _info


def sign(info):
    url = 'https://ehall.jlu.edu.cn/infoplus/form/YJSMRDK/start'
    headers = {
        "Host": "ehall.jlu.edu.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    logger.info('正在请求第1个链接响应...')
    response = requests.get(url=url, headers=headers, allow_redirects=False)
    logger.info('请求第1个链接成功')
    cookies = response.cookies.get_dict()
    location = response.headers['location']
    decode_url = parse.unquote(location)
    logger.info('正在请求第2个链接响应...')
    response = requests.get(url=decode_url, headers=headers, cookies=cookies, allow_redirects=False)
    logger.info('请求第2个链接响应成功')
    location = response.headers['location']
    encode_location = parse.unquote(location)
    new_url = encode_location
    logger.info('正在请求第3个链接响应...')
    response = requests.get(url=encode_location, headers=headers, cookies=cookies, allow_redirects=False)
    logger.info('请求第3个链接响应成功')
    location = response.headers['location']
    encode_location = parse.unquote(location)
    new_cookies = response.cookies.get_dict()
    logger.info('正在请求第4个链接响应...')
    response = requests.get(url=encode_location, headers=headers, cookies=new_cookies, allow_redirects=False)
    logger.info('请求第4个链接响应成功')
    response_xpath = etree.HTML(response.text)
    pid = response_xpath.xpath('//input[@name="pid"]/@value')
    source = response_xpath.xpath('//input[@name="source"]/@value')
    data = {
        "username": info['username'],
        "password": info['password'],
        "pid": pid,
        "source": source
    }
    content_type = {'Content-Type': 'application/x-www-form-urlencoded'}
    origin = {'Origin': 'https://ehall.jlu.edu.cn'}
    headers.update(content_type)
    headers.update(origin)
    headers.update({'Refer': encode_location})

    url = 'https://ehall.jlu.edu.cn/sso/login'
    logger.info('用户[{0}]正在登录系统...'.format(info['username']))
    response = requests.post(url=url, headers=headers, cookies=new_cookies, data=data, allow_redirects=False)
    login_cookies = response.cookies.get_dict()
    response_text = response.text.replace('\n', '')
    if len(response_text) > 0:
        if 'INVALID_PASSWORD' in response_text:
            msg = '用户[{0}]登陆失败，账号或者密码错误'.format(info['username'])
            logger.info(msg)
            desp = {
                "state": "失败",
                "msg": msg
            }
            send_notice(desp, info['sckey'])
            exit(0)
        else:
            raise MsgException(response_text)
    logger.info('用户[{0}]登录系统成功'.format(info['username']))
    last_cookies = dict(new_cookies, **login_cookies)
    headers.pop('Content-Type')
    headers.pop('Origin')

    logger.info('正在请求第5个链接响应...')
    response = requests.get(url=new_url, headers=headers, cookies=last_cookies, allow_redirects=False)
    logger.info('请求第5个链接响应成功')

    location = response.headers['location']
    encode_location = parse.unquote(location)

    logger.info('正在请求第6个链接响应...')
    response = requests.get(url=encode_location, cookies=cookies, headers=headers, allow_redirects=False)
    logger.info('请求第6个链接响应成功')

    location = response.headers['location']
    encode_location = parse.unquote(location)

    logger.info('正在请求第7个链接响应...')
    response = requests.get(url=encode_location, cookies=cookies, headers=headers)
    logger.info('请求第7个链接响应成功')

    url = 'https://ehall.jlu.edu.cn/infoplus/static/js/Release/Start.js'
    headers.update({'Refer': encode_location})
    logger.info('正在请求第8个链接响应...')
    requests.get(url=url, cookies=cookies, headers=headers)
    logger.info('请求第8个链接响应成功')

    response_xpath = etree.HTML(response.text)
    idc = response_xpath.xpath('//div/input[@id="idc"]/@value')[0]
    release = response_xpath.xpath('//div/input[@id="release"]/@value')[0]
    csrfToken = response_xpath.xpath('//meta[@itemscope="csrfToken"]/@content')[0]
    formData = {
        "_VAR_URL": encode_location,
        "_VAR_URL_Attr": {}
    }
    form_Data = json.dumps(formData)
    data = {
        "idc": idc,
        "release": release,
        "csrfToken": csrfToken,
        "formData": form_Data
    }
    logger.info('正在请求第9个链接响应...')
    url = 'https://ehall.jlu.edu.cn/infoplus/interface/start'
    response = requests.post(url=url, headers=headers, data=data, cookies=cookies)
    logger.info('请求第9个链接响应成功')

    if not is_json(response.text):
        msg = '/infoplus/interface/start文件数据格式出错'
        logger.info(msg)
        raise MsgException(msg)
    response_json = json.loads(response.text)
    if 'errno' in response_json and response_json['errno'] != 0:
        msg = response_json['error'].replace('\n', '')
        logger.info(msg)
        if 'try' in msg:
            raise MsgException(msg)
        desp = {
            "state": "失败",
            "msg": msg
        }
        send_notice(desp, info['sckey'])
        exit(0)
    entities = response_json['entities'][0]
    entities_list = entities.split('/')
    set_id = entities_list[5]
    logger.info('正在请求第10个链接响应...')
    requests.get(url=entities, cookies=cookies, headers=headers)
    logger.info('请求第10个链接响应成功')

    url = 'https://ehall.jlu.edu.cn/infoplus/alive'

    headers.update({'Refer': entities})
    logger.info('正在请求/infoplus/alive文件...')
    requests.get(url=url, cookies=cookies, headers=headers)
    logger.info('请求/infoplus/alive文件成功')

    url = 'https://ehall.jlu.edu.cn/infoplus/interface/render'
    headers.update({'content-type': 'application/x-www-form-urlencoded; charset=utf-8'})
    headers.pop('Refer')
    headers.pop('Upgrade-Insecure-Requests')
    headers.update({'Referer': entities})
    headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01'})
    headers.update({'Origin': 'https://ehall.jlu.edu.cn'})
    headers.update({'X-Requested-With': 'XMLHttpRequest'})
    data = {
        "stepId": set_id,
        "instanceId": "",
        "admin": "false",
        "rand": random.uniform(0, 1) * 999,
        "width": "1536",
        "lang": "zh",
        "csrfToken": csrfToken
    }
    logger.info('正在请求/infoplus/interface/render文件...')
    response = requests.post(url=url, cookies=cookies, headers=headers, data=data)
    logger.info('请求/infoplus/interface/render文件成功')

    if not is_json(response.text):
        msg = '/infoplus/interface/render文件数据格式出错'
        logger.info(msg)
        raise MsgException(msg)
    response_json = json.loads(response.text)
    if 'errno' in response_json and response_json['errno'] != 0:
        logger.info(response_json['error'])
        desp = {
            'state': "失败",
            "msg": response_json['error']
        }
        send_notice(desp, info['sckey'])
        exit(0)
    entities = response_json['entities'][0]
    data = entities['data']

    fields = entities['fields']
    actions = entities['actions']
    actionId = actions[0]['id']

    boundFields = ''
    for key in fields:
        if key != 'fieldSQbj':
            boundFields = '{0}{1},'.format(boundFields, key)
    boundFields = boundFields.rstrip(',')
    info.update({'fieldSQxm_Name': data['fieldSQxm_Name']})
    body = {
        "stepId": set_id,
        # actionId变量动态获取可能不对，可能会出错
        "actionId": actionId,
        "formData": data,
        "timestamp": get_int_timestamp(),
        "rand": random.uniform(0, 1) * 999,
        "boundFields": boundFields,
        "csrfToken": csrfToken,
        "lang": "zh"
    }
    url = 'https://ehall.jlu.edu.cn/infoplus/interface/listNextStepsUsers'
    logger.info('正在请求/infoplus/interface/listNextStepsUsers文件...')
    response = requests.post(url=url, cookies=cookies, headers=headers, data=body)
    logger.info('请求/infoplus/interface/listNextStepsUsers文件成功')
    if not is_json(response.text):
        msg = '/infoplus/interface/listNextStepsUsers文件数据格式出错'
        logger.info(msg)
        raise MsgException(msg)

    response_json = json.loads(response.text)
    if 'errno' in response_json and response_json['errno'] != 0:
        logger.info(response_json['error'])
        desp = {
            'state': "失败",
            "msg": response_json['error']
        }
        send_notice(desp, info['sckey'])
        exit(0)
    # remark变量的数据没有动态获取，可能会出错
    body.update({"remark": ""})
    body.update({"rand": random.uniform(0, 1) * 999})
    # nextUsers变量的数据没有动态获取，可能会出错
    nextUsers = {}
    nextUsers = json.dumps(nextUsers)
    body.update({"nextUsers": nextUsers})
    body.update({"timestamp": get_int_timestamp()})

    url = 'https://ehall.jlu.edu.cn/infoplus/interface/doAction'
    logger.info('正在请求/infoplus/interface/doAction文件...')
    response = requests.post(url=url, cookies=cookies, headers=headers, data=body)

    logger.info('请求/infoplus/interface/doAction文件成功')
    logger.info(response.text)
    if not is_json(response.text):
        msg = '/infoplus/interface/doAction文件数据格式出错'
        logger.info(msg)
        raise MsgException(msg)
    response_json = json.loads(response.text)
    if 'errno' in response_json and response_json['errno'] != 0:
        logger.info(response_json['errno'])
        desp = {
            'state': "失败",
            "msg": response_json['error']
        }
        send_notice(desp, info['sckey'])
        exit(0)
    msg = '恭喜{0}打卡成功'.format(info['fieldSQxm_Name'])
    logger.info(msg)
    desp = {
        'state': "成功",
        "msg": msg
    }
    send_notice(desp, info['sckey'])
    exit(0)


def send_notice(desp, sckey=''):
    if sckey == "":
        logger.info('没有sckey, 微信推送通知失败，请登录[http://sc.ftqq.com]获取sckey,并关注微信公众号[方糖]')
        exit(0)
    url = 'https://sc.ftqq.com/{0}.send'.format(sckey)
    text = '吉林大学防疫自动签到{0}通知'.format(desp['state'])
    data = {
        "text": text,
        "desp": '【{0}】:{1}'.format(get_now_time(), desp['msg'])
    }
    response = requests.post(url=url, data=data)
    # print(response.text)
    if not is_json(response.text):
        logger.info('sckey不正确, 微信通知失败，请登录[http://sc.ftqq.com]获取sckey,并关注微信公众号[方糖]')
        exit(0)
    response_json = json.loads(response.text)
    if 'errno' in response_json:
        if response_json['errno'] == 0:
            logger.info('微信推送通知成功【{0}】'.format(desp['msg']))
        elif response_json['errmsg'] == "bad pushtoken":
            logger.info('sckey不正确, 微信通知失败，请登录[http://sc.ftqq.com]获取sckey,并关注微信公众号[方糖]')
        else:
            logger.info('微信推送通知失败,{0}'.format(response_json['errmsg']))
    else:
        logger.info('sckey不正确, 微信通知失败，请登录[http://sc.ftqq.com]获取sckey,并关注微信公众号[方糖]')


if __name__ == '__main__':
    logger = Logger(log_filename='jlu.log', log_level=logging.DEBUG, logger_name='jlu').get_log()
    logger.info('===================================')
    logger.info('程序启动成功')
    sec = random.randrange(1, 40)
    mkdir = os.getcwd()
    config_file = '{0}{1}config.json'.format(mkdir, os.sep)
    logger.info('正在读取配置文件，文件位置[{0}]...'.format(config_file))
    info = read_config(config_file)
    if not info:
        msg = '读取配置文件有误，[{0}]不存在或者不是json文件'.format(config_file)
        logger.info(msg)
        exit(0)
    logger.info('读取配置文件config.json成功')
    for key in info:
        info[key] = info[key].strip()
    try:
        count = int(info['times'])
    except Exception:
        count = 20
    while True:
        try:
            count = count - 1
            sign(info)
        except Exception as e:
            if count <= 0:
                desp = {
                    "state": "失败",
                    "msg": e
                }
                logger.info('签到失败,请你手动尝试')
                send_notice(desp, info['sckey'])
                exit(0)
            logger.info('程序异常{0}，等待30秒后重试...'.format(e))
            time.sleep(30)
