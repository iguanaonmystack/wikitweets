import sys
from distutils.core import setup

version = '1.0'

setup(name='MPs_Edits',
      version=version,
      description='A bot that tracks edits to MPs\' articles on Wikipedia',
      author='Nick Murdoch',
      author_email='mps_edits@nivan.net',
      url='https://github.com/flexo/mps_edits',
      packages=['mps_edits'],
      install_requires=[
        'python-twitter',
        'twisted',
      ],
      entry_points={
        'console_scripts': ['mps_edits = mps_edits.client:main'],
      },
     )
