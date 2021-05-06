from setuptools import setup, find_packages


setup(
    name='twich',
    url='https://github.com/deepadmax/twich',
    author='Maximillian Strand',
    author_email='maximillian.strand@gmail.com',
    packages=find_packages(),
    install_requires=['requests', 'flask', 'websocket-client'],
    version='1.0',
    license='',
    description='Twich is a small library for interfacing with the Twitch API.',
    long_description=open('README.md').read(),
)