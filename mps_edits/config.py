"config.py - config options reader for mps_edits"
import os
import codecs
import ConfigParser

class TwitterConfig(object):
    """Twitter config options."""
    def __init__(self, parser):
        self.consumer_key = parser.get('twitter', 'consumer_key')
        self.consumer_secret = parser.get('twitter', 'consumer_secret')
        self.access_token_key = parser.get('twitter', 'access_token_key')
        self.access_token_secret = parser.get('twitter', 'access_token_secret')

class IRCConfig(object):
    """Wikimedia IRC config options."""
    def __init__(self, parser):
        self.server = parser.get('irc', 'server')
        self.port = parser.getint('irc', 'port')
        self.channel = parser.get('irc', 'channel')
        self.nick = parser.get('irc', 'nick')

class MPsConfig(set):
    """Subclass of set containing MPs to check."""
    def __init__(self, parser, relpath):
        super(MPsConfig, self).__init__()
        mps_filename = os.path.abspath(
            os.path.expanduser(parser.get('mps', 'file', {'here': relpath})))
        for line in codecs.open(mps_filename, 'r', 'utf-8'):
            line = line.strip()
            if line and not line.startswith('#'):
                self.add(line)

class Config(object):
    """Main config class."""
    def __init__(self, filename):
        relpath = os.path.dirname(filename)
        parser = ConfigParser.SafeConfigParser()
        parser.read(filename)

        self.irc = IRCConfig(parser)
        self.twitter = TwitterConfig(parser)
        self.mps = MPsConfig(parser, relpath)

