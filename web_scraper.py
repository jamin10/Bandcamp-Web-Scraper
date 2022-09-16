# Bandcamp Web Scraper

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os


def scrape_label_webpage(label):

    def generate_soup_object(label_link):
        # Send request for webpage HTML
        webpage_response = requests.get(label_link)
        webpage = webpage_response.content

        # Convert HTML to BeautifulSoup object
        webpage_soup = BeautifulSoup(webpage, "html.parser")
        return webpage_soup

    def get_label_title(webpage_soup):
        # Find the title of each webpage
        record_label_header = webpage_soup.find('title')
        record_label_header_text = record_label_header.get_text()
        record_label_title = record_label_header_text.partition('| ')[2]
        return record_label_title

    def get_music_info(webpage_soup):
        # Find all elements in an ol with class=title and add to a list
        title_list = []
        artist_list = []
        music_grid = webpage_soup.find('ol', {'id', 'music-grid'})
        for release in music_grid.find_all(attrs={'class':'title'}):
            # Split up elements into a list
            release_text = release.get_text('|').split('|')
            # Sometimes only has a track title so specify no artist
            # Add to title and artist lists
            if len(release_text) > 1:
                title_list.append(release_text[0])
                artist_list.append(release_text[1])
            else:
                title_list.append((release_text[0]))
                artist_list.append("none")

        # Use strip to remove spaces and add to new list
        strip_title_list = []
        for el in title_list:
            strip_title_list.append(el.strip())
        strip_artist_list = []
        for ele in artist_list:
            strip_artist_list.append(ele.strip())

        # Add lists to a dictionary
        label_dict["Artist"] = strip_artist_list
        label_dict["Title"] = strip_title_list

    def get_links(webpage_soup):
        # Find links to release pages and add to list
        links_list = []
        music_grid_links = webpage_soup.find('ol', {'id', 'music-grid'})
        for link in music_grid_links.find_all('a'):
            # use urljoin to provide full link not just relative
            links_list.append(urljoin(label, link.get('href')))

        # Add list to dictionary
        label_dict["Link"] = links_list

    # Create dictionary that will be returned
    label_dict = {}

    # Call functions
    webpage_soup = generate_soup_object(label)
    record_label_title = get_label_title(webpage_soup)
    get_music_info(webpage_soup)
    get_links(webpage_soup)

    return record_label_title, label_dict


def create_dataframe(label_dict):
    # Create a DataFrame from dictionary
    label_DF = pd.DataFrame({
        "Artist": label_dict["Artist"], "Title": label_dict["Title"], "Link": label_dict["Link"]
    })
    return label_DF


def write_to_excel(all_labels, file_path):
    # Write dictionary to excel
    with pd.ExcelWriter(file_path) as writer:
        for label_title, label_music in all_labels.items():
            label_music.to_excel(writer, sheet_name = label_title, index=False)


# Create the file path where spreadsheet should be stored
cwd = os.getcwd()
if not os.path.exists(os.path.join(cwd, 'results')):
    os.makedirs('results')

file_path = os.path.join(cwd, 'results', 'spreadsheet.xlsx')

# Input list of record labels
LABELS = ['https://wisdomteethuk.bandcamp.com/', 'https://livitysound.bandcamp.com/', 'https://music.hessleaudio.com/']

# Create a dictionary of DataFrames
all_labels = {}

# Loop through labels in list
for label in LABELS:
    record_label_title, label_dict = scrape_label_webpage(label)
    label_DF = create_dataframe(label_dict)

    # Add each DataFrame to dictionary
    all_labels[record_label_title] = label_DF

write_to_excel(all_labels, file_path)