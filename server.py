import logging
import json
from uuid import uuid4

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler


def init_logging():
    logger = logging.getLogger('client')
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - [%(asctime)s] - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


class EchoWebSocketHandler(WebSocketHandler):
    def open(self):
        logger.info("WebSocket opened")

    def on_message(self, message):
        logger.info("Message received")
        assert json.loads(message)
        logger.info("Message validated: it's json")
        logger.info("Message: {}".format(json.loads(message)))
        echo = {
            'received': json.loads(message),
            'sent': {
                'message': 'Payload received {}'.format(str(uuid4()))
            }
        }
        self.write_message(json.dumps(echo))
        logger.info("Message answered")

    def on_close(self):
        logger.info("WebSocket closed")


class StatusHandler(RequestHandler):
    def get(self):
        self.write(json.dumps({'status': 'Cool bro'}))


def init_app():
    return Application([
        (r"/", EchoWebSocketHandler),
        (r"/status", StatusHandler),
    ])


if __name__ == "__main__":
    logger = init_logging()
    app = init_app()
    app.listen(80)
    IOLoop.current().start()
