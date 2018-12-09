# coding: utf-8
# Taken from <https://github.com/rtfd/readthedocs.org/tree/2.8.3
#   readthedocs/search/parse_json.py>
#
# Copyright (c) 2010-2017 Read the Docs, Inc & contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
from pyquery import PyQuery
import logging
import codecs
import fnmatch
import json
import os


log = logging.getLogger(__name__)


def process_all_json_files(build_dir):
    """Return a list of pages to index"""
    html_files = []
    for root, _, files in os.walk(build_dir):
        for filename in fnmatch.filter(files, '*.fjson'):
            if filename in ['search.fjson', 'genindex.fjson',
                            'py-modindex.fjson']:
                continue
            html_files.append(os.path.join(root, filename))
    page_list = []
    for filename in html_files:
        try:
            result = process_file(filename)
            if result:
                page_list.append(result)
        # we're unsure which exceptions can be raised
        except:  # noqa
            pass
    return page_list


def process_file(filename):
    """Read a file from disk and parse it into a structured dict."""
    try:
        with codecs.open(filename, encoding='utf-8', mode='r') as f:
            file_contents = f.read()
    except IOError:
        log.info('Unable to read file: %s', filename)
        return None
    data = json.loads(file_contents)
    title = ''
    body_content = ''
    if 'current_page_name' in data:
        path = data['current_page_name']
    else:
        log.info('Unable to index file due to no name %s', filename)
        return None
    if 'body' in data and data['body']:
        body = PyQuery(data['body'])
        body_content = body.text().replace(u'¶', '')
    else:
        log.info('Unable to index content for: %s', filename)
    if 'title' in data:
        title = data['title']
        if title.startswith('<'):
            title = PyQuery(data['title']).text()
    else:
        log.info('Unable to index title for: %s', filename)

    return {'headers': process_headers(data, filename),
            'content': body_content, 'path': path, 'title': title}


def process_headers(data, filename):
    """Read headers from toc data."""
    headers = []
    if 'toc' in data:
        for element in PyQuery(data['toc'])('a'):
            headers.append(recurse_while_none(element))
        if None in headers:
            log.info('Unable to index file headers for: %s', filename)
    return headers


def recurse_while_none(element):
    if element.text is None:
        return recurse_while_none(element.getchildren()[0])
    return element.text
