import sys
from distutils.core import setup

version = '1.0'

setup(name='WikiTweets',
      version=version,
      description='A bot that tweets edits to a list of given articles on Wikipedia',
      author='Nick Murdoch',
      author_email='nick@nivan.net',
      url='https://github.com/flexo/wikitweets',
      packages=['wikitweets'],
      install_requires=[
        'python-twitter',
        'twisted',
      ],
      entry_points={
        'console_scripts': ['wikitweets = wikitweets.client:main'],
      },
     )
