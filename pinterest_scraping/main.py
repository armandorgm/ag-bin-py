import os
import requests
from bs4 import BeautifulSoup
from pprint import pprint

os.system("cls")

# https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
url = "https://www.pinterest.es/pin/11329436556590513/"
html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")
# Encuentra el elemento de video utilizando el selector CSS proporcionado
video_element = soup.select_one("body")
pprint(video_element)
