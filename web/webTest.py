import tornado.ioloop
import tornado.web
import sqlite3

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("Hello, world")
        data = self.get_argument('data')
        putData(data)

def putData(data):
    conn = sqlite3.connect('two_buttons.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO test_table VALUES ('%s')" % data)
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