#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Inter-references plugin for Pelican
===================================
Adds interrefs variable (which contains fields forward and backward) to article's context
'''

import logging
import re

from collections import defaultdict
from itertools import chain
from dataclasses import dataclass

from bs4 import BeautifulSoup
from pelican import signals


log = logging.getLogger(__name__)


absolute_url_pattern = re.compile(r'https?://')


@dataclass
class InterRef:
    forward = []
    backward = []

    def __bool__(self):
        return bool(self.forward or self.backward)


def add_inter_refs(generator):
    settings = generator.settings
    siteurl = settings.get('SITEURL', '')

    def is_site_url(url):
        if siteurl:
            return url.startswith(siteurl)
        else:
            if absolute_url_pattern.match(url):
                return False
            else:
                return True

    num_forward_refs = settings.get("FORWARD_REFS", None)
    num_backward_refs = settings.get("BACKWARD_REFS", None)

    forward_url_map = defaultdict(set)
    article_urls = {}

    for article in chain(generator.articles, generator.drafts):
        article_url = article.url
        article_urls[article_url] = article

        soup_doc = BeautifulSoup(article._content, 'html.parser')  # Use article._content rather than article.content, because the other option will raise problems
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



def register():
    signals.article_generator_finalized.connect(add_inter_refs)
