from lxml import html


def parse_events(text):
    root = html.fromstring(text)
    data = root.xpath('//tr/td//text()')
    s = '\n'.join([str(x) for x in data])
    print(text)
    return s
