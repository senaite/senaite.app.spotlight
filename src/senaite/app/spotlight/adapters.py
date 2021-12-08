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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from bika.lims import api
from plone.memoize import forever
from senaite.app.spotlight.interfaces import ISpotlightSearchAdapter
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from zope.interface import implementer

CATALOGS = [
    "portal_catalog",
    SAMPLE_CATALOG,
    SETUP_CATALOG,
    WORKSHEET_CATALOG,
]

MAX_RESULTS = 12


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
    if query is None:
        return []
    results = api.search(query, catalog=catalog)
    return results


@forever.memoize
def get_search_index_for(catalog):
    """Returns the search index to query
    """
    searchable_text_index = "SearchableText"
    listing_searchable_text_index = "listing_searchable_text"

    if catalog == SAMPLE_CATALOG:
        tool = api.get_tool(catalog)
        indexes = tool.indexes()
        if listing_searchable_text_index in indexes:
            return listing_searchable_text_index

    return searchable_text_index


def make_query(catalog):
    """A function to prepare a query
    """
    query = {}
    index = get_search_index_for(catalog)
    params = get_request_params()

    limit = params.get("limit", 5)

    q = params.get("q")
    if len(q) > 0:
        query[index] = q + "*"
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
