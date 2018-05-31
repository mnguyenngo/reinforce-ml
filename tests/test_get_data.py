""" Tests for get_data.py
"""

import unittest as unittest
import requests
from bs4 import BeautifulSoup
from src import get_data


class Test(unittest.TestCase):
    def test_main(self):
        book_url = ('https://en.wikipedia.org/wiki/'
                    'Book:Machine_Learning_%E2%80%93_The_Complete_Guide')
        response = requests.get(book_url)
        html = response.content
        self.assertEqual(type(html), bytes)
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(type(soup), BeautifulSoup)
        return soup

    def test_parse_sec(self):
        soup = self.test_main()
        sections = soup.select('dl')
        dds = get_data.parse_sec(sections[0])
        self.assertEqual(type(dds), list)
        self.assertEqual(type(dds[0]), dict)
        self.assertEqual('title' in dds[0].keys(), True)
        return dds

    def test_add_definition(self):
        baseurl = 'https://en.wikipedia.org'
        dds = self.test_parse_sec()
        dds_with_def = get_data.add_definition(dds[0])
        self.assertEqual('definition' in dds_with_def.keys(), True)

if __name__ == '__main__':
    unittest.main()
