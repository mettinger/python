import tornado.ioloop
import tornado.web
import sqlite3

#databasePath = '/home/ubuntu/github/python/buttonApp/two_buttons.db'
databasePath = '/home/ubuntu/github/python/buttonApp_2/app.db'

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
            timestamp, button_id, info, user_id = thisData.split("-")
            #cur.execute("INSERT INTO button_press VALUES ('%s',%s, '%s')" % (timestamp.strip(),button_id,info.strip()))
            cur.execute("INSERT INTO button_data (timestamp, button_id, user_id, info) VALUES ('%s',%s, %s, '%s')" %(timestamp.strip(), button_id, user_id, info.strip()))
        except:
            print("Error: ")
            print(thisData)
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