#%%
import requests
from bs4 import BeautifulSoup

# %%

URL = "https://www.rvtrader.com/Used-Travel-Trailer/rvs-for-sale?type=Travel%20Trailer%7C198073&condition=U&length=23%3A32&zip=05251&radius=400"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
# %%

from requests_html import HTMLSession
session = HTMLSession()
r = session.get(URL)


# %%
