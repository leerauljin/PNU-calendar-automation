#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ics import Calendar, Event
import lxml.html as lh
import requests

URL = 'https://www.pusan.ac.kr/kor/CMS/Haksailjung/view.do?mCode=MN076'
MAX_RETRY = 5
FILENAME_DB = 'pnu_cal_db.txt'
FILENAME_RESULT = 'pnu_cal.ics'


def extract_source():
    retry_count = 0
    while retry_count < MAX_RETRY:
        try:
            page = requests.get(URL)
        except requests.ConnectionError:
            print('Connection Error. Retrying...')
            retry_count += 1
        else:
            doc = lh.fromstring(page.content)
            break
    return doc


def read_db():
    try:
        with open(FILENAME_DB, 'r') as file:
            db = [line.rstrip() for line in file]
        print('DB Read Complete.')
    except FileNotFoundError:
        db = []
    return db


def save_db(db):
    # Write db file to avoid duplication
    with open(FILENAME_DB, 'w') as file:
        file.write("\n".join(db))

    print('DB Write Successful!')


def save_cal(calendar):
    with open(FILENAME_RESULT, 'w') as file:
        file.writelines(calendar)

    print('Calendar Write Successful!')


db = read_db()

calendar = Calendar()

doc = extract_source()
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

save_db(db)
save_cal(calendar)
