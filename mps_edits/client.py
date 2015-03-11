"""client.py - client for mps_edits"""
import re
import sys
import logging

import twitter # pip install python-twitter
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log as twisted_log

from . import config

log = logging.getLogger(__name__)

def configure_logging():
    """Set up logger, handler, and formatter."""
    log.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s')
    # add formatter to ch
    console_handler.setFormatter(formatter)
    # add ch to log
    log.addHandler(console_handler)

class EditsListener(irc.IRCClient):
    """IRC bot that listens to wikipedia edits."""
    edit_re = re.compile(
        r'^\x0314\[\[\x0307'    # <grey>[[<yellow>
        r'([^\x03]*)'           # Article name
        r'\x0314\]\]'           # <grey>]]
        r'\x034 \x0310 \x0302'  # <?><?><blue>
        r'([^\x03]*)')          # Diff URI
    ip_re = re.compile(
        r'^([0-9]{1,3}\.){3}[0-9]{1,3}$') # TODO - IPv6

    def __init__(self, cfg, twitter_api):
        self.nickname = cfg.irc.nick
        self.mps = cfg.mps
        self.twitter = twitter_api

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
                author = '[unknown]' # TODO
                log.debug(u"Noticed edit of %s", article)
                if article in self.mps:
                    by_msg = 'anonymously'
                    if not self.ip_re.match(author):
                        by_msg = 'by %s' % author
                    # TODO shorten if >140 chars
                    self.twitter.PostUpdate(
                        u"%s Wikipedia article edited %s %s" % (
                            article, by_msg, diffuri))

    def alterCollidedNick(self, nickname):
        """Generate an altered version of a nickname that caused a collision
        to create an unused related name for subsequent registration."""
        return nickname + '_'


class EditsListenerFactory(protocol.ClientFactory):
    """A factory for EditsListeners.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, cfg, twitter_api):
        self.channel = cfg.irc.channel
        self.cfg = cfg
        self.twitter = twitter_api

    def buildProtocol(self, addr):
        proto = EditsListener(self.cfg, self.twitter)
        proto.factory = self
        return proto

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

def main():
    """Main entry point for mps_edits"""
    # initialise config
    cfg = config.Config(sys.argv[1])

    # initialise logging
    twisted_log.startLogging(sys.stdout)
    configure_logging()
    log.debug('Starting up')

    # initialise Twitter API connection
    twitter_api = twitter.Api(
        consumer_key=cfg.twitter.consumer_key,
        consumer_secret=cfg.twitter.consumer_secret,
        access_token_key=cfg.twitter.access_token_key,
        access_token_secret=cfg.twitter.access_token_secret)
    status = twitter_api.VerifyCredentials()
    log.info("Logged into twitter: %s", status.text)

    # create factory protocol and application
    f = EditsListenerFactory(cfg.irc.channel, twitter_api)

    # connect factory to this host and port
    reactor.connectTCP(cfg.irc.server, cfg.irc.port, f)

    # run bot
    reactor.run()

if __name__ == '__main__':
    sys.exit(main())
