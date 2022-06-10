# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.APP.SPOTLIGHT.
#
# SENAITE.APP.SPOTLIGHT is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from bika.lims import api
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
from senaite.app.spotlight import logger
from senaite.app.spotlight.interfaces import ISpotlightSearchAdapter
from senaite.core.api.catalog import to_searchable_text_qs
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from zope.interface import implementer

CATALOGS = [
    SAMPLE_CATALOG,
    SETUP_CATALOG,
    WORKSHEET_CATALOG,
    SENAITE_CATALOG,
    "portal_catalog",
]

SEARCHABLE_TEXT_INDEXES = [
    "listing_searchable_text",
    "SearchableText",
    "Title",
]

MAX_RESULTS = 15


@implementer(ISpotlightSearchAdapter)
class SpotlightSearchAdapter(object):
    """Spotlight Search Adapter
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        search_results = []
        for catalog in CATALOGS:
            search_results.extend(search(catalog=catalog))
            # break early when the max search results were found
            if len(search_results) >= MAX_RESULTS:
                break

        # extract the data from all the brains
        items = map(get_brain_info, search_results[:MAX_RESULTS])

        return {
            "count": len(items),
            "items": items,
        }


def get_brain_info(brain):
    """Extract the brain info
    """
    icon = api.get_icon(brain)
    # avoid 404 errors with these guys
    if "document_icon.gif" in icon:
        icon = ""

    id = api.get_id(brain)
    url = api.get_url(brain)
    title = api.get_title(brain)
    description = api.get_description(brain)
    parent = api.get_parent(brain)
    parent_title = api.get_title(parent)
    parent_url = api.get_url(parent)

    return {
        "id": id,
        "title": title,
        "title_or_id": title or id,
        "description": description,
        "url": url,
        "parent_title": parent_title,
        "parent_url": parent_url,
        "icon": icon,
    }


def search(query=None, catalog=None):
    """Search
    """
    if query is None:
        query = make_query(catalog)
    # no query generated
    if query is None:
        return []
    logger.info("Spotlight query=%r for catalog=%r" % (query, catalog))
    results = api.search(query, catalog=catalog)
    return results


def get_search_index_for(catalog):
    """Returns the search index to query
    """
    search_index = None
    tool = api.get_tool(catalog)
    indexes = tool._catalog.indexes
    searchable_text_indexes = []

    # gather all ZCTextIndexes from this catalog
    for k, v in indexes.items():
        if type(v) == ZCTextIndex:
            searchable_text_indexes.append(k)

    # check if we have a prioritized catalog
    for idx in SEARCHABLE_TEXT_INDEXES:
        if idx in indexes:
            search_index = idx
            break

    if search_index is not None:
        return search_index
    elif len(searchable_text_indexes) > 0:
        return searchable_text_indexes[0]

    return None


def make_query(catalog):
    """A function to prepare a query
    """
    query = {}
    index = get_search_index_for(catalog)
    params = get_request_params()

    limit = params.get("limit", MAX_RESULTS)

    q = params.get("q")
    if index and len(q) > 0:
        query[index] = to_searchable_text_qs(q)
    else:
        return None

    portal_type = params.get("portal_type")
    if portal_type:
        if not isinstance(portal_type, list):
            portal_type = [portal_type]
        query["portal_type"] = portal_type
        query["sort_limit"] = int(limit)

    return query


def get_request_params():
    request = api.get_request()
    form = request.form
    if not form:
        form = json.loads(request.BODY)
    return form
