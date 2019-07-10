from distutils.core import setup

setup(name='cesmd',
      version='0.1dev',
      description='USGS ComCat search API in Python',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      packages=['cesmd'],
      install_requires=['requests'],
      entry_points={
          'console_scripts': ['getrecords=bin.getrecords.command_line:main']},
      scripts=['bin/getrecords'],
      )
