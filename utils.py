# -*- coding: utf-8 -*-
import cookielib
import copy
import csv
import StringIO
import urllib2

from flask import make_response
from pylinkvalidator import api


def generate_csv(items):
    header = ['status', 'source', 'url']
    strIO = StringIO.StringIO()
    writer = csv.DictWriter(
        strIO,
        delimiter=',',
        lineterminator='\n',
        fieldnames=header,
    )
    writer.writeheader()
    for item in items:
        for s_item in item['sources_data']:
            data = {
                'status': item['item_status'],
                'source': s_item['source_url'],
                'url': item['item_url'],
            }
            writer.writerow(data)
    return strIO.getvalue()


def csv_response(data):
    output = make_response(data)
    output.headers['Content-Disposition'] = 'attachment; filename=export.csv'
    output.headers["Content-type"] = "text/csv"
    return output


def return_error_pages(site_links=[], config={}):
    error_items = []
    crawled_site = api.crawl_with_options(
        site_links,
        config,
    )
    error_pages = crawled_site.error_pages
    for item in error_pages:
        raw = error_pages[item]
        sources = raw.sources
        sources_data = []
        for source in sources:
            source_url = source.origin.geturl()
            source_html = source.origin_str
            source_data = {
                'source_url': source_url,
                'source_html': source_html,
            }
            sources_data.append(source_data)
        item_url = raw.url_split.geturl()
        item_status = raw.status
        item_status_message = raw.get_status_message()
        data = {
            'sources': len(sources),
            'sources_data': sources_data,
            'item_url': item_url,
            'item_status': item_status,
            'item_status_message': item_status_message,
        }
        error_items.append(data)
    return error_items


def check_redirects(results):
    broken_links = copy.deepcopy(results)
    # CookieJar
    cj = cookielib.CookieJar()
    # Opener
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    # Iterate
    for item in results:
        # Defaults
        item_url = item['item_url']
        # Request
        req = urllib2.Request(
            item_url,
            None,
            {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; '
                           'G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/44.0.2403.157 Safari/537.36',
             'Accept': 'text/html,application/xhtml+xml,application/'
                       'xml;q=0.9,image/webp,*/*;q=0.8',
             'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
             'Accept-Encoding': 'gzip, deflate, sdch',
             'Accept-Language': 'en-US,en;q=0.8',
             'Connection': 'keep-alive'},
        )
        try:
            resp = opener.open(req)
            resp_code = resp.getcode()
            if resp_code == 200:
                broken_links.remove(item)
        except Exception:
            pass
    return broken_links
