2.7.1 (unreleased)
------------------

- #33 Rewrite the spotlight search as a React component
- Consume the shared React instance exposed by senaite.core (Webpack
  externals) instead of bundling a copy
- Added a dedicated spotlight control panel (hotkey, catalogs, commands,
  result limit, highlighting) reachable from the spotlight settings link
- Allow a per-user trigger hotkey, stored in localStorage and defaulting to
  the configured global hotkey; record or reset it from the spotlight footer
- Added a command palette to navigate or trigger registered actions, filtered
  by the permissions of the current user; type "/" to list all commands
  ("/add" to filter them). Besides the configured commands (Add Samples,
  Samples, Worksheets, Clients, Batches, Setup, Logout), the palette lazily
  lists "New <type>" create actions for the setup content types, only for
  users that may access the setup
- Added catalog and content type narrowing, prefix scoping (e.g. "s:water"),
  client side sorting and match highlighting
- Browse a catalog by scoping to it (chip or "s:" prefix) with no search term:
  the first results of that catalog are listed
- Show a secondary identifier (e.g. the client id) next to a result title to
  disambiguate same-named results
- Rank the merged multi-catalog results by relevance to the search term in
  Python (nearest match first), using brain metadata only so objects are only
  woken up for the results that are actually shown
- Added workflow state filtering via an "is:<state>" token, e.g.
  "s:CA20 is:received" finds samples matching CA20 in the received state.
  Typing "is:" shows an autocomplete of the available states (scoped to the
  active catalog)
- Added a standalone full page search at "@@spotlight-search" (listing based)
  reachable from the spotlight, with catalog switcher tabs, filters and
  pagination
- Harden against runtime errors: a misconfigured catalog id no longer breaks
  page rendering, request params are coerced safely, and the breadcrumb parent
  walk is depth-bounded
- Neutralize the "-" operator in search terms so IDs like "WS-001" no longer
  collapse the ZCTextIndex search
- Narrow single token / barcode like searches client side so broadened catalog
  matches (e.g. "CA-01-0" also matching "CA-02-01") are filtered out
- Treat empty control panel DataGrid cells (the "<NO_VALUE>" sentinel) as
  unset, so a blank "sort_on"/"portal_types"/"index" no longer breaks the
  search (e.g. with prefix scoping like "w:WS-00")
- Ignore invalid/non-sortable "sort_on" indexes and handle catalog errors
  gracefully, so a misconfigured catalog no longer breaks the whole search
- Redesigned the look and feel as a modern command palette with dark mode


2.7.0 (unreleased)
------------------

- #32 Handle catalog search errors gracefully
- #31 JQuery3 compatibility


2.6.0 (2025-04-04)
------------------

- Version 2.5.0 -> 2.6.0


2.5.0 (2024-01-03)
------------------

- #30 Compatibility with core#2368 (Drop usage of portal_catalog tool)


2.4.0 (2023-03-10)
------------------

- Version 2.3.0 -> 2.4.0


2.3.0 (2022-10-03)
------------------

- Version 2.2.0 -> 2.3.0


2.2.0 (2022-06-10)
------------------

- #27 Use searchable text index converter from catalog API
- #26 Improve spotlight search results


2.1.0 (2022-01-05)
------------------

- #25 Changed catalog imports for compatibility with senaite.core#1872
- Updated resources


2.0.0 (2021-07-26)
------------------

- #7 Use absolute portal URL for spotlight JS


2.0.0rc3 (2021-01-04)
---------------------

- Updated resources
- Updated build system to Webpack 5


2.0.0rc2 (2020-10-13)
---------------------

- Updated resources


2.0.0rc1 (2020-08-05)
---------------------

- Compatibility with `senaite.core` 2.x


1.0.3 (2020-08-04)
------------------

- updated resources


1.0.2 (2020-03-02)
------------------

- #2 Fix visible spotlight viewlet on page load
- #1 Added missing dependency to `senaite.jsonapi`


1.0.1 (2020-02-04)
------------------

- Minimized JS code from 124K to 53K


1.0.0 (2020-02-04)
------------------

- Initial release
