import json, base64, hashlib, time, re, requests
from urllib.parse import urlencode

class IPTV:
    def __init__(self):
        self.is_proxy = False
        self.proxy = {}
        self.headers = {'User-Agent': 'Mozilla/5.0', 'CLIENT-IP': '127.0.0.1', 'X-FORWARDED-FOR': '127.0.0.1'}
        self.h = ['50.7.92.106', '50.7.220.170', '67.159.6.34', '198.16.100.186', '50.7.234.10']
        self.d = 'W3siaWQiOiAiMDAxIiwgImZ1biI6ICJzbXQiLCAicGlkIjogIjEyMzQ1IiwgInR2Zy1pZCI6ICJ0djEiLCAidHZnLW5hbWUiOiAiVGVzdCIsICJ0dmctbG9nbyI6ICJodHRwczovL2xvZ28udHh0IiwgImdyb3VwLXRpdGxlIjogIuWkjeW4h+WkjeiDveWtmCIsICJuYW1lIjogIlRlc3QgQ2hhbm5lbCJ9XQ=='

    def getProxyUrl(self):
        return "/proxy?from=bot"

    def b64decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')

    def b64encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def liveContent(self, url):
        data_list = json.loads(self.b64decode(self.d))
        tv_list = ['#EXTM3U']
        for i in data_list:
            tvg_id = i['tvg-id']
            tvg_name = i['tvg-name']
            tvg_logo = i['tvg-logo']
            group_name = i['group-title']
            name = i['name']
            fun = i['fun']
            pid = i['pid']
            tv_list.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_name}",{name}')
            for ip in self.h:
                tv_list.append(f'{self.getProxyUrl()}&fun={fun}&pid={pid}&ip={ip}')
        return '\n'.join(tv_list)
        
    def homeContent(self, filter):
        return {}

    def homeVideoContent(self):
        return {}

    def categoryContent(self, cid, page, filter, ext):
        return {}

    def detailContent(self, did):
        return {}

    def searchContent(self, key, quick, page='1'):
        return {}

    def searchContentPage(self, keywords, quick, page):
        return {}

    def playerContent(self, flag, pid, vipFlags):
        return {}

    def localProxy(self, params):

        _fun = params.get('fun', None)
        _type = params.get('type', None)

        if _fun is not None:
            fun = getattr(self, f'fun_{_fun}')
            return fun(params)

        if _type is not None:
            if params['type'] == "m3u8":
                return self.get_m3u8_text(params)

            if params['type'] == "ts":
                return self.get_ts(params)

        return [302, "text/plain", None, {'Location': 'https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/mp4/xgplayer-demo-720p.mp4'}]
    def fun_smt(self, params):
        pid = params['pid']
        ip = params['ip']
        url = f'http://{ip}:8278/{pid}/playlist.m3u8'
        t = str(int(time.time() / 150))
        p = {
            'tid': 'mc42afe745533',
            'ct': t,
            'tsum': hashlib.md5(f'tvata nginx auth module/{pid}/playlist.m3u8mc42afe745533{t}'.encode('utf-8')).hexdigest()
        }
        play_url = self.b64encode(url + '?' + urlencode(p))
        url = f'{self.getProxyUrl()}&type=m3u8&url={play_url}'
        return [302, "text/plain", None, {'Location': url}]


    def get_m3u8_text(self,params):
        url = self.b64decode(params['url'])
        headers = self.headers
        home_url = url.replace(url.split('/')[-1], '')

        def callback_function(match):
            uri = home_url + match.group(1)
            a = self.b64encode(uri)
            # h = params['headers']
            return f"{self.getProxyUrl()}&type=ts&url={a}"
        if self.is_proxy:
            response = requests.get(url, headers=headers, proxies=self.proxy)
        else:
            response = requests.get(url, headers=headers)
        m3u8_text = re.sub(r'(.*\.ts.*)', callback_function, response.text)
        return [200, "application/vnd.apple.mpegurl", m3u8_text]

    def get_ts(self, params):
        url = self.b64decode(params['url'])
        headers = self.headers
        if self.is_proxy:
            response = requests.get(url, headers=headers, proxies=self.proxy)
        else:
            response = requests.get(url, headers=headers)
        return [206, "application/octet-stream", response.content]

    def destroy(self):
        return '正在Destroy'

    def b64encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def b64decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')

if __name__ == '__main__':
    pass
