from datetime import datetime

from lxml import html


def join(strings):
    return ''.join(str(x.strip()) for x in strings)


def parse_date(text):
    pattern = '%Y-%m-%d' if ('-' in text) else '%d.%m.%Y'
    return datetime.strptime(text, pattern)


def parse_events(text):
    root = html.fromstring(text)

    rows = root.xpath('//table[contains(@id,"GridInfo")]/tr')

    data = ({
        'date': parse_date(join(row.xpath('td[1]//text()'))),
        'event': join(row.xpath('td[2]//text()')),
        'place': join(row.xpath('td[3]//text()'))
    } for row in rows if not row.xpath('th'))

    return sorted(data, key=lambda k: k["date"])
