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
from plone.registry.interfaces import IRegistry
from plone.registry.recordsproxy import RecordsProxy
from plone.supermodel import model
from plone.z3cform import layout
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
from senaite.core.permissions import AddAnalysisRequest
from senaite.core.permissions import ManageBika
from senaite.core.schema.registry import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from zope import schema
from zope.component import getUtility
from zope.interface import Interface

# Registry prefix under which the settings are stored.
PREFIX = "senaite.app.spotlight"

# Default hotkey to toggle the spotlight overlay. The value follows the
# `KeyboardEvent` semantics used on the client: modifier names joined with "+"
# and the final key, e.g. "Control+Space", "Meta+k" or "Control+Shift+f".
DEFAULT_HOTKEY = u"Control+Space"

# Default maximum number of search results returned by the search adapter.
DEFAULT_MAX_RESULTS = 25

# z3c.form / DataGrid stores empty optional cells as this sentinel string
NO_VALUE = u"<NO_VALUE>"

# Empty defaults for every `ISpotlightCatalog` cell. Rows are always stored
# with all keys present so the DataGrid widget renders the optional cells
# blank instead of the z3c.form `<NO_VALUE>` marker for absent keys.
CATALOG_ROW_DEFAULTS = {
    "catalog": u"",
    "label": u"",
    "prefix": u"",
    "portal_types": u"",
    "index": u"",
    "sort_on": u"",
    "sort_order": u"ascending",
    "enabled": True,
    "show_for_clients": True,
}

# Empty defaults for every `ISpotlightCommand` cell (same rationale as
# `CATALOG_ROW_DEFAULTS`): rows are stored complete so the DataGrid never
# renders the `<NO_VALUE>` marker for a blank optional cell.
COMMAND_ROW_DEFAULTS = {
    "command_id": u"",
    "title": u"",
    "icon": u"",
    "url": u"",
    "permission": u"",
    "keywords": u"",
}


def complete_row(row, defaults):
    """Return `row` as a full dict based on `defaults`.

    Missing (or `None`) cells, and cells left as the z3c.form `<NO_VALUE>`
    sentinel, are filled from `defaults`, so a stored row never carries an
    absent key or a raw `<NO_VALUE>` marker. Byte-string values are coerced
    to unicode: the row schema fields are `TextLine` (unicode), and a
    programmatic registry write validates strictly (unlike the GenericSetup
    import, which coerces silently).
    """
    full = dict(defaults)
    for key, value in row.items():
        if value is None or value == NO_VALUE:
            continue
        if isinstance(value, bytes):
            value = api.safe_unicode(value)
        full[key] = value
    return full


def complete_catalog_row(row):
    """Return `row` as a full `ISpotlightCatalog` dict.
    """
    return complete_row(row, CATALOG_ROW_DEFAULTS)


def complete_command_row(row):
    """Return `row` as a full `ISpotlightCommand` dict.
    """
    return complete_row(row, COMMAND_ROW_DEFAULTS)


# Default catalogs to search. Each entry maps to the `ISpotlightCatalog` row
# schema. A `prefix` allows scoping a search to a single catalog, e.g. typing
# "s:water" only searches the catalog whose prefix is "s".
#
# Installed SENAITE catalogs not listed here are appended automatically by
# `get_catalogs` (auto-discovery). Internal bookkeeping catalogs (analyses,
# audit trail, import logs, attachments) are listed with `enabled` False so
# they are known to the discovery pass (hence not re-added as active scopes)
# but stay off by default; flip `enabled` to search them.
DEFAULT_CATALOGS = [complete_catalog_row(row) for row in [
    {"catalog": "senaite_catalog_sample", "label": u"Samples",
     "prefix": u"s"},
    {"catalog": "senaite_catalog_setup", "label": u"Setup",
     "show_for_clients": False},
    {"catalog": "senaite_catalog_worksheet", "label": u"Worksheets",
     "prefix": u"w", "show_for_clients": False},
    {"catalog": "senaite_catalog", "label": u"SENAITE"},
    {"catalog": "senaite_catalog_client", "label": u"Clients",
     "prefix": u"c", "show_for_clients": False},
    {"catalog": "senaite_catalog_contact", "label": u"Contacts",
     "show_for_clients": False},
    {"catalog": "senaite_catalog_report", "label": u"Reports",
     "prefix": u"r", "enabled": False},
    {"catalog": "senaite_catalog_label", "label": u"Labels",
     "enabled": False},
    {"catalog": "senaite_catalog_analysis", "label": u"Analyses",
     "enabled": False},
    {"catalog": "senaite_catalog_auditlog", "label": u"Audit Log",
     "enabled": False},
    {"catalog": "senaite_catalog_autoimportlog", "label": u"Auto Import Log",
     "enabled": False},
    {"catalog": "senaite_attachments_catalog", "label": u"Attachments",
     "enabled": False},
]]

# Zope meta_type shared by every `CatalogTool`, used to enumerate the
# catalog tools in the portal root without waking unrelated objects.
CATALOG_META_TYPE = "Plone Catalog Tool"

# Pseudo-states surfaced in the "is:" autocomplete that map to the
# `is_active` boolean index instead of a workflow `review_state`.
ACTIVE_STATE_IDS = (u"active", u"inactive")

# Default command palette actions. Each entry maps to the `ISpotlightCommand`
# row schema. A command with a `permission` is only shown to users that hold
# the permission on the portal.
DEFAULT_COMMANDS = [complete_command_row(row) for row in [
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
]]


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

    show_for_clients = schema.Bool(
        title=_(u"Show for clients"),
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
            u"The catalogs to search. Every installed SENAITE catalog is "
            u"listed here automatically; set a label or prefix, reorder, or "
            u"uncheck Enabled to exclude one. Saving persists the list."),
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


class MergedCatalogsProxy(RecordsProxy):
    """Registry proxy that lists every installed catalog in the grid.

    Reading `catalogs` returns the stored rows plus a row for each
    auto-discovered catalog not yet listed (see `merged_catalog_rows`),
    so the control panel always shows all catalogs and any of them can be
    toggled or labeled without typing an id. Every other attribute and
    all writes behave like the base proxy, so saving persists the
    submitted rows to the registry as usual.
    """

    def __getattr__(self, name):
        if name == "catalogs":
            return merged_catalog_rows()
        return RecordsProxy.__getattr__(self, name)


class SpotlightControlPanelForm(RegistryEditForm):
    schema = ISpotlightControlPanel
    schema_prefix = PREFIX
    label = _("SENAITE Spotlight Settings")

    def getContent(self):
        """Bind the form to a proxy that lists all catalogs in the grid
        """
        return MergedCatalogsProxy(
            getUtility(IRegistry), self.schema, prefix=self.schema_prefix)


SpotlightControlPanelView = layout.wrap_form(
    SpotlightControlPanelForm, ControlPanelFormWrapper)


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


def to_bool(value, default=True):
    """Coerce a DataGrid value to a boolean, treating empty cells as default
    """
    if value in (None, u"", "", NO_VALUE):
        return default
    return bool(value)


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
        "show_for_clients": to_bool(record.get("show_for_clients", True)),
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


def discover_catalog_names():
    """Return the ids of all installed SENAITE catalogs.

    Discovery relies on the `ISenaiteCatalogObject` marker that
    `senaite.core`'s `BaseCatalog` implements, so every add-on catalog
    derived from it (e.g. senaite.storage's `senaite_catalog_storage`)
    is found without any further registration. Enumeration is scoped to
    the catalog `meta_type` so unrelated portal-root objects are not
    woken on each request.
    """
    portal = api.get_portal()
    names = []
    for obj in portal.objectValues(CATALOG_META_TYPE):
        if ISenaiteCatalogObject.providedBy(obj):
            names.append(obj.getId())
    return sorted(names)


def catalog_title(name):
    """Return the title of the catalog tool `name`, falling back to `name`.
    """
    tool = api.get_tool(name, default=None)
    if tool is None:
        return api.safe_unicode(name)
    return api.safe_unicode(clean(getattr(tool, "title", None)) or name)


def discovered_catalog(name):
    """Build a catalog config dict for an auto-discovered catalog.

    Mirrors the shape returned by `parse_catalog`. The label defaults to
    the catalog tool title (an operator can rename it in the control
    panel); no search prefix is assigned automatically.
    """
    return {
        "name": name,
        "label": catalog_title(name),
        "prefix": None,
        "portal_types": [],
        "index": None,
        "sort_on": None,
        "sort_order": "ascending",
        "show_for_clients": True,
    }


def get_catalogs():
    """Return the searchable catalog records as plain dictionaries.

    Merges the explicitly configured catalogs (registry) with the
    catalogs auto-discovered from all installed SENAITE catalogs.
    Configured rows win: they carry the label, prefix, ordering and the
    `enabled` flag, and a configured catalog is never re-added by the
    discovery pass, even when it is disabled (this is how the internal
    catalogs shipped as disabled `DEFAULT_CATALOGS` rows stay off).
    Discovered catalogs that are not configured are appended with a
    derived label, so installing an add-on that registers a catalog
    surfaces it in the search without manual configuration.
    """
    records = get_record("catalogs", default=DEFAULT_CATALOGS)
    catalogs = [
        parse_catalog(record) for record in records
        if record.get("enabled", True)
    ]
    # skip empty (e.g. auto-appended) rows without a catalog
    catalogs = [catalog for catalog in catalogs if catalog["name"]]

    # every catalog named in the config (enabled or not) is "known" and
    # must not be re-added by discovery, so a deliberately disabled row
    # stays disabled
    known = {record.get("catalog") for record in records
             if record.get("catalog")}
    for name in discover_catalog_names():
        if name in known:
            continue
        catalogs.append(discovered_catalog(name))
        known.add(name)
    return catalogs


def is_client_only_user():
    """Whether the current user is a client contact without lab access

    A client contact is bound to a client, which `api.get_current_client`
    resolves via the user's contact link. Lab staff (lab contacts, managers,
    anonymous, ...) are never bound to a client, so this never restricts lab
    users regardless of how the "Client" role is granted.
    """
    return api.get_current_client() is not None


def get_searchable_catalogs():
    """Return the catalogs the current user is allowed to search

    Same as `get_catalogs`, but for client-only users (client contacts)
    drops every catalog whose `show_for_clients` flag is off, so a client
    contact never searches lab objects they cannot access (setup, clients,
    contacts by default). `get_catalogs` stays pure; the role-aware
    filtering lives here, so every search entry point (modal adapter,
    full-page search) shares it.
    """
    catalogs = get_catalogs()
    if not is_client_only_user():
        return catalogs
    return [c for c in catalogs if c.get("show_for_clients", True)]


def discovered_catalog_row(name):
    """Build a full `ISpotlightCatalog` grid row for a discovered catalog.

    Enabled by default (matching the search-time behavior), labeled from
    the catalog tool title. Used to seed the control panel grid so every
    installed catalog is visible and toggleable without typing an id.
    """
    return complete_catalog_row({
        "catalog": name,
        "label": catalog_title(name),
        "enabled": True,
    })


def merged_catalog_rows():
    """Return the full catalog row set for the control panel grid.

    The stored rows plus a row for every installed catalog not yet
    listed, so the grid always shows all catalogs and any of them can be
    enabled, disabled, labeled or prefixed without typing a catalog id.
    Saving the form persists whatever rows are submitted (materializing
    the discovered ones); newly installed add-on catalogs keep appearing
    here on the next render.
    """
    records = get_record("catalogs", default=DEFAULT_CATALOGS)
    rows = [complete_catalog_row(dict(record)) for record in records]
    known = {row["catalog"] for row in rows if row.get("catalog")}
    for name in discover_catalog_names():
        if name in known:
            continue
        rows.append(discovered_catalog_row(name))
        known.add(name)
    return rows


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


def has_active_index(catalog_name):
    """Whether the catalog carries the `is_active` boolean index
    """
    tool = api.get_tool(catalog_name, default=None)
    if tool is None:
        return False
    return "is_active" in tool._catalog.indexes


def get_state_suggestions(catalog_name):
    """Return the "is:<state>" autocomplete suggestions for a catalog

    The active/inactive pseudo-states (mapped to the `is_active` boolean
    index) come first when the catalog supports them, followed by the
    distinct workflow review states. Used to drive the "is:" autocomplete.
    """
    suggestions = []
    if has_active_index(catalog_name):
        for state_id in ACTIVE_STATE_IDS:
            suggestions.append(
                {"id": state_id, "title": prettify_state(state_id)})
    existing = {suggestion["id"] for suggestion in suggestions}
    for state in get_review_states(catalog_name):
        if state["id"] not in existing:
            suggestions.append(state)
    return suggestions


def get_config():
    """Return the resolved spotlight configuration as a plain dictionary
    """
    return {
        "hotkey": get_record("hotkey", default=DEFAULT_HOTKEY),
        "max_results": get_record("max_results", default=DEFAULT_MAX_RESULTS),
        "min_chars": get_record("min_chars", default=2),
        "debounce": get_record("debounce", default=200),
        "highlight": get_record("enable_highlighting", default=True),
        "catalogs": get_searchable_catalogs(),
        "commands": get_commands(),
    }
