#!/usr/bin/env python3

import collections
import re
from datetime import date, timedelta
from itertools import chain
from typing import Iterator, Optional, Tuple

import bs4
import requests

CHINA_HOLIDAY_WORKDAY_URLS = collections.OrderedDict({
    2019: "http://www.gov.cn/zhengce/content/2018-12/06/content_5346276.htm",
    2020: "http://www.gov.cn/zhengce/content/2019-11/21/content_5454164.htm",
    2021: "http://www.gov.cn/zhengce/content/2020-11/25/content_5564127.htm"
})


def get_paper(url: str) -> str:
    assert re.match(r'http://www.gov.cn/zhengce/content/\d{4}-\d{2}/\d{2}/content_\d+.htm',
                    url), 'Site changed, need human verify'

    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = bs4.BeautifulSoup(response.text, features='html.parser')

    container = soup.find('td', class_='b12c')
    assert container, f'Can not get paper container from url: {url}'

    ret = container.get_text().replace('\u3000\u3000', '\n')
    assert ret, f'Can not get paper context from url: {url}'

    return ret


def get_rules(paper: str) -> Iterator[Tuple[str, str]]:
    lines: list = paper.splitlines()
    lines = sorted(set(lines), key=lines.index)
    count = 0

    for i in chain(get_normal_rules(lines), get_patch_rules(lines)):
        count += 1
        yield i

    if not count:
        raise NotImplementedError(lines)


def get_normal_rules(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    for i in lines:
        match = re.match(r'[一二三四五六七八九十]、(.+?)：(.+)', i)
        if match:
            yield match.groups()


def get_patch_rules(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    name = None

    for i in lines:
        match = re.match(r'.*\d+年(.{2,})(?:假期|放假)安排.*', i)
        if match:
            name = match.group(1)
        if not name:
            continue

        match = re.match(r'^[一二三四五六七八九十]、(.+)$', i)
        if not match:
            continue

        description = match.group(1)
        if re.match(r'.*\d+月\d+日.*', description):
            yield name, description


def _cast_int(value):
    return int(value) if value else None


class DescriptionParser:
    def __init__(self, description: str, year: int):
        self.description = description
        self.year = year
        self.date_history = list()

    def parse(self) -> Iterator[dict]:
        del self.date_history[:]

        for i in re.split('[，。；]', self.description):
            for j in SentenceParser(self, i).parse():
                yield j

        if not self.date_history:
            raise NotImplementedError(self.description)

    def get_date(self, year: Optional[int], month: Optional[int], day: int) -> date:
        assert day, 'No day specified'

        if month is None:
            month = self.date_history[-1].month

        if (year is None
                and month == 12
                and self.date_history
                and max(self.date_history) < date(year=self.year, month=2, day=1)):
            year = self.year - 1

        year = year or self.year
        return date(year=year, month=month, day=day)


class SentenceParser:
    def __init__(self, parent: DescriptionParser, sentence):
        self.parent = parent
        self.sentence = sentence

    def extract_dates(self, text: str) -> Iterator[date]:
        count = 0
        text = text.replace('(', '（').replace(')', '）')

        for i in chain(*(method(self, text) for method in self.date_extraction_methods)):
            count += 1
            is_seen = i in self.parent.date_history
            self.parent.date_history.append(i)
            if is_seen:
                continue
            yield i

        if not count:
            raise NotImplementedError(text)

    def _extract_dates_1(self, value: str) -> Iterator[date]:
        match = re.findall(r'(?:(\d+)年)?(?:(\d+)月)?(\d+)日', value)

        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert len(groups) == 3, groups
            yield self.parent.get_date(year=groups[0], month=groups[1], day=groups[2])

    def _extract_dates_2(self, value: str) -> Iterator[date]:
        match = re.findall(
            r'(?:(\d+)年)?(?:(\d+)月)?(\d+)日[至\-—](?:(\d+)年)?(?:(\d+)月)?(\d+)日', value)

        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert len(groups) == 6, groups
            start = self.parent.get_date(year=groups[0],
                                         month=groups[1], day=groups[2])
            end = self.parent.get_date(year=groups[3],
                                       month=groups[4], day=groups[5])
            for i in range((end - start).days + 1):
                yield start + timedelta(days=i)

    def _extract_dates_3(self, value: str) -> Iterator[date]:
        match = re.findall(
            r'(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:（[^）]+）)?'
            r'(?:、(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:（[^）]+）)?)+',
            value)

        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert not (len(groups) % 3), groups
            for i in range(0, len(groups), 3):
                yield self.parent.get_date(year=groups[i], month=groups[i+1], day=groups[i+2])

    date_extraction_methods = [
        _extract_dates_1,
        _extract_dates_2,
        _extract_dates_3
    ]

    def parse(self) -> Iterator[dict]:
        for method in self.parsing_methods:
            for i in method(self):
                yield i

    def _parse_rest_1(self):
        match = re.match(r'(.+)(放假|补休|调休|公休)+(?:\d+天)?$', self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {
                    'date': i,
                    'isOffDay': True
                }

    def _parse_work_1(self):
        match = re.match('(.+)上班$', self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {
                    'date': i,
                    'isOffDay': False
                }

    def _parse_shift_1(self):
        match = re.match('(.+)调至(.+)', self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {
                    'date': i,
                    'isOffDay': False
                }
            for i in self.extract_dates(match.group(2)):
                yield {
                    'date': i,
                    'isOffDay': True
                }

    parsing_methods = [
        _parse_rest_1,
        _parse_work_1,
        _parse_shift_1,
    ]


def parse_paper(year: int, url: str) -> Iterator[dict]:
    paper = get_paper(url)
    rules = get_rules(paper)

    ret = ({'name': name, **i}
           for name, description in rules
           for i in DescriptionParser(description, year).parse())

    try:
        for i in ret:
            yield i
    except NotImplementedError as ex:
        raise RuntimeError('Can not parse paper', url) from ex


def fetch_holidays_workdays() -> (collections.OrderedDict, collections.OrderedDict):
    holidays, workdays = collections.OrderedDict(), collections.OrderedDict()

    for year, url in CHINA_HOLIDAY_WORKDAY_URLS.items():
        for day in parse_paper(year, url):
            actual_year = str(day['date'])[:4]

            if day['isOffDay']:
                if actual_year not in holidays:
                    holidays[actual_year] = set()
                holidays[actual_year].add('"{}"'.format(str(day['date'])))
            else:
                if actual_year not in workdays:
                    workdays[actual_year] = set()
                workdays[actual_year].add('"{}"'.format(str(day['date'])))

    for year, days in holidays.items():
        holidays[year] = sorted(list(days))

    for year, days in workdays.items():
        workdays[year] = sorted(list(days))

    return holidays, workdays


def dump2golang(holidays, workdays: collections.OrderedDict):
    content = """package util

var holidays = []string{
%s}

var workdays = []string{
%s}

func IsHoliday(t time.Time) bool {
    weekday := t.Weekday()
    date := t.Format(DateFormat)

    isSpecialHoliday, isNormalWeekEnd := false, false
    if funk.Contains(holidays, date) {
    isSpecialHoliday = true
    }

    if (weekday == time.Saturday || weekday == time.Sunday) && !funk.Contains(workdays, date) {
        isNormalWeekEnd = true
    }

    return isSpecialHoliday || isNormalWeekEnd
}

func IsWorkday(t time.Time) bool {
    return !IsHoliday(t)
}
"""
    holidays_str, workdays_str = '', ''

    with open("holiday_workday.go", 'w') as wf:
        for days in holidays.values():
            holidays_str += '    {},\n'.format(', '.join(days))
        for days in workdays.values():
            workdays_str += '    {},\n'.format(', '.join(days))

        wf.write(content % (holidays_str, workdays_str))


def main():
    dump2golang(*fetch_holidays_workdays())


if __name__ == '__main__':
    main()
