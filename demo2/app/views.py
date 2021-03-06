# -*- coding: UTF-8 –*-
# Create your views here.

from flask import request, jsonify, render_template

from demo2.app import APP
from demo2.app import config
from wechat.component import WxComponentApplication, WxComponentApi
from wechat.official import WxApplication, WxApi, WxTextResponse
from wechat.token_manager import RedisTokenManager, LocalTokenManager
from wechat.crypt import Sign

class WxApp(WxApplication):
    """把用户输入的文本原样返回。
    """

    SECRET_TOKEN = config.TOKEN
    APP_ID = config.APP_ID
    ENCODING_AES_KEY = config.ENCODING_AES_KEY

    def on_text(self, req):
        return WxTextResponse(req.Content, req)


@APP.route('/')
def wechat():
    app = WxApp()
    result = app.process(request.args, request.data)
    return result


wxapi = WxApi(
    config.APP_ID,
    config.APP_SECRET,
    # LocalTokenManager()
    RedisTokenManager(
        host=getattr(config, 'REDIS_HOST'),
        port=getattr(config, 'REDIS_PORT'),
        db=getattr(config, 'REDIS_DB', 0))
)


@APP.route('/admin')
def admin():
    menu = wxapi.get_menu()
    return jsonify(menu)


@APP.route('/admin/jsapitk')
def jsapitk():
    jsapitk = wxapi.jsapi_ticket
    print(wxapi.access_token)
    print(jsapitk)
    return render_template('index.html', signature={})


@APP.route('/wechat/weui')
def weui():
    """The view for test weui"""

    # 注意 URL 一定要动态获取，不能 hardcode
    print('url:', request.url)
    jsapitk = wxapi.jsapi_ticket
    print(jsapitk)
    sign = Sign(jsapitk[0]['ticket'], request.url)
    print(sign.sign())

    return render_template('index.html', signature=sign.sign())



@APP.route('/admin/apitk')
def apitk():
    apitk = wxapi.api_ticket
    print(wxapi.access_token)
    print(apitk)
    return jsonify(apitk)


@APP.route('/admin/token')
def token():
    access_token = wxapi.access_token
    print(access_token)
    return jsonify(access_token)


class WxComponentApp(WxComponentApplication):
    SECRET_TOKEN = config.TOKEN
    APP_ID = config.APP_ID
    ENCODING_AES_KEY = config.ENCODING_AES_KEY

    def on_verify_ticket(self, event):
        verify_ticket = event.get('ComponentVerifyTicket')
        print("接收到的verify_ticket: %s", verify_ticket)
        # cache.set('verify_ticket', verify_ticket)


@APP.route('/auth/event')
def auth_event():
    app = WxComponentApp()
    rsp = app.process(request.args, request.data)
    return rsp

# class WxComApi(WxComponentApi):
#     COMPONENT_APP_ID = ''
#     COMPONENT_APP_SECRET = ''
#
#
# def component_access_token_api(request):
#     verify_ticket = cache.get('verify_ticket')
#     if not verify_ticket:
#         verify_ticket = "verify_ticket为空, 请先获取verify_ticket"
#
#     api = WxComApi()
#     content, error = api.get_component_access_token(verify_ticket)
#     if content:
#         access_token = content.get('component_access_token')
#         cache.set('component_access_token', access_token)
#         content = json.dumps(content)
#     print('component_access_token: %s', content)
#     if error:
#         print('获取component_access_token失败: %s, %s', error.code, error.message)
#     return HttpResponse(content)
#
#
# def pre_auth_code_api(request):
#     access_token = cache.get('component_access_token')
#     if not access_token:
#         return HttpResponse("component_access_token为空, 请先获取component_access_token")
#
#     api = WxComApi()
#     content, error = api.get_pre_auth_code(access_token)
#     if content:
#         pre_auth_code = content.get('pre_auth_code')
#         cache.set('pre_auth_code', pre_auth_code)
#         content = json.dumps(content)
#     print('pre_auth_code: %s', content)
#     if error:
#         print('获取pre_auth_code失败: %s, %s', error.code, error.message)
#     return HttpResponse(content)
#
#
# def authorize(request):
#     """
#     授权演示页面
#     """
#     pre_auth_code = cache.get('pre_auth_code')
#     if not pre_auth_code:
#         return HttpResponse("pre_auth_code为空, 请先获取pre_auth_code")
#
#     html = """
#         <html>
#             <head>
#                 <title>公众号第三方平台授权</title>
#             </head>
#             <body>
#                 <a href='%s'>微信授权</a>
#             </body>
#         </html>
#         """
#
#     redirect_url = "http://%s%s" % (request.get_host(), reverse('save_authorization_info'))
#     api = WxComApi()
#     authorization_age = api.get_authorization_page(pre_auth_code, redirect_url)
#     html = html % (authorization_age)
#     return HttpResponse(html)
#
#
# def save_authorization_info(request):
#     """
#     用户授权成功
#     """
#     access_token = cache.get('component_access_token')
#     if not access_token:
#         return HttpResponse("component_access_token为空, 请先获取component_access_token")
#
#     print("request.GET: %r", request.GET)
#     auth_code = request.GET.get("auth_code", None)
#
#     api = WxComApi()
#     content, error = api.get_authorization_info(auth_code, access_token)
#     if content:
#         content = json.dumps(content)
#     print('authorization_info: %s', content)
#     if error:
#         print('获取授权信息失败: %s, %s', error.code, error.message)
#     return HttpResponse(content)
