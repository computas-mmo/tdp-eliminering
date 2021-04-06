from bs4 import BeautifulSoup

# global constant instead of duplicating literals
MACRO = 'ac:structured-macro'
PARAMETER = 'ac:parameter'
NAME = 'ac:name'

with open("page.html") as page:
    soup = BeautifulSoup(page, "html.parser")
    print("open page.html")
    diff = False
    for macro in soup.find_all(name=MACRO, attrs={NAME: "tdp-fragment"}):
        print("do replacement of tdp-fragment")
        # print(macro.prettify())
        macro[NAME] = 'multiexcerpt'
        macro.find(PARAMETER, attrs={NAME: 'key'})[NAME] = 'name'
        diff = True

    if diff:
        print("Diff found, trying to update new_page.html")
        open("new_page.html", "a").write(soup.decode())
    else:
        print("No diff found, page is unchanged.")
