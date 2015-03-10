"""client.py - client for MPs_Edits"""
import re
import sys
import time
import logging

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log as twisted_log

log = logging.getLogger(__name__)

def configure_logging():
    """Set up logger, handler, and formatter."""
    log.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to log
    log.addHandler(ch)

class EditsListener(irc.IRCClient):
    """IRC bot that listens to wikipedia edits."""
    
    nickname = "mps_edits"
    edit_re = re.compile(
        r'^\x0314\[\[\x0307'    # <grey>[[<yellow>
        r'([^\x03]*)'           # Article name
        r'\x0314\]\]'           # <grey>]]
        r'\x034 \x0310 \x0302'  # <?><?><blue>
        r'([^\x03]*)')          # Diff URI
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        log.info("connected")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        log.info("disconnected")

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        log.info('signed on')
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        msg = msg.decode('utf-8')

        if user == 'rc-pmtpa':
            # TODO - check for channel ops instead
            log.debug(u"Incoming message: %s", msg)
            m = self.edit_re.match(msg)
            if m is not None:
                article = m.group(1)
                diffuri = m.group(2)
                log.info(u"%s Wikipedia article edited %s", article, diffuri)

    def alterCollidedNick(self, nickname):
        """Generate an altered version of a nickname that caused a collision
        to create an unused related name for subsequent registration."""
        return nickname + '_'


class EditsListenerFactory(protocol.ClientFactory):
    """A factory for EditsListeners.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel):
        self.channel = channel

    def buildProtocol(self, addr):
        p = EditsListener()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    twisted_log.startLogging(sys.stdout)
    configure_logging()
    log.debug('Starting up')
    
    # create factory protocol and application
    f = EditsListenerFactory('#en.wikipedia')

    # connect factory to this host and port
    reactor.connectTCP("irc.wikimedia.org", 6667, f)

    # run bot
    reactor.run()
