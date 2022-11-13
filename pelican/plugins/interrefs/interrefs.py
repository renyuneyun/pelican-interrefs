#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Inter-references plugin for Pelican
===================================
Adds interrefs variable (which contains fields forward and backward) to article's context

TODO
---------------
- i18n_subsite is not correct handled. Though the generated result is of no problem
  Maybe worth figuring out why, and fix it. I believe currently linking across
  i18n_subsites won't be identified correctly.
- Complexity is high (O(n^3)). See the comment of relevant section
- Maybe using other signals is a neater solution
'''

import logging
import re

from collections import defaultdict
from itertools import chain
from dataclasses import dataclass

from bs4 import BeautifulSoup
from pelican import signals
from pelican.generators import ArticlesGenerator


log = logging.getLogger(__name__)


absolute_url_pattern = re.compile(r'https?://')
anchor_url_pattern = re.compile(r'^#')


@dataclass
class InterRef:
    forward = []
    backward = []

    def __bool__(self):
        return bool(self.forward or self.backward)


def add_inter_refs_article(generator):
    settings = generator.settings
    siteurl = settings.get('SITEURL', '')

    def is_site_url(url):
        if absolute_url_pattern.match(url):
            if siteurl:
                return url.startswith(siteurl)
            else:
                return False
        else:
            if anchor_url_pattern.match(url):
                return False
            return True

    num_forward_refs = settings.get("FORWARD_REFS", None)
    num_backward_refs = settings.get("BACKWARD_REFS", None)

    forward_url_map = defaultdict(set)
    article_urls = {}

    for article in chain(generator.articles, generator.drafts):
        article_url = article.url
        article_urls[article_url] = article

        # Note: previously used article._content rather than article.content, because the other option will raise problems (e.g. images won't load) when using signal article_generators_finalized. But now uses different signal, which no longer has this issue.
        soup_doc = BeautifulSoup(article.content, 'html.parser')
        for anchor in soup_doc(['a', 'object']):
            if 'href' not in anchor.attrs:
                continue
            url = anchor['href']

            if is_site_url(url):
                forward_url_map[article_url].add(url)

    forward_internal_map = defaultdict(set)
    backward_internal_map = defaultdict(set)

    # Not very efficient. Worst case O(n^3), where n is the number of articles.
    # Needs optimization afterwards
    for article_url_from, links in forward_url_map.items():
        for link in links:
            for article_url_to, article_to in article_urls.items():
                if link.endswith(article_url_to) or link.endswith(article_to.slug):
                    forward_internal_map[article_url_from].add(article_url_to)
                    backward_internal_map[article_url_to].add(article_url_from)

    for article in chain(generator.articles, generator.drafts):
        article_url = article.url
        interrefs = InterRef()
        if article_url in forward_internal_map:
            forward_refs = [article_urls[a_url] for a_url in forward_internal_map[article_url]]
            if num_forward_refs is not None:
                forward_refs = [ref for i, ref in enumerate(forward_refs)
                                if i < num_forward_refs]
            interrefs.forward = forward_refs
        if article_url in backward_internal_map:
            backward_refs = [article_urls[a_url] for a_url in backward_internal_map[article_url]]
            if num_backward_refs is not None:
                backward_refs = [ref for i, ref in enumerate(backward_refs)
                                 if i < num_backward_refs]
            interrefs.backward = backward_refs
        article.interrefs = interrefs


def add_inter_refs_generators(generators):
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            add_inter_refs_article(generator)


def register():
    signals.all_generators_finalized.connect(add_inter_refs_generators)
