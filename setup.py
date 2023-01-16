from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('screener_scraper/__init__.py').read(),
    re.M
    ).group(1)

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup( 
    name = 'screener_scraper', 
    packages = ['screener_scraper'], # this must be the same as the name above 
    version = version, 
    description = 'Scrapes company data from screener.in', 
    long_description = long_description,
    long_description_content_type='text/markdown',
    author = 'Feluda', 
    author_email = 'dummy@gmail.com', 
    url = 'https://github.com/adulef/scrneer_scraper', # use the URL to the github repo 
    download_url = 'https://github.com/adulef/scrneer_scraper/dist/' + version + '.tar.gz', 
    keywords = ['screener', 'scraping', 'scraper'],
    classifiers = [], 
    install_requires=[package.split("\n")[0] for package in open("requirements.txt", "r").readlines()]
)
