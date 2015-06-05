import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.httpclient
import tornado.gen
import json

from tornado.options import define, options
define('port', default = 8967, help = "run on the given port", type = int)

'''class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, 'http://www.weibo.cn')
        self.write('hello, world')
        self.finish()'''

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        try:
            ipAddr = self.request.headers['X-Forwarded-For']
        except KeyError:
            ipAddr = self.request.remote_ip

        client = tornado.httpclient.AsyncHTTPClient()
        geoIpResponse = yield tornado.gen.Task(client.fetch, 'https://freegeoip.net/json/' + ipAddr)
        geoInfo = json.loads(geoIpResponse.body.decode('utf-8'))
        latitude, longitude = str(geoInfo['latitude']), str(geoInfo['longitude'])
        weatherResponse = yield tornado.gen.Task(client.fetch, 'http://api.openweathermap.org/data/2.5/forecast/daily?mode=json&cnt=1&' + 'lon=' + longitude + '&lat=' + latitude)
        weatherInfo = json.loads(weatherResponse.body.decode('utf-8'))
        weather = int(weatherInfo['list'][0]['weather'][0]['id'])
        umbrella = [200, 201, 202, 210, 211, 212, 221, 230, 231, 232, 300, 301, 302, 310, 311, 312, 313, 314, 321, 500, 501, 502, 503, 504, 511, 520, 521, 522, 531, 600, 601, 602, 611, 612, 615, 616, 620, 621, 622, 781, 900, 901, 902, 906]
        if weather in umbrella:
            self.write('记得带伞')
        else:
            self.write(str(weather) + '不用带伞')
        self.finish()

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [
            (r'^/$', IndexHandler),    
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()