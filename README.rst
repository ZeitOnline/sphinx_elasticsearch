====================
sphinx_elasticsearch
====================

Indexes a documentation project build via `Sphinx`_ into elasticsearch.
This is a stand-alone extraction of the functionality used by readthedocs.org,
compatible with elasticsearch-6.

.. _`sphinx`: https://www.sphinx-doc.org/


Usage
=====

Set up:

* Install `elasticsearch`_
* Install the package: ``virtualenv --python=python3 .; bin/pip install sphinx_elasticsearch``
* Create index:
  ``bin/sphinx-elasticsearch create-index --es-url=http://localhost:9200 --replicas=1 --shards=5``
  ``bin/sphinx-elasticsearch put-mapping --es-url=http://localhost:9200``

By default we use an index named ``docs`` and a document type ``page``, you can customize this via the ``--index`` and ``--type`` parameters (but you'll need to pass them to all three commands, create-index, put-mapping and index).

Note that you'll probably be better off managing index creation and mapping setup yourself; these two setup commands are more for getting started quickly and out of the box.

Index your sphinx project:

* Build your project as JSON (for easier parsing): ``bin/sphinx-build -b json . json-build``
* Index into ES: ``bin/sphinx-elasticsearch index --es-url=http://localhost:9200 --index=docs json-build``
  (If you pass ``--commit`` any previously indexed pages that have been deleted will be removed automatically.)


.. _`elasticsearch`: https://www.elastic.co/products/elasticsearch


Elasticsearch Mapping
=====================

:project: Short name of the project. Clients will use this to construct URLs.
:path: Relative path of the page, without extension.
:id: Unique identifier (hash of ``project`` and ``path``)
:commit: Optional, to allow deleting deleted pages on subsequent index runs.
:title: Title of the page
:headers: List of all headers on the page
:content: Body of the page (any HTML markup is stripped by ES)
