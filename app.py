# -*- coding: utf-8 -*-

import csv
import StringIO

import BeautifulSoup
import requests
from flask import Flask, make_response, render_template, request
from pylinkvalidator import api

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    template = 'index.html'
    form = request.form
    data = {}
    if len(form):
        submit = form.get('form.button.submit', '')
        website_url = form.get('website_url', '')
        if not website_url:
            return render_template(template)
        timeout = int(form.get('timeout', '5'))
        depth = int(form.get('depth', '0'))
        csv_data = form.get('csv_data', '')
        if submit == 'csv':
            if csv_data:
                return csv_response(csv_data)
            return render_template(template)
        result = return_error_pages(
            site_links=[website_url],
            config={
                'depth': depth,
                'timeout': timeout,
                'workers': 12,
                'mode': 'process',
                'progress': True,
            },
        )
        csv_data = generate_csv(result)
        data['errors'] = result
        data['website_url'] = website_url
        data['timeout'] = timeout
        data['depth'] = depth
        data['csv_data'] = csv_data
    return render_template(template, **data)


@app.route('/inspector', methods=['GET', 'POST'])
def inspector():
    template = 'inspector.html'
    form = request.form
    data = {
        'broken_link': '',
        'page_html': '',
    }
    if len(form):
        item_url = form.get('item_url', '')
        item_source_url = form.get('item_source_url', '')
        data['broken_link'] = item_url.replace(item_source_url, '')
        r = requests.get(item_source_url)
        soup = BeautifulSoup.BeautifulSoup(r.content)
        data['page_html'] = soup.prettify().decode('utf-8')
    return render_template(template, **data)


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
