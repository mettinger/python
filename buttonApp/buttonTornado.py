import tornado.ioloop
import tornado.web
import sqlite3

databasePath = '/home/ubuntu/github/python/buttonApp/two_buttons.db'

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("Hello, world")
        data = self.get_argument('data')
        putData(data)

def putData(data):
    conn = sqlite3.connect(databasePath)
    cur = conn.cursor()
    for thisData in data.split(','):
        try:
            timestamp, button_id = thisData.split("-")
            cur.execute("INSERT INTO button_press VALUES ('%s',%s)" % (timestamp.strip(),button_id))
        except:
            pass
    conn.commit()
    conn.close()
    
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8890)
    tornado.ioloop.IOLoop.current().start()