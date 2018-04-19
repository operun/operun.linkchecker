# -*- coding: utf-8 -*-
import BeautifulSoup
import requests
from flask import Flask, render_template, request
from utils import (
    check_redirects,
    csv_response,
    generate_csv,
    return_error_pages,
)

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
                'test-outside': True,
            },
        )
        if result:
            result = check_redirects(result)
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
        'source_url': '',
    }
    if len(form):
        item_url = form.get('item_url', '')
        item_source_url = form.get('item_source_url', '')
        r = requests.get(item_source_url)
        soup = BeautifulSoup.BeautifulSoup(r.content)
        data['broken_link'] = item_url.replace(item_source_url, '')
        data['page_html'] = soup.prettify().decode('utf-8')
        data['source_url'] = item_source_url
    return render_template(template, **data)
