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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from senaite.app.spotlight.adapters import rank_brains
from senaite.app.spotlight.adapters import search_brains
from senaite.app.spotlight.adapters import split_state
from senaite.app.spotlight.controlpanel import get_searchable_catalogs
from senaite.core.browser.listing.base import ListingView

# Maximum number of merged results fetched per catalog
MAX_PER_CATALOG = 50

# Hard cap of the merged result set across all catalogs
LISTING_MAX_RESULTS = 500

# Safety bound for the parent-walk when building the location breadcrumbs
MAX_BREADCRUMB_DEPTH = 20


class SearchView(ListingView):
    """A standalone, full page search across the spotlight catalogs

    Reuses the catalogs configured in the spotlight control panel and merges
    the results into a single, cross-catalog listing. The catalog switcher tabs
    allow to narrow the search down to "All" or a single catalog.
    """

    def __init__(self, context, request):
        super(SearchView, self).__init__(context, request)

        # no "Add" action, this is a read-only search page and not the
        # context's folder contents
        self.context_actions = {}

        self.catalogs = get_searchable_catalogs()
        # search uses its own merged backend, so no catalog content filter
        self.catalog = "uid_catalog"
        self.contentFilter = {}

        self.form_id = "search"
        self.title = _("Search")
        self.show_select_column = False
        self.show_search = True
        self.show_workflow_action_buttons = False
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(u"Title")}),
            ("getId", {
                "title": _(u"ID")}),
            ("portal_type", {
                "title": _(u"Type")}),
            ("location", {
                "title": _(u"Location")}),
        ))

        self.review_states = self.get_catalog_review_states()
        self.default_review_state = "all"

    def get_catalog_review_states(self):
        """Expose "All" plus the configured catalogs as switcher tabs
        """
        columns = list(self.columns.keys())
        states = [{
            "id": "all",
            "title": _(u"All"),
            "contentFilter": {},
            "columns": columns,
        }]
        for catalog in self.catalogs:
            states.append({
                "id": catalog["name"],
                "title": catalog.get("label") or catalog["name"],
                "contentFilter": {},
                "columns": columns,
            })
        return states

    def get_selected_scope(self):
        """Return the selected catalog scope, or None for "All"
        """
        key = "{}_review_state".format(self.form_id)
        selected = self.request.form.get(key, "all")
        names = [c["name"] for c in self.catalogs]
        return selected if selected in names else None

    def get_scoped_catalogs(self):
        """Return the catalog config records in scope of the current selection
        """
        scope = self.get_selected_scope()
        if scope is None:
            return self.catalogs
        return [c for c in self.catalogs if c["name"] == scope]

    def search(self, searchterm="", ignorecase=True):
        """Merge the brains of all catalogs in scope into a single result set

        The search term sanitizing (e.g. the "-" operator) is handled by the
        spotlight search backend.
        """
        if not searchterm:
            return []
        # support the "is:<state>" token in the listing search box as well
        term, state = split_state(searchterm)
        if not term:
            return []
        brains = []
        for catalog in self.get_scoped_catalogs():
            brains.extend(
                search_brains(catalog, term, MAX_PER_CATALOG, state))
        # rank the mixed brain set by relevance to the term (metadata only)
        return rank_brains(brains, term)[:LISTING_MAX_RESULTS]

    def folderitem(self, obj, item, index):
        """Render a single, catalog agnostic result row
        """
        item["replace"]["Title"] = get_link_for(obj)
        item["getId"] = api.get_id(obj)
        item["portal_type"] = api.get_portal_type(obj)
        item["replace"]["location"] = self.get_location_breadcrumbs(obj)
        return item

    def get_location_breadcrumbs(self, obj):
        """Render the parent containers as a breadcrumb of links

        Walks up from the immediate parent to the portal, e.g.
        "SENAITE > Worksheets", similar to the breadcrumbs navigation.
        """
        ancestors = []
        parent = api.get_parent(obj)
        # walk up to and including the portal, with a hard depth cap as a
        # safety bound against unexpectedly deep or cyclic parent chains
        for _depth in range(MAX_BREADCRUMB_DEPTH):
            if parent is None:
                break
            ancestors.append(parent)
            if api.is_portal(parent):
                break
            parent = api.get_parent(parent)
        ancestors.reverse()
        links = [
            get_link(api.get_url(p), api.get_title(p), csrf=False)
            for p in ancestors
        ]
        return u" › ".join(links)
