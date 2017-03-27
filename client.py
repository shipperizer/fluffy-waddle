import asyncio
import os
import json
import sys
from datetime import datetime
import logging

from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory


def init_logging():
    logger = logging.getLogger('client')
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - [%(asctime)s] - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


class ClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        def noise():
            self.sendMessage(json.dumps({'message': 'Opening trial'}).encode('utf8'))
            self.factory.reactor.callLater(15, noise)
        noise()

    def onMessage(self, payload, isBinary):
        logger.info("Message received")
        assert json.loads(payload.decode('utf8'))
        logger.info("Message validated: it's json")
        logger.info(json.loads(payload.decode('utf8')))
        if datetime.now().second % 30 == 0:
          noise = {'message': 'Payload received'}
          self.sendMessage(json.dumps(noise).encode('utf8'))
          logger.info("Send some noise every 30s")


class ClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = ClientProtocol

    def clientConnectionFailed(self, connector, reason):
        logger.info("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.error("Client connection lost .. retrying ..")
        self.retry(connector)


if __name__ == '__main__':
   logger = init_logging()

   log.startLogging(sys.stdout)

   factory = ClientFactory()
   factory.protocol = ClientProtocol

   reactor.connectTCP(os.environ['SERVER_HOST'], 80, factory)
   reactor.run()
