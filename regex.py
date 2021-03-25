# Queries cannot use multi-line strings :(
FRAGMENT_SEARCH = r'<ac:structured-macro ac:name="tdp-fragment" ac:schema-version="1" ac:macro-id="([a-z0-9-]+)">' + \
                  r'<ac:parameter ac:name="key">(.+?)' + \
                  r'</ac:parameter><ac:rich-text-body>'

FRAGMENT_REPLACE = r'<ac:structured-macro ac:name="multiexcerpt-macro" ac:schema-version="1" ac:macro-id="\1">' + \
                   r'<ac:parameter ac:name="name">\2' + \
                   r'</ac:parameter><ac:rich-text-body>'

FRAGMENT_INCLUDE_SEARCH = r'<ac:structured-macro ac:name="tdp-fragment-include" ac:schema-version="1" ac:macro-id="([a-z0-9-]+)">' + \
                 r'(?:<ac:parameter ac:name="header">false</ac:parameter>)?' + \
                 r'(?:<ac:parameter ac:name="pagecontext">(?:true|false)</ac:parameter>)?' + \
                 r'<ac:parameter ac:name="page"><ac:link><ri:page ri:content-title="(.+?)"\ /></ac:link></ac:parameter>' + \
                 r'(?:<ac:parameter ac:name="text">.+?</ac:parameter>)?' + \
                 r'(?:<ac:parameter ac:name="panel">(true|false)</ac:parameter>)?' + \
                 r'<ac:parameter ac:name="key">(.+?)</ac:parameter>' + \
                 r'(?:<ac:parameter ac:name="searchable">(?:true|false)</ac:parameter>)?' + \
                 r'(?:<ac:parameter ac:name="expandrelative">(?:true|false)</ac:parameter>)?' + \
                 r'</ac:structured-macro>'

FRAGMENT_INCLUDE_REPLACE = r'<ac:structured-macro ac:macro-id="\1" ac:name="multiexcerpt-include-macro" ac:schema-version="1">' + \
                  r'<ac:parameter ac:name="name">\4</ac:parameter>' + \
                  r'<ac:parameter ac:name="page">' + \
                  r'<ac:link>' + \
                  r'<ri:page ri:content-title="\2" />' + \
                  r'</ac:link>' + \
                  r'</ac:parameter>' + \
                  r'<ac:parameter ac:name="addpanel">true</ac:parameter>' + \
                  r'</ac:structured-macro>'
