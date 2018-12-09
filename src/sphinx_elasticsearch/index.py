# Inspired by <https://github.com/rtfd/readthedocs.org/tree/2.8.3/
#   readthedocs/search/indexes.py>
import click
import elasticsearch
import elasticsearch.helpers
import hashlib
import json
import os.path
import sphinx_elasticsearch.parse_json
import sys


@click.group()
def cli():
    pass


@cli.command()
@click.option('--es-url', default='http://localhost:9200')
@click.option('--index', default='docs')
@click.option('--type', default='page')
@click.option('--project-name', required=True)
@click.option('--commit')
@click.argument('build-dir')
def index(es_url, index, type, project_name, commit, build_dir):
    if not os.path.exists(build_dir):
        raise IOError('Directory does not exist: %s' % build_dir)

    es = elasticsearch.Elasticsearch([es_url])

    pages = sphinx_elasticsearch.parse_json.process_all_json_files(build_dir)
    to_index = []
    for page in pages:
        page_id = hashlib.md5((
            project_name + '-' + page['path']).encode('utf-8')).hexdigest()
        doc = {
            'id': page_id,
            'project': project_name,
            'path': page['path'],
            'title': page['title'],
            'headers': page['headers'],
            'content': page['content'],
            'commit': commit,
        }
        to_index.append({
            '_index': index,
            '_type': type,
            '_id': page_id,
            '_source': doc,
        })
    elasticsearch.helpers.bulk(es, to_index)

    if commit:
        es.delete_by_query(body={'query': {'bool': {
            'must': [{'term': {'project': project_name}}],
            'must_not': [{'term': {'commit': commit}}],
        }}}, index=index, doc_type=type)


@cli.command()
@click.option('--es-url', default='http://localhost:9200')
@click.option('--project-name', default=None)
@click.option('--index', default='docs')
@click.argument('query')
def search(es_url, index, query, project_name):
    # This is an example for reference, for a complete implementation see
    # <https://github.com/ZeitOnline/sphinx_zon_theme>
    es = elasticsearch.Elasticsearch([es_url])
    body = {'query': {'bool': {'should': [
        {'match_phrase': {'title': {'query': query, 'boost': 10, 'slop': 2}}},
        {'match_phrase': {'headers': {'query': query, 'boost': 5, 'slop': 3}}},
        {'match_phrase': {'content': {'query': query, 'slop': 5}}},
    ]}},
        'highlight': {'fields': {
            'title': {},
            'headers': {},
            'content': {},
        }},
        '_source': ['title', 'project', 'path'],
        'size': 25,
    }

    if project_name:
        body['query']['bool']['filter'] = [
            {'term': {'project': project_name}}]

    json.dump(es.search(index=index, body=body), sys.stdout, indent=2)


@cli.command()
@click.option('--es-url', default='http://localhost:9200')
@click.option('--index', default='docs')
@click.option('--replicas', required=True)
@click.option('--shards', required=True)
def create_index(es_url, index, replicas, shards):
    # This is mostly for convenience so you can get started out-of-the-box;
    # if you have specific elasticsearch requirements, you'll be better off
    # creating the index yourself externally.
    es = elasticsearch.Elasticsearch([es_url])
    es.indices.create(index=index, body={'settings': {
        'number_of_replicas': replicas,
        'number_of_shards': shards,
    }})


@cli.command()
@click.option('--es-url', default='http://localhost:9200')
@click.option('--index', default='docs')
@click.option('--type', default='page')
def put_mapping(es_url, index, type):
    # This is the simplest possible mapping for the fields we need; you'll
    # probably want to at least add stemmers for your documentation language.
    # And like for `create_index`, you'll probably be better off
    # managing the mapping yourself externally.
    es = elasticsearch.Elasticsearch([es_url])
    es.indices.put_mapping(type, {type: {
        # Disable _all field to reduce index size.
        '_all': {'enabled': False},
        'properties': {
            'id': {'type': 'keyword'},
            'project': {'type': 'keyword'},
            'path': {'type': 'keyword'},
            'commit': {'type': 'keyword'},

            'title': {'type': 'text'},
            'headers': {'type': 'text'},
            'content': {'type': 'text'},
        }
    }}, index)
