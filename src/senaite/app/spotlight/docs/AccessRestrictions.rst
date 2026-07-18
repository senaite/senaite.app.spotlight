Search access restrictions
==========================

The spotlight search hides two things that a user should not see: inactive
(deactivated) objects, and the lab-only catalogs (setup, worksheets,
clients, contacts) when the user is a client contact. Inactive objects have
an escape hatch (the "is:inactive" token); the catalog visibility is driven
by a per-catalog "show_for_clients" flag in the control panel, so an
operator can opt any catalog in or out for client contacts.

Running this test from the buildout directory::

    bin/test -m senaite.app.spotlight -t AccessRestrictions

Test Setup
----------

Needed imports:

    >>> from bika.lims import api
    >>> from senaite.app.spotlight import controlpanel as cp
    >>> from senaite.app.spotlight.adapters import make_query


Hiding inactive objects by default
----------------------------------

Every standard SENAITE catalog inherits the `is_active` boolean index from
`BaseCatalog`. Without a state token, the query filters on active objects
only, so deactivated objects stay out of the results:

    >>> sample_catalog = {"name": "senaite_catalog_sample"}
    >>> query = make_query(sample_catalog, "water", 10)
    >>> query["is_active"]
    True


Revealing inactive objects with the escape hatch
------------------------------------------------

Power users can still find deactivated objects with the "is:inactive"
token. It maps to the `is_active` boolean index (not the workflow
`review_state`), so the query pins to inactive objects:

    >>> query = make_query(sample_catalog, "water", 10, state="inactive")
    >>> query["is_active"]
    False

The "is:active" token restricts to active objects explicitly:

    >>> query = make_query(sample_catalog, "water", 10, state="active")
    >>> query["is_active"]
    True

The active-state tokens map to the `is_active` boolean index only, and are
kept distinct from the workflow `review_state` resolution, so "is:inactive"
never leaks into a `review_state` query:

    >>> query = make_query(sample_catalog, "water", 10, state="inactive")
    >>> "review_state" in query
    False


Catalogs without the index are searched unchanged
-------------------------------------------------

The active filter is guarded by the catalog actually having the `is_active`
index. Standard SENAITE catalogs inherit it from `BaseCatalog`, so the
sample catalog is filtered:

    >>> "is_active" in make_query(sample_catalog, "water", 10)
    True

A catalog without the index (e.g. the `uid_catalog` the search falls back
to) is left untouched by the guard, so search is unchanged for it:

    >>> cp.has_active_index("senaite_catalog_sample")
    True
    >>> cp.has_active_index("uid_catalog")
    False


Surfacing active/inactive in the "is:" autocomplete
---------------------------------------------------

To make the active-only default discoverable, the "is:" autocomplete offers
the active/inactive pseudo-states for every catalog that carries the
`is_active` index, ahead of the workflow states:

    >>> states = cp.get_state_suggestions("senaite_catalog_sample")
    >>> [s["id"] for s in states[:2]]
    [u'active', u'inactive']
    >>> states[0]["title"]
    u'Active'

A catalog without the index offers no active/inactive pseudo-states:

    >>> [s["id"] for s in cp.get_state_suggestions("uid_catalog")
    ...  if s["id"] in (u"active", u"inactive")]
    []


Hiding lab-only catalogs from client-only users
-----------------------------------------------

The lab-only catalogs ship with the "show_for_clients" flag turned off,
while the rest default to on:

    >>> by_name = dict((c["name"], c) for c in cp.get_catalogs())
    >>> by_name["senaite_catalog_setup"]["show_for_clients"]
    False
    >>> by_name["senaite_catalog_contact"]["show_for_clients"]
    False
    >>> by_name["senaite_catalog_sample"]["show_for_clients"]
    True

`get_searchable_catalogs` is the single choke point that both search entry
points use. Lab staff (the test user is a lab manager) can search the lab
catalogs (setup, clients, contacts):

    >>> names = [c["name"] for c in cp.get_searchable_catalogs()]
    >>> all(name in names for name in (
    ...     "senaite_catalog_setup",
    ...     "senaite_catalog_client",
    ...     "senaite_catalog_contact"))
    True

A client contact is bound to a client, which `api.get_current_client`
resolves. Simulate a client-only user: the lab-only catalogs are dropped
from the searchable scope, while the sample catalog remains:

    >>> orig = api.get_current_client
    >>> api.get_current_client = lambda: object()
    >>> names = [c["name"] for c in cp.get_searchable_catalogs()]
    >>> any(name in names for name in (
    ...     "senaite_catalog_setup",
    ...     "senaite_catalog_client",
    ...     "senaite_catalog_contact"))
    False
    >>> "senaite_catalog_sample" in names
    True

Restore the original resolver, so lab staff keep their full scope:

    >>> api.get_current_client = orig
    >>> "senaite_catalog_setup" in [
    ...     c["name"] for c in cp.get_searchable_catalogs()]
    True
