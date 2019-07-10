#!/usr/bin/env python

from cesmd import get_records


def test_get_records_eventid():
    outdir = get_records('nc73201181', 'mhearne@usgs.gov',
                         eventid='nc73201181', unpack=True,
                         station_type='G')


if __name__ == '__main__':
    test_get_records_eventid()
