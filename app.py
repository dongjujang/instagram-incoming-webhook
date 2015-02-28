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
    self.write('')
    self.finish()

class MediaHandler(SentryMixin, tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def post(self):
    valid = True
    status_code = 200
    keys = ['user_id',
            'media_id',
            'username',
            'link',
            'image',
            'text',
            'created_time']
    doc = {}
    for key in keys:
      value = self.get_argument(key, None)
      if key == 'text' and not value:
        pass
      else:
        if not value:
          valid = False
          break
      if key == 'link':
        value = value.replace('http://instagram.com/p/', '')
        value = value.replace('https://instagram.com/p/', '')
        value = value.replace('/', '')
      doc[key] = value

    if not valid:
      status_code = 400
    else:
      collection = DB[doc['user_id']]
      found_doc = collection.find_one({'media_id': doc['media_id']})
      if not found_doc:
        collection.insert(doc)

    self.set_status(status_code)
    self.set_header('Content-Type', 'application/json')
    self.write('')
    self.finish()

class CommentHandler(SentryMixin, tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def post(self):
    valid = True
    status_code = 200
    keys = ['media_user_id',
            'media_id',
            'user_id',
            'username',
            'text',
            'created_time']
    doc = {}
    for key in keys:
      value = self.get_argument(key, None)
      if not value:
        valid = False
        break
      doc[key] = value

    if not valid:
      status_code = 400
    else:
      collection = DB[doc['user_id']]
      found_doc = collection.find_one({'media_id': doc['media_id']})
      if not found_doc:
        pass
      comments = found_doc.get('comments', [])
      exist = False
      for comment in comments:
        if comment.get('created_time', '') == doc['created_time']:
          exist = True
          break
      if exist:
        pass
      comments.append({'user_id': doc['user_id'],
                       'username': doc['username'],
                       'text': doc['text'],
                       'created_time': doc['created_time']})
      comments = sorted(comments, key=lambda x: x['created_time'], reverse=True)
      found_doc['comments'] = comments
      collection.update({'media_id': doc['media_id']}, found_doc)
    
    self.set_status(status_code)
    self.set_header('Content-Type', 'application/json')
    self.write('')
    self.finish()

application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/media', MediaHandler),
    (r'/comment', CommentHandler),
])

application.sentry_client = AsyncSentryClient(os.environ.get('SENTRY_API_KEY', ''))

if __name__ == '__main__':
  port = os.environ.get('PORT', 8888)
  application.listen(port)
  tornado.ioloop.IOLoop.instance().start()
