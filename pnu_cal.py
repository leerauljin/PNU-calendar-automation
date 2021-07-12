#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ics import Calendar, Event
from retrying import retry
import requests
import lxml.html as lh


@retry(stop_max_attempt_number=5, wait_random_min=5000, wait_random_max=10000)
def request_url(url):
    page = requests.get(url)
    return page


try:
    with open('pnu_cal_db.txt', 'r') as file:
        db = [line.rstrip() for line in file]
except FileNotFoundError:
    db = []

calendar = Calendar()

url = 'https://www.pusan.ac.kr/kor/CMS/Haksailjung/view.do?mCode=MN076'

page = request_url(url)
doc = lh.fromstring(page.content)

# Parse data that are stored between <tr>..</tr> of HTML
calendar_rows = doc.xpath('//tr')

# Skip header row
for row in calendar_rows[1:]:
    date_element, subject_element = row.iterchildren()
    raw_date = date_element.text_content()
    subject = subject_element.text_content()
    clean_date = raw_date.replace('.', '-')
    begin_date, end_date = clean_date.split(' - ')

    # Check for duplicate event entry
    db_entry = raw_date + ' ' + subject

    if db_entry not in db:
        db.append(db_entry)
        event = Event()
        event.name = subject
        event.begin = begin_date
        event.end = end_date
        event.make_all_day()
        calendar.events.add(event)

with open('pnu_cal.ics', 'w') as file:
    file.writelines(calendar)

# Write db file to avoid duplication
with open('pnu_cal_db.txt', 'w') as file:
    file.write("\n".join(db))
