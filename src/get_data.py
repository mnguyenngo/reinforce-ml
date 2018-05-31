import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def parse_sec(sec):
    """Get title and links and save as python dictionaries

    Arguments:
        sec (html): is a dl element
    Returns:
        parsed_dds: list of dictionaries
    """
    parsed_dds = []
    # dt is html term name element
    dt = sec.select_one('dt')
    if dt is not None:
        # title of section
        sec_title = dt.text
        # dd element is an html term element
        dds = sec.select('dd')
        if dds is not None:
            # get title and link information in a python dictionary
            parsed_dds = [parse_dd(dd, sec_title) for dd in dds]
    if len(parsed_dds) > 0:
        return parsed_dds


def parse_dd(dd, sec_title):
    """Get link and title data and returns in a python dictionary

    Arguments:
        dd (html): html term element
        sec_title (str): section title (title of dl)
    Returns:
        link_dict (dict): dictionary of link data
    """
    link = dd.select_one('a')
    if link is not None:
        attrs = link.attrs
        link_dict = {
            'title': attrs['title'],
            'href': attrs['href'],
            'section': sec_title
        }
        return link_dict


def add_definition(link_dict):
    """Add definitions to the dictionaries

    Arguments:
        link_dict (dict): dictionary of link data
    Returns:
        link_dict (dict): same dictionary except with dictionary data
    """
    # base url for wikipedia
    baseurl = 'https://en.wikipedia.org'

    if link_dict is not None:
        url = baseurl + link_dict['href']
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            div = soup.select_one('div.mw-parser-output')
            if div is not None:
                p_definition = div.select_one('p')
                if p_definition is not None:
                    definition = p_definition.text
                    link_dict['definition'] = definition
                    print("Got definition for {}.".format(link_dict['title']))
    return link_dict


if __name__ == '__main__':
    """Get links from book page and get definition from each link

    In terminal, run: `python get_data.py`
    """
    # url to wikipedia book on machine learning
    book_url = ('https://en.wikipedia.org/wiki/'
                'Book:Machine_Learning_%E2%80%93_The_Complete_Guide')

    # attribute placeholder
    # my_attr = {'format': 'json'}
    response = requests.get(book_url)

    if response.status_code == 200:
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        # dl is description list tag
        sections = soup.select('dl')

        parsed_links = []
        for sec in sections:
            # get section title and links in the section
            parsed_content = parse_sec(sec)
            if parsed_content is not None:
                parsed_links.extend(parsed_content)

        # remove none objects
        parsed_links = [d for d in parsed_links if d is not None]

        # go to each link and get first paragraph which will be the definition
        for link_dict in parsed_links:
            link_dict = add_definition(link_dict)

        # convert data to dataframe
        ml_def_df = pd.DataFrame(parsed_links)

        # get date that the script was run
        today = dt.datetime.today().strftime('%y%m%d')

        # save dataframe to pickle
        ml_def_df.to_pickle('../data/{}_def.pkl'.format(today))
