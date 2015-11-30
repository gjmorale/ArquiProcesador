import RSSFeed, NoRSS_reader, sapi_reader

RSSFeed.builder('RSS_sources.json')
NoRSS_reader.builder("NoRSS_sources.json")

STEP = 20
with open('sapilog.txt') as logfile:
    last_page = int(logfile.readline())
    new_last_page = last_page + STEP
sapi_reader.builder('sapi.json', limit=50, start=last_page, end=new_last_page)

with open('sapilog.txt', 'w') as logfile:
    logfile.write(str(new_last_page))
