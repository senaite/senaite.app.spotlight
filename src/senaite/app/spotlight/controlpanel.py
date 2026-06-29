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

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.supermodel import model
from plone.z3cform import layout
from senaite.core.permissions import AddAnalysisRequest
from senaite.core.permissions import ManageBika
from senaite.core.schema.registry import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from zope import schema
from zope.interface import Interface

# Registry prefix under which the settings are stored.
PREFIX = "senaite.app.spotlight"

# Default hotkey to toggle the spotlight overlay. The value follows the
# `KeyboardEvent` semantics used on the client: modifier names joined with "+"
# and the final key, e.g. "Control+Space", "Meta+k" or "Control+Shift+f".
DEFAULT_HOTKEY = u"Control+Space"

# Default maximum number of search results returned by the search adapter.
DEFAULT_MAX_RESULTS = 25

# Default catalogs to search. Each entry maps to the `ISpotlightCatalog` row
# schema. A `prefix` allows scoping a search to a single catalog, e.g. typing
# "s:water" only searches the catalog whose prefix is "s".
DEFAULT_CATALOGS = [
    {"catalog": "senaite_catalog_sample", "label": u"Samples",
     "prefix": u"s", "enabled": True},
    {"catalog": "senaite_catalog_setup", "label": u"Setup",
     "enabled": True},
    {"catalog": "senaite_catalog_worksheet", "label": u"Worksheets",
     "prefix": u"w", "enabled": True},
    {"catalog": "senaite_catalog", "label": u"SENAITE",
     "enabled": True},
    {"catalog": "senaite_catalog_client", "label": u"Clients",
     "prefix": u"c", "enabled": True},
    {"catalog": "senaite_catalog_contact", "label": u"Contacts",
     "enabled": True},
    {"catalog": "senaite_catalog_report", "label": u"Reports",
     "prefix": u"r", "enabled": False},
    {"catalog": "senaite_catalog_label", "label": u"Labels",
     "enabled": False},
]

# Default command palette actions. Each entry maps to the `ISpotlightCommand`
# row schema. A command with a `permission` is only shown to users that hold
# the permission on the portal.
DEFAULT_COMMANDS = [
    {"command_id": u"add-sample", "title": u"Add Samples",
     "icon": u"fas fa-plus", "url": u"${portal_url}/samples/ar_add",
     "permission": AddAnalysisRequest, "keywords": u"new, create, register"},
    {"command_id": u"samples", "title": u"Samples",
     "icon": u"fas fa-vial", "url": u"${portal_url}/samples"},
    {"command_id": u"worksheets", "title": u"Worksheets",
     "icon": u"fas fa-th-list", "url": u"${portal_url}/worksheets"},
    {"command_id": u"clients", "title": u"Clients",
     "icon": u"fas fa-users", "url": u"${portal_url}/clients"},
    {"command_id": u"batches", "title": u"Batches",
     "icon": u"fas fa-layer-group", "url": u"${portal_url}/batches"},
    {"command_id": u"setup", "title": u"Setup",
     "icon": u"fas fa-cog", "url": u"${portal_url}/setup",
     "permission": ManageBika},
    {"command_id": u"logout", "title": u"Logout",
     "icon": u"fas fa-sign-out-alt", "url": u"${portal_url}/logout"},
]


class ISpotlightCatalog(Interface):
    """Row schema for a searchable catalog
    """

    catalog = schema.TextLine(
        title=_(u"Catalog"),
        description=_(
            u"The catalog id to search, e.g. senaite_catalog_sample"),
        required=True,
    )

    label = schema.TextLine(
        title=_(u"Label"),
        description=_(u"Label shown in the scope bar"),
        required=False,
        default=u"",
        missing_value=u"",
    )

    prefix = schema.TextLine(
        title=_(u"Prefix"),
        description=_(
            u"Short token to scope a search to this catalog, "
            u"e.g. 's' to search with 's:water'"),
        required=False,
        default=u"",
        missing_value=u"",
    )

    portal_types = schema.TextLine(
        title=_(u"Portal types"),
        description=_(
            u"Comma separated list of portal types to restrict the "
            u"search to"),
        required=False,
        default=u"",
        missing_value=u"",
    )

    index = schema.TextLine(
        title=_(u"Search index"),
        description=_(u"Searchable text index to query (optional override)"),
        required=False,
        default=u"",
        missing_value=u"",
    )

    sort_on = schema.TextLine(
        title=_(u"Sort on"),
        description=_(u"Index to sort the catalog results on"),
        required=False,
        default=u"",
        missing_value=u"",
    )

    sort_order = schema.Choice(
        title=_(u"Sort order"),
        values=[u"ascending", u"descending"],
        default=u"ascending",
        required=False,
    )

    enabled = schema.Bool(
        title=_(u"Enabled"),
        default=True,
        required=False,
    )


class ISpotlightCommand(Interface):
    """Row schema for a command palette action
    """

    command_id = schema.TextLine(
        title=_(u"ID"),
        description=_(u"Unique command identifier"),
        required=True,
    )

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title shown in the command palette"),
        required=True,
    )

    icon = schema.TextLine(
        title=_(u"Icon"),
        description=_(u"Icon class, e.g. 'fas fa-plus'"),
        required=False,
        default=u"",
        missing_value=u"",
    )

    url = schema.TextLine(
        title=_(u"URL"),
        description=_(
            u"Target URL, may contain the '${portal_url}' "
            u"placeholder"),
        required=True,
    )

    permission = schema.TextLine(
        title=_(u"Permission"),
        description=_(u"Zope permission required to see the command"),
        required=False,
        default=u"",
        missing_value=u"",
    )

    keywords = schema.TextLine(
        title=_(u"Keywords"),
        description=_(u"Comma separated list of extra search terms"),
        required=False,
        default=u"",
        missing_value=u"",
    )


class ISpotlightControlPanel(model.Schema):
    """Spotlight control panel settings
    """

    hotkey = schema.TextLine(
        title=_(u"Hotkey"),
        description=_(
            u"Keyboard shortcut to toggle the spotlight overlay. "
            u"Join modifier keys and the final key with '+', e.g. "
            u"'Control+Space', 'Meta+k' or 'Control+Shift+f'."),
        default=DEFAULT_HOTKEY,
        required=True,
    )

    max_results = schema.Int(
        title=_(u"Maximum results"),
        description=_(u"Maximum number of search results to return."),
        default=DEFAULT_MAX_RESULTS,
        required=True,
    )

    min_chars = schema.Int(
        title=_(u"Minimum characters"),
        description=_(
            u"Minimum number of characters before a search is "
            u"triggered."),
        default=2,
        required=True,
    )

    debounce = schema.Int(
        title=_(u"Search debounce (ms)"),
        description=_(
            u"Time in milliseconds to wait after the last keystroke "
            u"before sending the search request."),
        default=200,
        required=True,
    )

    enable_highlighting = schema.Bool(
        title=_(u"Highlight matches"),
        description=_(
            u"Highlight the matching parts of the search term in "
            u"the results."),
        default=True,
        required=False,
    )

    directives.widget(
        "catalogs",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    catalogs = schema.List(
        title=_(u"Catalogs"),
        description=_(
            u"The catalogs to search. Add-ons may append further "
            u"catalogs through their own registry profile."),
        value_type=DataGridRow(title=u"Catalog", schema=ISpotlightCatalog),
        default=list(DEFAULT_CATALOGS),
        required=False,
    )

    directives.widget(
        "commands",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    commands = schema.List(
        title=_(u"Commands"),
        description=_(
            u"The command palette actions. Add-ons may append "
            u"further commands through their own registry profile."),
        value_type=DataGridRow(title=u"Command", schema=ISpotlightCommand),
        default=list(DEFAULT_COMMANDS),
        required=False,
    )

    model.fieldset(
        "search",
        label=_(u"Search"),
        fields=["hotkey", "max_results", "min_chars", "debounce",
                "enable_highlighting"],
    )

    model.fieldset(
        "catalogs",
        label=_(u"Catalogs"),
        fields=["catalogs"],
    )

    model.fieldset(
        "commands",
        label=_(u"Commands"),
        fields=["commands"],
    )


class SpotlightControlPanelForm(RegistryEditForm):
    schema = ISpotlightControlPanel
    schema_prefix = PREFIX
    label = _("SENAITE Spotlight Settings")


SpotlightControlPanelView = layout.wrap_form(
    SpotlightControlPanelForm, ControlPanelFormWrapper)


# z3c.form / DataGrid stores empty optional cells as this sentinel string
NO_VALUE = u"<NO_VALUE>"


def clean(value):
    """Normalize empty DataGrid values (incl. the NO_VALUE sentinel) to None
    """
    if value in (None, u"", "", NO_VALUE):
        return None
    return value


def get_record(name, default=None):
    """Read a spotlight registry record by its short name
    """
    value = api.get_registry_record("{}.{}".format(PREFIX, name))
    if value is None:
        return default
    return value


def to_list(value):
    """Split a comma separated string into a list of trimmed tokens
    """
    value = clean(value)
    if not value:
        return []
    return [token.strip() for token in value.split(",") if token.strip()]


def parse_catalog(record):
    """Normalize a catalog row into a plain dictionary
    """
    return {
        "name": clean(record.get("catalog")),
        "label": clean(record.get("label")) or clean(record.get("catalog")),
        "prefix": clean(record.get("prefix")),
        "portal_types": to_list(record.get("portal_types")),
        "index": clean(record.get("index")),
        "sort_on": clean(record.get("sort_on")),
        "sort_order": clean(record.get("sort_order")) or "ascending",
    }


def parse_command(record):
    """Normalize a command row into a plain dictionary
    """
    return {
        "id": clean(record.get("command_id")),
        "title": clean(record.get("title")),
        "icon": clean(record.get("icon")) or "",
        "url": clean(record.get("url")) or "",
        "permission": clean(record.get("permission")),
        "keywords": to_list(record.get("keywords")),
    }


def get_catalogs():
    """Return the enabled catalog records as plain dictionaries
    """
    records = get_record("catalogs", default=DEFAULT_CATALOGS)
    catalogs = [
        parse_catalog(record) for record in records
        if record.get("enabled", True)
    ]
    # skip empty (e.g. auto-appended) rows without a catalog
    return [catalog for catalog in catalogs if catalog["name"]]


def get_commands():
    """Return the command palette records as plain dictionaries
    """
    records = get_record("commands", default=DEFAULT_COMMANDS)
    commands = [parse_command(record) for record in records]
    # skip empty (e.g. auto-appended) rows without an id or url
    return [command for command in commands
            if command["id"] and command["url"]]


def prettify_state(state):
    """Return a human readable label for a workflow state id
    """
    return api.safe_unicode(state).replace(u"_", u" ").strip().capitalize()


def get_review_states(catalog_name):
    """Return the distinct review states of a catalog as {id, title} dicts

    Used to drive the "is:<state>" autocomplete suggestions on the client.
    Returns an empty list for an unknown catalog, so a misconfigured catalog
    id can never break the viewlet that renders on every page.
    """
    tool = api.get_tool(catalog_name, default=None)
    if tool is None:
        return []
    index = tool._catalog.indexes.get("review_state")
    if index is None:
        return []
    states = []
    for value in sorted(index.uniqueValues()):
        if not value:
            continue
        states.append({"id": value, "title": prettify_state(value)})
    return states


def get_config():
    """Return the resolved spotlight configuration as a plain dictionary
    """
    return {
        "hotkey": get_record("hotkey", default=DEFAULT_HOTKEY),
        "max_results": get_record("max_results", default=DEFAULT_MAX_RESULTS),
        "min_chars": get_record("min_chars", default=2),
        "debounce": get_record("debounce", default=200),
        "highlight": get_record("enable_highlighting", default=True),
        "catalogs": get_catalogs(),
        "commands": get_commands(),
    }
