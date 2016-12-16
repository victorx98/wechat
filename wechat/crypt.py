# -*- coding: utf-8 -*-
"""
关于Crypto.Cipher模块，ImportError: No module named 'Crypto'解决方案
请到官方网站 https://www.dlitz.net/software/pycrypto/ 下载pycrypto。
下载后，按照README中的“Installation”小节的提示进行pycrypto安装。
"""
import base64
import string
import random
import hashlib
import time
import struct
import xml.etree.cElementTree as ET
import socket
import sys
from Crypto.Cipher import AES
import imp

if sys.version_info < (3, 0):
    imp.reload(sys)
    sys.setdefaultencoding('utf-8')
    PY3 = False


    def str2bytes(str_s):
        """str to bytes"""
        return str_s
else:
    def str2bytes(str_s):
        """str to bytes"""
        return str_s.encode("utf-8") if isinstance(str_s, str) else str_s

WX_BIZ_MSG_CRYPT_OK = 0
WX_BIZ_MSG_CRYPT_VALIDATE_SIGNATURE_ERROR = -40001
WX_BIZ_MSG_CRYPT_PARSE_XML_ERROR = -40002
WX_BIZ_MSG_CRYPT_COMPUTE_SIGNATURE_ERROR = -40003
WX_BIZ_MSG_CRYPT_ILLEGAL_AES_KEY = -40004
WX_BIZ_MSG_CRYPT_VALIDATE_APPID_OR_CORPID_ERROR = -40005
WX_BIZ_MSG_CRYPT_ENCRYPT_AES_ERROR = -40006
WX_BIZ_MSG_CRYPT_DECRYPT_AES_ERROR = -40007
WX_BIZ_MSG_CRYPT_ILLEGAL_BUFFER = -40008
WX_BIZ_MSG_CRYPT_ENCODE_BASE64_ERROR = -40009
WX_BIZ_MSG_CRYPT_DECODE_BASE64_ERROR = -40010
WX_BIZ_MSG_CRYPT_GEN_RETURN_XML_ERROR = -40011


class FormatException(Exception):
    """Format Exception"""
    pass


def throw_exception(message, exception_class=FormatException):
    """my define raise exception function"""
    raise exception_class(message)


class SHA1(object):
    """计算公众平台的消息签名接口"""

    def get_sha1(self, token, timestamp, nonce, encrypt):
        """用SHA1算法生成安全签名
        @param token:  票据
        @param timestamp: 时间戳
        @param encrypt: 密文
        @param nonce: 随机字符串
        @return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update("".join(sortlist))
            return WX_BIZ_MSG_CRYPT_OK, sha.hexdigest()
        except Exception:
            return WX_BIZ_MSG_CRYPT_COMPUTE_SIGNATURE_ERROR, None

    @staticmethod
    def get_signature(token, timestamp, nonce):
        """get Signature"""
        sign_ele = [token, timestamp, nonce]
        sign_ele.sort()
        str_s = "".join(sign_ele)
        return hashlib.sha1(str2bytes(str_s)).hexdigest()


class XMLParse:
    """提供提取消息格式中的密文及生成回复消息格式的接口"""
    AES_TEXT_RESPONSE_TEMPLATE = '''<xml>
<Encrypt><![CDATA[%(msg_encrypt)s]]></Encrypt>
<MsgSignature><![CDATA[%(msg_signaturet)s]]></MsgSignature>
<TimeStamp>%(timestamp)s</TimeStamp>
<Nonce><![CDATA[%(nonce)s]]></Nonce>
</xml>'''

    def extract(self, xmltext):
        """提取出xml数据包中的加密消息
        @param xmltext: 待提取的xml字符串
        @return: 提取出的加密消息字符串
        """
        try:
            xml_tree = ET.fromstring(xmltext)
            encrypt = xml_tree.find("Encrypt")
            touser_name = xml_tree.find("ToUserName")
            if touser_name is not None:
                touser_name = touser_name.text
            return WX_BIZ_MSG_CRYPT_OK, encrypt.text, touser_name
        except Exception:
            return WX_BIZ_MSG_CRYPT_PARSE_XML_ERROR, None, None

    def generate(self, encrypt, signature, timestamp, nonce):
        """生成xml消息
        @param encrypt: 加密后的消息密文
        @param signature: 安全签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 生成的xml字符串
        """
        resp_dict = {
            'msg_encrypt': encrypt,
            'msg_signaturet': signature,
            'timestamp': timestamp,
            'nonce': nonce,
        }
        resp_xml = self.AES_TEXT_RESPONSE_TEMPLATE % resp_dict
        return resp_xml


class PKCS7Encoder():
    """提供基于PKCS7算法的加解密接口"""
    block_size = 32

    def encode(self, text):
        """ 对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def decode(self, decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = ord(decrypted[-1])
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


class Prpcrypt(object):
    """提供接收和推送给公众平台消息的加解密接口"""

    def __init__(self, key):
        # self.key = base64.b64decode(key+"=")
        self.key = key
        # 设置加解密模式为AES的CBC模式
        self.mode = AES.MODE_CBC

    def encrypt(self, text, appid):
        """对明文进行加密
        @param text: 需要加密的明文
        @return: 加密得到的字符串
        """
        # 16位随机字符串添加到明文开头
        if sys.version_info < (3, 0):
            text = self.get_random_str() + struct.pack("I", socket.htonl(len(text))) + text + appid
        else:
            text = self.get_random_str() + struct.pack("I", socket.htonl(
                len(text))).decode() + text + appid
        # 使用自定义的填充方式对明文进行补位填充
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        # 加密
        cryptor = AES.new(self.key, self.mode, self.key[:16])
        try:
            ciphertext = cryptor.encrypt(text)
            # 使用BASE64对加密后的字符串进行编码
            return WX_BIZ_MSG_CRYPT_OK, base64.b64encode(ciphertext)
        except Exception:
            return WX_BIZ_MSG_CRYPT_ENCRYPT_AES_ERROR, None

    def decrypt(self, text, appid):
        """对解密后的明文进行补位删除
        @param text: 密文
        @return: 删除填充补位后的明文
        """
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text = cryptor.decrypt(base64.b64decode(text))
        except Exception:
            return WX_BIZ_MSG_CRYPT_DECRYPT_AES_ERROR, None
        try:
            pad = ord(plain_text[-1])
            # 去掉补位字符串
            # pkcs7 = PKCS7Encoder()
            # plain_text = pkcs7.encode(plain_text)
            # 去除16位随机字符串
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack("I", content[:4])[0])
            xml_content = content[4:xml_len + 4]
            from_appid = content[xml_len + 4:]
        except Exception:
            return WX_BIZ_MSG_CRYPT_ILLEGAL_BUFFER, None
        if from_appid != appid:
            return WX_BIZ_MSG_CRYPT_VALIDATE_APPID_OR_CORPID_ERROR, None
        return 0, xml_content

    def get_random_str(self):
        """ 随机生成16位字符串
        @return: 16位字符串
        """
        if sys.version_info < (3, 0):
            rule = string.letters + string.digits
        else:
            rule = string.ascii_letters + string.digits
        str_s = random.sample(rule, 16)
        return "".join(str_s)


class WXBizMsgCrypt(object):
    """WXBizMsgCrypt"""

    def __init__(self, s_token, s_encoding_aes_key, s_corp_id):
        if sys.version_info < (3, 0):
            (s_token, s_encoding_aes_key, s_corp_id) = map(str2bytes,
                                                           (s_token, s_encoding_aes_key, s_corp_id))
        else:
            (s_token, s_encoding_aes_key, s_corp_id) = list(
                map(str2bytes, (s_token, s_encoding_aes_key, s_corp_id)))
        try:
            self.key = base64.b64decode(s_encoding_aes_key + "=")
            assert len(self.key) == 32
        except:
            throw_exception("[error]: EncodingAESKey unvalid !",
                            FormatException)
            # return WX_BIZ_MSG_CRYPT_ILLEGAL_AES_KEY )
        self.m_s_token = s_token
        self.m_s_corp_id = s_corp_id

    def verify_url(self, s_msg_signature, s_time_stamp, s_nonce, s_echo_str):
        """Verify URL"""
        if sys.version_info < (3, 0):
            (s_msg_signature, s_time_stamp, s_nonce, s_echo_str) = map(str2bytes, (
                s_msg_signature, s_time_stamp, s_nonce, s_echo_str))
        else:
            (s_msg_signature, s_time_stamp, s_nonce, s_echo_str) = list(map(str2bytes, (
                s_msg_signature, s_time_stamp, s_nonce, s_echo_str)))
        sha1 = SHA1()
        ret, signature = sha1.get_sha1(self.m_s_token,
                                       s_time_stamp, s_nonce, s_echo_str)
        if ret != 0:
            return ret, None
        if not signature == s_msg_signature:
            return WX_BIZ_MSG_CRYPT_VALIDATE_SIGNATURE_ERROR, None
        prpcrypt = Prpcrypt(self.key)
        ret, s_reply_echo_str = prpcrypt.decrypt(s_echo_str, self.m_s_corp_id)
        return ret, s_reply_echo_str

    def encrypt_msg(self, s_reply_msg, s_nonce, timestamp=None):
        """Encrypt Msg"""
        if sys.version_info < (3, 0):
            (s_reply_msg, s_nonce, timestamp) = map(str2bytes, (s_reply_msg, s_nonce, timestamp))
        else:
            (s_reply_msg, s_nonce, timestamp) = list(
                map(str2bytes, (s_reply_msg, s_nonce, timestamp)))
        pc = Prpcrypt(self.key)
        ret, encrypt = pc.encrypt(s_reply_msg, self.m_s_corp_id)
        if ret != 0:
            return ret, None
        if timestamp is None:
            timestamp = str(int(time.time()))
        # 生成安全签名
        sha1 = SHA1()
        ret, signature = sha1.get_sha1(self.m_s_token, timestamp, s_nonce, encrypt)
        if ret != 0:
            return ret, None
        xml_parse = XMLParse()
        return ret, xml_parse.generate(encrypt, signature, timestamp, s_nonce)

    def decrypt_msg(self, s_post_data, s_msg_signature, s_time_stamp, s_nonce):
        """Decrypt Msg"""
        if sys.version_info < (3, 0):
            (s_post_data, s_msg_signature, s_time_stamp, s_nonce) = map(str2bytes, (
                s_post_data, s_msg_signature, s_time_stamp, s_nonce))
        else:
            (s_post_data, s_msg_signature, s_time_stamp, s_nonce) = list(map(str2bytes, (
                s_post_data, s_msg_signature, s_time_stamp, s_nonce)))
        xml_parse = XMLParse()
        ret, encrypt, touser_name = xml_parse.extract(s_post_data)
        if ret != 0:
            return ret, None
        sha1 = SHA1()
        ret, signature = sha1.get_sha1(self.m_s_token, s_time_stamp, s_nonce, encrypt)
        if ret != 0:
            return ret, None
        if not signature == s_msg_signature:
            return WX_BIZ_MSG_CRYPT_VALIDATE_SIGNATURE_ERROR, None
        pc = Prpcrypt(self.key)
        ret, xml_content = pc.decrypt(encrypt, self.m_s_corp_id)
        return ret, xml_content
