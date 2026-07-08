Catalog auto-discovery
======================

The spotlight search scope is assembled from two sources: the catalogs
configured in the control panel registry, and the catalogs discovered
automatically from every installed SENAITE catalog. Add-on catalogs (e.g.
the one shipped by `senaite.storage`) therefore become searchable without
any manual configuration.

Running this test from the buildout directory::

    bin/test -m senaite.app.spotlight -t CatalogDiscovery

Test Setup
----------

Needed imports:

    >>> from senaite.app.spotlight import controlpanel as cp
    >>> from senaite.app.spotlight.adapters import strip_html


Discovering installed catalogs
------------------------------

Discovery enumerates the portal-root catalog tools that provide the
`ISenaiteCatalogObject` marker (implemented by `senaite.core`'s
`BaseCatalog` and inherited by every add-on catalog):

    >>> names = cp.discover_catalog_names()
    >>> "senaite_catalog_sample" in names
    True
    >>> "senaite_catalog_setup" in names
    True

The result is sorted and free of duplicates:

    >>> names == sorted(set(names))
    True


Assembling the search scope
---------------------------

`get_catalogs` merges the configured rows with the discovered catalogs.
The active search scope holds the enabled catalogs:

    >>> scope = sorted(c["name"] for c in cp.get_catalogs())
    >>> "senaite_catalog_sample" in scope
    True
    >>> "senaite_catalog_setup" in scope
    True

The internal bookkeeping catalogs ship as disabled rows, so they stay out
of the default scope:

    >>> "senaite_catalog_auditlog" in scope
    False
    >>> "senaite_catalog_analysis" in scope
    False


Showing every catalog in the control panel
-------------------------------------------

The control panel grid lists all installed catalogs, the disabled ones
included, so any of them can be labeled, prefixed or toggled without
typing a catalog id:

    >>> rows = cp.merged_catalog_rows()
    >>> by_id = dict((r["catalog"], r) for r in rows)
    >>> by_id["senaite_catalog_sample"]["enabled"]
    True
    >>> by_id["senaite_catalog_auditlog"]["enabled"]
    False

Every discovered catalog is represented:

    >>> set(names).issubset(set(by_id))
    True


Complete, unicode rows
----------------------

Rows are always complete and store unicode values, so the DataGrid never
renders the `<NO_VALUE>` marker for a missing cell:

    >>> row = by_id["senaite_catalog_sample"]
    >>> sorted(row.keys())
    ['catalog', 'enabled', 'index', 'label', 'portal_types', 'prefix', 'sort_on', 'sort_order']

`complete_catalog_row` fills the missing cells and coerces byte strings to
unicode, which a programmatic registry write requires:

    >>> row = cp.complete_catalog_row({"catalog": b"senaite_catalog_x"})
    >>> row["catalog"] == u"senaite_catalog_x"
    True
    >>> isinstance(row["catalog"], unicode)
    True
    >>> row["sort_order"]
    u'ascending'
    >>> row["enabled"]
    True


Plain text descriptions
-----------------------

Result descriptions are stripped of HTML, so a rich-text field renders as
plain text in the search overlay instead of showing raw tags:

    >>> strip_html(u"<address>Street 3<br/>City</address>")
    u'Street 3 City'
    >>> strip_html(u"")
    u''
    >>> strip_html(None)
    u''
