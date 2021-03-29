from bs4 import BeautifulSoup

with open("page.html") as content:
    soup = BeautifulSoup(fp, "html.parser")
