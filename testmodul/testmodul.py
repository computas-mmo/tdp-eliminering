from bs4 import BeautifulSoup

# global constant instead of duplicating literals
MACRO = 'ac:structured-macro'
PARAMETER = 'ac:parameter'
NAME = 'ac:name'

with open("page.html") as page:
    soup = BeautifulSoup(page, "html.parser")
    print("open page.html")
    diff = False
    # TDP Fragment -> MultiExcerpt
    for macro in soup.find_all(name='ac:structured-macro', attrs={NAME: 'tdp-fragment'}):
        macro[NAME] = 'multiexcerpt'
        macro.find(PARAMETER, attrs={NAME: 'key'})[NAME] = 'MultiExcerptName'

        diff = True

    # TDP Fragment Include -> MultiExcerpt Include
    for macro in soup.find_all(name='ac:structured-macro', attrs={NAME: 'tdp-fragment-include'}):
        macro[NAME] = 'multiexcerpt-include'
        macro.find(PARAMETER, attrs={NAME: 'key'})[NAME] = 'MultiExcerptName'

        # Optional panel argument for multiexcerpt-include
        panel = macro.find(PARAMETER, attrs={NAME: 'panel'})
        if panel is not None:
            panel[NAME] = 'addpanel'

        # Remove all other arguments
        for option in ('header', 'pagecontext', 'text', 'searchable', 'expandrelative'):
            for tag in macro.find_all(PARAMETER, attrs={NAME: option}):
                tag.decompose()

        diff = True


    if diff:
        print("Diff found, trying to update new_page.html")
        open("new_page.html", "w").write(soup.decode(formatter="html"))
    else:
        print("No diff found, page is unchanged.")
