import os
import json
import pymongo
import tornado.ioloop
import tornado.web
from raven.contrib.tornado import AsyncSentryClient
from raven.contrib.tornado import SentryMixin

DB = pymongo.MongoClient("mongodb", 27017).instagram

class IndexHandler(SentryMixin, tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):
    self.set_header('Content-Type', 'application/json')
    response = {}
    self.write(json.dumps(response))
    self.finish()
      
  @tornado.web.asynchronous
  def post(self):
    isValid = True
    status_code = 200
    keys = ['user_id',
            'media_id',
            'username',
            'image',
            'text',
            'created_time']
    doc = {}
    for key in keys:
      value = self.get_argument(key, None)
      if not value:
        isValid = False
        break
      doc[key] = value

    if not isValid:
      status_code = 400
    else:
      collection = DB[doc['user_id']]
      collection.insert(doc)

    self.set_status(status_code)
    self.set_header('Content-Type', 'application/json')
    self.write('')
    self.finish()

application = tornado.web.Application([
    (r'/', IndexHandler),
])

application.sentry_client = AsyncSentryClient(os.environ.get('SENTRY_API_KEY', ''))

if __name__ == '__main__':
  port = os.environ.get('PORT', 8888)
  application.listen(port)
  tornado.ioloop.IOLoop.instance().start()