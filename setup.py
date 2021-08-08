from setuptools import setup, find_packages
import os

version = '0.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='raspi.lpd8806',
      version=version,
      description="Servers for playing predefined sequences "
                  "on a LPD8806 based LED strip connected to "
                  "a RaspberryPi.",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
        ],
      keywords='raspberry pi lpd8806',
      author='Daniel Havlik',
      author_email='dh@gocept.com',
      url='http://gocept.com',
      license='BSD',
      packages=find_packages('src', exclude=['ez_setup']),
      package_data={},
      package_dir={'': 'src'},
      namespace_packages=['raspi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'haigha==0.5.9',
          'mushroom==0.3.3',
          'requests==1.1.0',
          'gevent==0.13.8',
          'gevent-websocket==0.3.6'
      ],
      setup_requires=[
          'setuptools_hg'],
      entry_points={
        'console_scripts': [
            'led_webserver = raspi.lpd8806.led:main',
            'led_queue_worker = raspi.lpd8806.led_queue_worker:entry'],
        },
      )
