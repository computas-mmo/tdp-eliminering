from bs4 import BeautifulSoup

# global constant instead of duplicating literals
MACRO = 'ac:structured-macro'
PARAMETER = 'ac:parameter'
NAME = 'ac:name'

with open("page.html") as page:
    soup = BeautifulSoup(page, "html.parser")
    # print(soup.prettify())
    for macro in soup.find_all(name=MACRO, attrs={NAME: "tdp-fragment"}):
        print("hi\n")
        print(macro.prettify())
        macro[NAME] = 'multiexcerpt'
        macro.find(PARAMETER, attrs={NAME: 'key'})[NAME] = 'name'
