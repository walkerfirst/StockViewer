from urllib import parse
import requests
import re
import base64
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA
import json

def encrpt(password, public_key):
    rsakey = RSA.importKey(public_key)
    cipher = Cipher_pksc1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(password.encode()))
    return cipher_text.decode()


s = requests.session()
# 从html里面获取参数
get_params_url = 'https://passport.jd.com/new/login.aspx?'
response = s.get(url=get_params_url)

loginname = '180*******'
# 正则表达式获取
uuid = re.findall(r"""id="uuid" name="uuid" value="(.*?)"/>""", response.text)[0]
eid = '5B4PGABPPZMEMRMCQMYLIT3EBUOP576CMIC6TVU2ZT26UI2YXWG7POGQIIZNCFMHF2LNDXDXTLC54I5V6WP355ZVE4' # 隐藏参数1【存在与elenent】
fp = '4576ae6a115a0bf9013d988afe393b64'   #隐藏参数2 似乎固定参数【存在与element】
_t = '_t'
loginType = 'c'
pubKey = re.findall(r"""name="pubKey" id="pubKey" value="(.*?)" """, response.text)[0]
sa_token = re.findall(r"""id="sa_token" name="sa_token" value="(.*?)"/>""", response.text)[0]
appid = re.findall(r"""id = "slideAppId" value="(.*?)" """, response.text)[0]

response = s.get(url='https://seq.jd.com/jseqf.html?bizId=passport_jd_com_login_pc&platform=js&version=1')
seqSid = re.findall(r"""ar _jdtdmap_sessionId="(.*?)";""", response.text)[0]


# 获取challenge
callbacks = 'jsonp_03705059368865016'
slideChallengeUrl = 'https://iv.jd.com/slide/g.html?'
challengeParams = {
    'appid': appid,
    'scene': 'login',
    'product': 'bind-suspend',
    'e': eid,
    'lang': 'zh_CN',
    'callbacks': callbacks
}
challengeResponse = s.get(url=slideChallengeUrl+parse.urlencode(challengeParams))
c = json.loads(challengeResponse.text)['challenge']

# 获取authcode
getAuthcodeUrl = 'https://iv.jd.com/slide/s.html?'
d = ''    # 未知，和滑动轨迹相关
authcodeData = {
    'd': d,
    'c': c,
    'w': '0',
    'appid': appid,
    'scene': 'login',
    'product': 'bind-suspend',
    'e': eid,
    's': seqSid,
    'o': loginname,
    'lang': 'zh_CN',
    'callbacks': callbacks
}

response = s.post(url=getAuthcodeUrl, data=authcodeData)
authcode = json.loads(response.text)['validate']


print('uuid: ' + uuid)
print('pubKey: ' + pubKey)
print('sa_token: ' + sa_token)
print('seqSid: ' + seqSid)
print('challenge: ' + c)
print('authcode: ' + authcode)
public_key = """-----BEGIN PUBLIC KEY-----""" + '\n' + pubKey + '\n' + """-----END PUBLIC KEY-----"""
pass_word = '你的京东密码'
nloginpwd = encrpt(pass_word, public_key)
print('nloginpwd: ' + nloginpwd)
# print(public_key)

query_string = {
    'uuid': uuid,
    'ReturnUrl': 'https://www.jd.com/',
    'r': '0.17803919186799178',
    'version': '2015'
}
query_data = parse.urlencode(query_string)
url = 'https://passport.jd.com/uc/loginService?'+query_data


form_data = {
    'uuid': uuid,
    'eid': eid,
    'fp': fp,
    '_t': _t,
    'loginType': loginType,
    'loginname': loginname,
    'nloginpwd': nloginpwd,
    'authcode': authcode,
    'pubKey': pubKey,
    'sa_token': sa_token,
    'seqSid': seqSid,
    'useSlideAuthCode': '1'
}
response = s.post(url=url, data=form_data)
print(response.content)
print(form_data)
# # 查看全部订单---用于检测登入是否成功
get_order_url = 'https://order.jd.com/lazy/getOrderProductInfo.action'
form_data = {
    'orderWareIds': '6772447,28963064241,100003322095,3633865,1524452394,20104267538,39859829911,39859829912,39859829913,5399004,5148241,100000440283',
    'orderWareTypes': '0,0,0,0,0,0,0,0,0,0,0,0',
    'orderIds': '102533901401,101975046353,101885954715,101994752966,101725563313,100911288261,100911288261,100911288261,100911288261,100689520591,100689520591,100185092518',
    'orderTypes': '0,22,0,0,22,22,22,22,22,0,0,0',
    'orderSiteIds': '0,0,0,0,0,0,0,0,0,0,0,0',
    'sendPays': '0,0,0,0,0,0,0,0,0,0,0,0'
}

response = s.post(url=get_order_url, data=form_data)
print(response.text)