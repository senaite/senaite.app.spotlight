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

import json
import re

try:
    from html import unescape as html_unescape  # py3
except ImportError:  # pragma: no cover
    from HTMLParser import HTMLParser
    html_unescape = HTMLParser().unescape

from bika.lims import api
from bika.lims.api import APIError
from Missing import Missing
from Products.ZCatalog.Catalog import CatalogError
from Products.ZCTextIndex.ParseTree import ParseError
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
from senaite.app.spotlight import logger
from senaite.app.spotlight.controlpanel import get_config
from senaite.app.spotlight.controlpanel import get_searchable_catalogs
from senaite.app.spotlight.interfaces import ISpotlightSearchAdapter
from senaite.core.api.catalog import to_searchable_text_qs
from zope.interface import implementer

# Matches any HTML tag. Used to strip markup from result descriptions so
# rich-text fields (e.g. a storage facility address) render as plain text
# in the search overlay instead of showing raw `<address>`/`<br/>` markup.
HTML_TAG_RE = re.compile(r"<[^>]+>")

# Matches a `<br>` / `<br/>` break tag, turned into a space so words on
# separate lines do not run together once the tags are removed.
HTML_BREAK_RE = re.compile(r"(?i)<\s*br\s*/?\s*>")

# Order of preferred searchable text indexes to query per catalog.
SEARCHABLE_TEXT_INDEXES = [
    "listing_searchable_text",
    "SearchableText",
    "Title",
]

# Hard cap to protect the server, regardless of the configured value.
MAX_RESULTS = 50

# Maximum number of brains scored per catalog when ranking by relevance. This
# bounds the (cheap, metadata-only) scoring work; matches beyond this cap are
# not considered for ranking.
CANDIDATE_LIMIT = 100

# State tokens that map to the `is_active` boolean index instead of the
# workflow `review_state` index. Used as an escape hatch to reveal (or pin
# to) deactivated objects, e.g. "is:inactive".
ACTIVE_STATES = {
    u"active": True,
    u"inactive": False,
}


@implementer(ISpotlightSearchAdapter)
class SpotlightSearchAdapter(object):
    """Spotlight Search Adapter

    Performs a configuration driven search across the catalogs registered in
    the spotlight control panel. The query may carry a prefix token (e.g.
    "s:water") to scope the search to a single catalog.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._config = None

    @property
    def config(self):
        if self._config is None:
            self._config = get_config()
        return self._config

    def __call__(self):
        params = get_request_params()
        # strip the "is:<state>" token first, so it is not mistaken for a
        # catalog prefix (e.g. "is:" would look like the "is" prefix)
        term, state = split_state(params.get("q", ""))
        term, prefix = split_prefix(term)
        # an explicit state request parameter takes precedence
        state = params.get("state") or state

        limit = min(api.to_int(params.get("limit"), self.max_results),
                    MAX_RESULTS)
        catalogs, scoped = self.resolve_catalogs(
            prefix, params.get("catalog"))

        # nothing to search for, unless browsing a single scoped catalog (an
        # empty term while scoped lists the first results of that catalog)
        if not term and not scoped:
            return {"count": 0, "items": []}

        # collect candidate brains from all catalogs WITHOUT waking objects
        candidates = []
        for catalog in catalogs:
            brains = search_brains(catalog, term, CANDIDATE_LIMIT, state)
            for brain in brains[:CANDIDATE_LIMIT]:
                candidates.append((brain, catalog))

        # rank by relevance for a real term (cheap metadata only); for browse
        # keep the catalog's own title-sorted order
        ranked = rank_candidates(candidates, term) if term else candidates
        items = [
            sanitize_item(get_brain_info(brain, catalog))
            for brain, catalog in ranked[:limit]
        ]

        return {"count": len(items), "items": items}

    @property
    def max_results(self):
        return api.to_int(self.config.get("max_results"), MAX_RESULTS)

    def resolve_catalogs(self, prefix=None, catalog=None):
        """Return (catalogs, scoped) for the query

        `scoped` is True when the search is narrowed to one or more explicit
        catalogs or a matching prefix; this enables the "browse first
        results" mode for an empty term. `catalog` may be a single name or a
        comma separated list (multi-catalog selection).
        """
        catalogs = get_searchable_catalogs()
        names = to_catalog_names(catalog)
        if names:
            return [c for c in catalogs if c.get("name") in names], True
        if prefix:
            scoped = [c for c in catalogs if c.get("prefix") == prefix]
            if scoped:
                return scoped, True
        return catalogs, False


def search_brains(catalog, term, limit, state=None):
    """Search a single catalog record and return the matching brains

    Catalog errors are logged and swallowed so a misconfigured catalog does
    not break the whole search.
    """
    name = catalog.get("name")
    try:
        query = make_query(catalog, term, limit, state)
        if query is None:
            return []
        return api.search(query, catalog=name)
    except (APIError, ParseError, CatalogError, KeyError) as exc:
        logger.warning("Search in catalog '%s' failed: %s", name, exc)
        return []


def get_metadata(brain, attr):
    """Read brain metadata as lowercased unicode without waking the object
    """
    value = getattr(brain, attr, None)
    if not value or isinstance(value, Missing):
        return u""
    return api.safe_unicode(value).lower()


def length_bonus(value):
    """Small bonus (0..10) that favors shorter, closer matches
    """
    return max(0.0, 10.0 - 0.1 * len(value))


def field_score(value, term, tokens):
    """Score a single metadata value against the search term

    Higher is better: exact > prefix > substring (earlier is better) > all
    tokens present > some tokens present.
    """
    if not value or not term:
        return 0.0
    if value == term:
        return 100.0
    if value.startswith(term):
        return 90.0 + length_bonus(value)
    position = value.find(term)
    if position >= 0:
        return 70.0 - min(position, 20) + length_bonus(value)
    if tokens and all(token in value for token in tokens):
        return 50.0 + length_bonus(value)
    hits = sum(1 for token in tokens if token in value)
    if hits:
        return 20.0 * hits / len(tokens)
    return 0.0


def relevance_score(brain, term, tokens):
    """Relevance of a brain to the term using cheap metadata only

    The id is weighted slightly higher than the title, since spotlight is
    mostly used to find objects by their id (e.g. barcodes).
    """
    id_score = field_score(get_metadata(brain, "getId"), term, tokens)
    title_score = field_score(get_metadata(brain, "Title"), term, tokens)
    return max(id_score, 0.97 * title_score)


def rank_by_relevance(items, term, get_brain):
    """Sort items by relevance of their brain to the term (metadata only)

    Ties are broken by sortable_title for a stable, predictable order. No
    objects are woken up. `get_brain` extracts the brain from an item.
    """
    term = api.safe_unicode(term).lower()
    tokens = [token for token in term.split() if token]

    def sort_key(item):
        brain = get_brain(item)
        return (-relevance_score(brain, term, tokens),
                get_metadata(brain, "sortable_title"))

    return sorted(items, key=sort_key)


def rank_candidates(candidates, term):
    """Sort (brain, catalog) tuples by relevance to the term
    """
    return rank_by_relevance(candidates, term, lambda item: item[0])


def rank_brains(brains, term):
    """Sort a flat list of brains by relevance to the term
    """
    return rank_by_relevance(brains, term, lambda brain: brain)


def split_state(query):
    """Split a query into (term, state)

    A state filter is expressed with an "is:<state>" token anywhere in the
    query, e.g. "CA20 is:received" -> the state is "received" and the term is
    "CA20". Queries without the token return an empty state.
    """
    query = (query or "").strip()
    match = re.search(r"(?:^|\s)is:(\S+)", query, re.IGNORECASE)
    if not match:
        return query, None
    state = match.group(1)
    term = re.sub(r"(?:^|\s)is:\S+", " ", query, flags=re.IGNORECASE)
    term = re.sub(r"\s+", " ", term).strip()
    return term, state


def is_active_token(state):
    """Return the `is_active` boolean for an "is:active"/"is:inactive" token

    Returns True for "active", False for "inactive" and None for any other
    (or empty) token, so the caller can tell an active-state token apart from
    a workflow `review_state` token.
    """
    if not state:
        return None
    return ACTIVE_STATES.get(api.safe_unicode(state).lower())


def is_sublist(needle, haystack):
    """Check if `needle` occurs as a contiguous sublist of `haystack`
    """
    size = len(needle)
    if size == 0:
        return False
    return any(haystack[i:i + size] == needle
               for i in range(len(haystack) - size + 1))


def resolve_review_states(indexes, token):
    """Resolve a state token to the matching review_state index values

    Matches the token against the distinct `review_state` values present in
    the catalog on whole underscore-delimited segments (so "received" matches
    "sample_received" and "verified" matches both "verified" and
    "to_be_verified", but "active" does NOT match "inactive"). Spaces in the
    token are treated as underscores, so "to be verified" matches
    "to_be_verified".
    """
    index = indexes.get("review_state")
    if index is None:
        return []
    needle = [s for s in api.safe_unicode(token).lower().replace(
        " ", "_").split("_") if s]
    matched = []
    for value in index.uniqueValues():
        segments = api.safe_unicode(value).lower().split("_")
        if is_sublist(needle, segments):
            matched.append(value)
    return matched


def to_catalog_names(catalog):
    """Parse the request `catalog` parameter into a list of catalog names

    Accepts a comma separated string (as sent by the overlay for a
    multi-catalog selection) or a list; blank entries are dropped.
    """
    if not catalog:
        return []
    if isinstance(catalog, (list, tuple)):
        values = catalog
    else:
        values = api.safe_unicode(catalog).split(",")
    names = [api.safe_unicode(value).strip() for value in values]
    return [name for name in names if name]


def split_prefix(query):
    """Split a query into (term, prefix)

    A prefix is a short token followed by a colon, e.g. "s:water" -> the prefix
    is "s" and the term is "water". Queries without a colon return an empty
    prefix.
    """
    query = (query or "").strip()
    if ":" not in query:
        return query, None
    prefix, _, term = query.partition(":")
    prefix = prefix.strip()
    # only treat short alphanumeric tokens as a prefix
    if prefix.isalnum() and len(prefix) <= 3:
        return term.strip(), prefix
    return query, None


def get_search_index_for(indexes, override=None):
    """Returns the searchable text index to query from the given indexes

    :param indexes: the catalog `_catalog.indexes` mapping
    :param override: optional index name to use if present in the catalog
    """
    # honor an explicit index override from the configuration
    if override and override in indexes:
        return override

    # check if we have a prioritized index
    for idx in SEARCHABLE_TEXT_INDEXES:
        if idx in indexes:
            return idx

    # fall back to the first ZCTextIndex found
    for key, index in indexes.items():
        if isinstance(index, ZCTextIndex):
            return key

    return None


def sanitize_term(term):
    """Neutralize ZCTextIndex query operators in the search term

    ZCTextIndex treats "-" as a negation operator, so a term like "WS-001"
    becomes "WS AND NOT 001" and collapses the search. We replace the hyphen
    with a space so the term is tokenized into separate words instead, e.g.
    "WS-001" -> "WS 001".
    """
    return term.replace("-", " ")


def is_sortable_index(index):
    """Check if the given catalog index can be used as a sort index
    """
    return index is not None and hasattr(index, "documentToKeyMap")


def make_query(catalog, term, limit, state=None):
    """Prepare a catalog query from a catalog config record and search term
    """
    name = catalog.get("name")
    tool = api.get_tool(name, default=None)
    if tool is None:
        logger.warning("Spotlight: unknown catalog '%s'", name)
        return None
    indexes = tool._catalog.indexes

    query = {}
    # text search; an empty term means "browse" (list the first results)
    if term:
        index = get_search_index_for(indexes, catalog.get("index"))
        if not index:
            return None
        query[index] = to_searchable_text_qs(sanitize_term(term))
    elif "path" in indexes:
        # browse: query a real index (everything under the portal) so the
        # catalog reliably returns items, instead of relying on the behavior
        # of a query that has only sort parameters
        query["path"] = api.get_path(api.get_portal())
    else:
        # no way to match all without a real index query
        return None

    # active/inactive and workflow state filtering. "is:active"/"is:inactive"
    # map to the `is_active` boolean index; any other "is:<state>" token maps
    # to the workflow `review_state` index. Without a token, inactive objects
    # are hidden by default. All of it is guarded by the catalog actually
    # having the index, so catalogs lacking `is_active` (e.g. uid_catalog) are
    # searched unchanged.
    active = is_active_token(state)
    if active is not None:
        # explicit escape hatch: reveal (or pin to) (in)active objects
        if "is_active" in indexes:
            query["is_active"] = active
    elif state:
        # explicit workflow state (e.g. "is:received"); do not force the
        # active default, so states like "cancelled" stay findable. If the
        # catalog has no matching state, skip it so results stay accurate.
        review_states = resolve_review_states(indexes, state)
        if not review_states:
            return None
        query["review_state"] = review_states
    elif "is_active" in indexes:
        # no state token: hide inactive objects by default
        query["is_active"] = True

    portal_types = catalog.get("portal_types")
    if portal_types:
        if not isinstance(portal_types, list):
            portal_types = [portal_types]
        query["portal_type"] = portal_types

    # only sort on a configured index that exists in this catalog AND is
    # capable of sorting (has a `documentToKeyMap`, e.g. a FieldIndex),
    # otherwise ZCatalog raises a CatalogError
    sort_on = catalog.get("sort_on")
    if sort_on and is_sortable_index(indexes.get(sort_on)):
        query["sort_on"] = sort_on
        query["sort_order"] = catalog.get("sort_order", "ascending")
    elif sort_on:
        logger.warning("Ignoring invalid sort index '%s' for catalog '%s'",
                       sort_on, name)
    elif not term and is_sortable_index(indexes.get("sortable_title")):
        # browse: default to alphabetical order for stable first results
        query["sort_on"] = "sortable_title"

    query["sort_limit"] = int(limit)
    return query


def strip_html(text):
    """Return `text` with HTML markup removed and whitespace collapsed.

    Rich-text fields (e.g. an `AddressField` rendering as
    `<address>...<br/>...</address>`) would otherwise show their raw tags
    in the search overlay, which escapes HTML. Break tags become spaces so
    words on separate lines stay separated, the remaining tags are dropped
    and character entities are unescaped.
    """
    text = api.safe_unicode(text or u"")
    if not text:
        return u""
    text = HTML_BREAK_RE.sub(u" ", text)
    text = HTML_TAG_RE.sub(u" ", text)
    text = html_unescape(text)
    return re.sub(r"\s+", u" ", text).strip()


def get_brain_info(brain, catalog=None):
    """Extract the relevant info from a catalog brain
    """
    icon = api.get_icon(brain)
    # avoid 404 errors with the default document icon
    if "document_icon.gif" in icon:
        icon = ""

    parent = api.get_parent(brain)

    # secondary identifier to disambiguate same-named results (e.g. clients
    # sharing a name). Read from brain metadata when available (no wakeup).
    secondary_id = getattr(brain, "getClientID", None)
    if isinstance(secondary_id, Missing):
        secondary_id = None

    return {
        "id": api.get_id(brain),
        "uid": api.get_uid(brain),
        "title": api.get_title(brain),
        "title_or_id": api.get_title(brain) or api.get_id(brain),
        "description": strip_html(api.get_description(brain)),
        "url": api.get_url(brain),
        "portal_type": api.get_portal_type(brain),
        "review_state": api.get_review_status(brain),
        "parent_title": api.get_title(parent),
        "parent_url": api.get_url(parent),
        "secondary_id": secondary_id or "",
        "icon": icon,
        "catalog": catalog.get("name") if catalog else "",
        "catalog_label": catalog.get("label", "") if catalog else "",
    }


def sanitize_item(item):
    """Replace Missing.Value with empty strings for JSON serialization
    """
    return {
        key: ("" if isinstance(value, Missing) else value)
        for key, value in item.items()
    }


def get_request_params():
    """Return the request parameters from the form or the request body
    """
    request = api.get_request()
    form = request.form
    if not form:
        try:
            form = json.loads(request.BODY)
        except (ValueError, TypeError):
            form = {}
    return form
