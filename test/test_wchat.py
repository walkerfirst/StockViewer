import itchat
#PICTURE, RECORDING, ATTACHMENT, VIDEO,TEXT
# 图片、录制、附件、视频、文本
from itchat.content import PICTURE, RECORDING, ATTACHMENT, VIDEO,TEXT
#登入
itchat.auto_login()
#保持运行
itchat.run()
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    filedpx="./filex/"+msg["FileName"] #得到文件路径，目录需要手动创建
    msg.download(filedpx) #下载
    return "你发送的文件类型"+msg['Type']+"  保存地址为：filex/"+msg.fileName