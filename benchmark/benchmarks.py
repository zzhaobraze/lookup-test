# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import re
import configparser
import urllib.request
import urllib.parse
import pathlib

import logging
import concurrent.futures
import time
import datetime
import csv
import threading
import random
import argparse


def check_endpoint(url_info):
    start_time = datetime.datetime.now().timestamp()
    try:
        req = urllib.request.Request(url_info['url'], None, url_info['header'])
        bl = urllib.request.urlopen(req)
        status = bl.status
        end_time = datetime.datetime.now().timestamp()
        run_duration = end_time - start_time
        return [url_info['key'], status,
            datetime.datetime.fromtimestamp(start_time).strftime("%m/%d/%Y %H:%M:%S"),
            datetime.datetime.fromtimestamp(end_time).strftime("%m/%d/%Y %H:%M:%S"),
            run_duration]
    except Exception as e:
        logging.info("Error with %s: %s", url_info['url'], e)
        end_time = datetime.datetime.now().timestamp()
        run_duration = end_time - start_time
        return [url_info['key'], 'error',
            datetime.datetime.fromtimestamp(start_time).strftime("%m/%d/%Y %H:%M:%S"),
            datetime.datetime.fromtimestamp(end_time).strftime("%m/%d/%Y %H:%M:%S"),
            run_duration]

def verify_url(url):
    if not url.lower().startswith('https://'):
        raise argparse.ArgumentTypeError('Url must start with "https://"')
    return url

if __name__ == "__main__":
    settings = {
        'max_workers': 10,
        'max_threads': 20,
        'max_samples': 100
    }

    aparser = argparse.ArgumentParser(description='Runs simple benchmarks agains the Lookup Endpoint')
    aparser.add_argument('-e','--endpoint', dest='endpoint', type=verify_url, required=True,
        help='Lookup endpoint to test. Example https://www.endpoint.com/lookup')
    aparser.add_argument('-d','--datafile', dest='datafile', type=str, required=True,
        help='Sample Data file(csv) to load')
    aparser.add_argument('-a','--auth', dest='AUTHENTICATION', type=str, required=False,
        help='Authentication string. Default to env variable or ".env" file.')
    aparser.add_argument('-w','--workers', dest='max_workers', type=int, default=settings['max_workers'],
        help='Maximum number of workers default to %i'%(settings['max_workers']))
    aparser.add_argument('-t','--threads', dest='max_threads', type=int, default=settings['max_threads'],
        help='Maximum number of threads, default to %i'%(settings['max_threads']))
    aparser.add_argument('-s','--samples', dest='max_samples', type=int, default=settings['max_samples'],
        help='Maximum number of samples to run, default to %i'%(settings['max_samples']))

    args = aparser.parse_args()

    run_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    result_filename =  './benchmark-results-%s.csv'%( run_timestamp)
    summary_filename =  './benchmark-summary-%s.csv'%(run_timestamp)

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    lookup_list = []

    settings = {}
    reqSettings = [
        "AUTHENTICATION"
    ]

    for arg in vars(args):
        settings[arg] = getattr(args, arg)
    if ("AUTHENTICATION" not in settings) or (settings["AUTHENTICATION"] is None):
        if "AUTHENTICATION" in os.environ:
            for setting in reqSettings:
                if setting in os.environ:
                    settings[setting] = os.environ[setting]
        else:
            config = configparser.RawConfigParser()
            config.read('./.env')
            if config.has_section('lookup'):
                for setting in reqSettings:
                    settings[setting] = config.get('lookup', setting)

    if "AUTHENTICATION" not in settings:
        raise RuntimeError("Missing authentication credentials")



    data_file = settings['datafile']

    logging.info("Loading %s", data_file)
    try:
        with open(data_file, newline='') as csvfile:
            csv_lines = csv.reader(csvfile, dialect='excel')
            header = next(csv_lines, None)
            for row in csv_lines:
                lookup_list.append(row[0])
        logging.info("Done loading %s", data_file)
    except Exception as e:
        logging.info("Error loading %s: %s", data_file, e)
        raise RuntimeError("File not found %s"%(data_file))


    summary = {}
    result_file = open(result_filename, "w")
    result_file.write("key,status,start_time,end_time,duration(s)\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=settings['max_workers']) as executor:
        for batch in range(0, settings['max_samples'], settings['max_threads']):
            logging.info("Running batch %i to %i of %i",batch, batch + settings['max_threads'], settings['max_samples'])
            sample_list = list(map(lambda lk: lk, random.choices(lookup_list, k=settings['max_threads'])))
            sample_data = list(map(
                lambda sk: {
                    "url": "%s?id=%s"%(settings['endpoint'], sk),
                    "key": sk,
                    "header": { 'Authorization' : settings['AUTHENTICATION']}
                    },
                sample_list
            ))
            results = list(executor.map(
                check_endpoint,
                sample_data
            ))
            for result in results:
                if result:
                    result_file.write("%s\n" % ','.join(str(rc) for rc in result))
                    if result[1] not in summary:
                        summary[result[1]] = { 'total': 0.0, 'count': 0}
                    summary[result[1]]['total'] += result[4]
                    summary[result[1]]['count'] += 1

    result_file.close()
    logging.info("Summarizing results %s", summary_filename)
    summary_file = open(summary_filename, "w")
    summary_file.write("status,total duration(s), total counts, average response(ms)\n")
    for result in summary:
        summary_file.write("%s,%.6f,%i,%.6f\n"%(
            result,
            summary[result]['total'],
            summary[result]['count'],
            ((summary[result]['total']*1000)/summary[result]['count'])))
    summary_file.close()
    logging.info("Done summary results %s", summary_filename)
