# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 05:40:52 2023

@author: Nadzmi Ag Thomas
"""

# ================
# Import libraries
import requests  # For HTTP request and fetching html document
from bs4 import BeautifulSoup, NavigableString  # For parsing the html document
from urllib.parse import urljoin  # Joing base url and relative url
import pandas as pd  # Storing the data
import time  # For pausing between scraping
from stqdm import stqdm  # Progress bar

# ================
# Define function

# Turn link's content into soup


def get_soup(link):
    res = requests.get(link)
    htmlData = res.content
    soup = BeautifulSoup(htmlData, "html.parser")
    return soup

# Get all contents between two tags


def get_between_tags(start_tag, end_tags, find_tag=None, cleaner=None):
    lst = []
    tag = start_tag
    while tag not in end_tags:
        if find_tag == None:
            lst.append(tag)
        elif tag.name == find_tag:
            lst.append(tag)
        else:
            pass
        tag = tag.find_next()
    if cleaner:
        lst = cleaner(lst)
    return lst

# Get the next h2 tags or the navigation div


def get_end_tags(start_tag):
    if start_tag:
        end_tag1 = start_tag.find_next("h2")
        end_tag2 = start_tag.find_next("div", role="navigation")
        end_tags = [end_tag1, end_tag2]
        return end_tags
    else:
        return [None]

# Turn list of li into list text


def texify(lst):
    if lst:
        return list(map(lambda x: x.text, lst))
    return lst

# Turn li to link


def li_to_link(li, base_url):
    try:
        li = urljoin(base_url, li.a.get("href"))
    except:
        pass
    return li

# Turn list of li (with href) into list link


def linkify(lst, base_url):
    if lst:
        return list(map(lambda x: li_to_link(x, base_url), lst))
    return lst

# Scrape wikipedia page and return dictionary


def scrape_page(link):
    soup = get_soup(link)

    return_vals = {
        "Title": "", "Link": link, "Description": "", "Information": "",
        "See Also Text": [], "See Also Link": [], "References": [],
        "Bibliographies": [], "Further Reading": [],
        "External Links": [], "External Links Text": []
    }

    # Get the title
    title = soup.find(class_="mw-page-title-main").text
    return_vals["Title"] = title

    # Get the contents
    content = soup.select_one(
        "#mw-content-text > div.mw-content-ltr.mw-parser-output")

    # Get the description
    description = content.find("h2").find_all_previous("p")
    description = texify(description)
    description = "\n".join(description)
    return_vals["Description"] = description

    # Get the information
    information = ""
    # Stop adding to info when these are encountered:
    stop = ["See also[edit]", "References[edit]", "Bibliography[edit]",
            "Further reading[edit]", "External links[edit]"]
    skip = ["figure", "table", "style"]  # Skip these
    start = content.find("h2").previous_sibling

    for sibling in start.next_siblings:
        current_text = sibling.text
        tag_name = sibling.name

        if current_text in stop:
            break
        if not isinstance(sibling, NavigableString) and sibling.role == "Navigation":
            break
        if tag_name in skip:
            continue

        if tag_name:
            if tag_name[0] == 'h':
                current_text = '>'*(int(tag_name[1]) - 1) + ' ' + current_text

            elif tag_name in ["ul", "ol"]:
                temp = ''
                for text in current_text.split('\n'):
                    temp += '- ' + text + '\n'
                current_text = temp

            elif tag_name == "blockquote":
                current_text = '"' + current_text + '"\n'
        information += current_text
        return_vals["Information"] = information

    # Get see also
    start_tag = content.find(id="See_also")
    if start_tag:
        end_tags = get_end_tags(start_tag)
        see_alsos = get_between_tags(start_tag, end_tags, "li")
        return_vals["See Also Text"] = texify(see_alsos)
        return_vals["See Also Link"] = linkify(see_alsos, link)

    # Get references
    references = []
    start_tag = content.find(id="References")
    if start_tag:
        end_tags = get_end_tags(start_tag)
        references = get_between_tags(start_tag, end_tags, "li", texify)

        for ind, string in enumerate(references):
            references[ind] = f'[{ind + 1}] {string[2:]}'
        return_vals["References"] = references

    # Get bibliographies
    bibliographies = []
    start_tag = content.find(id="Bibliography")
    if start_tag:
        end_tags = get_end_tags(start_tag)
        bibliographies = get_between_tags(start_tag, end_tags, "li", texify)
        return_vals["Bibliograhies"] = bibliographies

    # Get further readings
    further_readings = []
    start_tag = content.find(id="Further_reading")
    if start_tag:
        end_tags = get_end_tags(start_tag)
        further_readings = get_between_tags(start_tag, end_tags, "li", texify)
        return_vals["Further Reading"] = further_readings

    # Get external links
    external_links = []
    start_tag = content.find(id="External_links")
    if start_tag:
        end_tags = get_end_tags(start_tag)
        external_links = get_between_tags(start_tag, end_tags, "li")
        return_vals["External Links"] = linkify(external_links, link)
        return_vals["External Links Text"] = texify(external_links)

    return return_vals

# Scrape wikipedia pages and turn dataframe


def wikipedia_links_to_df(data):
    if isinstance(data, list):  # If not DataFrame
        temp = {"link": data}
    else:
        temp = data.to_dict('list')

    n = len(temp['link'])  # Number of pages
    if n <= 0:
        return None

    output = scrape_page(temp['link'][0])
    for key, val in output.items():
        temp[key] = [val]

    time.sleep(1)

    for i in stqdm(range(1, n), desc="Scraping... ", initial=1, total=n,
                   bar_format='{percentage:.0f}%'):
        output = scrape_page(temp['link'][i])
        time.sleep(1)
        for key, val in output.items():
            temp[key].append(val)

    temp = pd.DataFrame.from_dict(temp).drop("link", axis=1)
    return temp
