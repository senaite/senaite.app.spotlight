<div align="center">

  <a href="https://github.com/senaite/senaite.app.spotlight">
    <img src="static/logo.png" alt="senaite.app.spotlight" height="128" />
  </a>

  <p>MacOS like Spotlight search for SENAITE</p>

  <div>
    <a href="https://pypi.python.org/pypi/senaite.app.spotlight">
      <img src="https://img.shields.io/pypi/v/senaite.app.spotlight.svg?style=flat-square" alt="pypi-version" />
    </a>
    <a href="https://github.com/senaite/senaite.app.spotlight/pulls">
      <img src="https://img.shields.io/github/issues-pr/senaite/senaite.app.spotlight.svg?style=flat-square" alt="open PRs" />
    </a>
    <a href="https://github.com/senaite/senaite.app.spotlight/issues">
      <img src="https://img.shields.io/github/issues/senaite/senaite.app.spotlight.svg?style=flat-square" alt="open Issues" />
    </a>
    <a href="#">
      <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="pr" />
    </a>
    <a href="https://www.senaite.com">
      <img src="https://img.shields.io/badge/Made%20for%20SENAITE-%E2%AC%A1-lightgrey.svg" alt="Made for SENAITE" />
    </a>
  </div>
</div>


## About

Quickly find contents in SENAITE by pressing the configured hotkey
(`Ctrl-Space` by default) and start typing.

The spotlight is a React component that consumes the shared React instance
exposed by `senaite.core`. It searches the configured catalogs on the server
and narrows, sorts and highlights the results on the client. A command palette
allows navigating to or triggering registered actions directly.

See the screencast how to use it: https://www.youtube.com/watch?v=AIA5atToc-c


## Search syntax

The search term supports a few inline tokens:

- `/` opens the command palette and lists all available commands. Type after
  the slash to filter them, e.g. `/add`.
- `<prefix>:<term>` scopes the search to a single catalog, e.g. `s:water`
  searches only the catalog whose prefix is `s` (see the Catalogs setting).
- `is:<state>` filters by workflow state, e.g. `CA20 is:received` finds items
  matching `CA20` that are in the `received` state. Typing `is:` opens an
  autocomplete of the available states (scoped to the active catalog when a
  prefix is used, otherwise the union of all catalogs). The state is matched
  on whole, underscore-delimited segments of the catalog's review states (so
  `received` matches `sample_received` and `verified` matches both `verified`
  and `to_be_verified`, but `active` does not match `inactive`).

Tokens can be combined, e.g. `s:CA20 is:received`. The same tokens also work in
the search box of the standalone search page.


## Configuration

The spotlight has its own control panel at `@@spotlight-controlpanel`,
reachable from the SENAITE control panel ("Spotlight Settings") and from the
settings link inside the spotlight itself (shown to users with the
`senaite.core: Manage Bika` permission). The following settings are available:

- **Hotkey**: Keyboard shortcut to toggle the overlay, e.g. `Control+Space`,
  `Meta+k` or `Control+Shift+f`.
- **Maximum results** / **Minimum characters** / **Search debounce**: Tune the
  search behavior.
- **Highlight matches**: Highlight the matching parts of the search term.
- **Catalogs**: A grid of the catalogs to search. Every installed SENAITE
  catalog is listed here automatically (see Catalog auto-discovery below).
  Each row has a `catalog`, `label`, optional `prefix` (scopes a search to a
  single catalog, e.g. typing `s:water`), `portal_types`, `index`, `sort_on`,
  `sort_order` and `enabled`.
- **Commands**: A grid of command palette actions. Each row has an `id`,
  `title`, `icon`, `url` (may contain the `${portal_url}` placeholder), an
  optional `permission` (the command is only shown to users holding it) and
  `keywords`.

### Catalog auto-discovery

Every installed SENAITE catalog is added to the search scope automatically.
Discovery finds all catalog tools that provide the `ISenaiteCatalogObject`
marker (implemented by `senaite.core`'s `BaseCatalog`, and so inherited by
every add-on catalog), which means installing an add-on such as
`senaite.storage` makes its catalog searchable without any configuration.

Discovered catalogs show up as rows in the **Catalogs** grid, so the control
panel always lists all catalogs. From there you can:

- Uncheck **Enabled** to exclude a catalog from the search.
- Set a **Label** shown in the scope bar, or a **Prefix** for scoped searches
  (e.g. `s:water`).
- Reorder the rows to change the order of the scope tabs.

The internal bookkeeping catalogs (analyses, audit log, import logs,
attachments) ship as disabled rows, so they stay out of the search by default
while remaining one checkbox away. Saving the control panel persists the list;
catalogs installed afterwards keep appearing automatically.

The settings are stored in the registry under the `senaite.app.spotlight`
prefix. Catalogs need no manual entry thanks to auto-discovery, but add-ons
can still contribute command palette actions (or pre-seed a catalog's label
or prefix) by shipping their own `registry.xml` that appends to the list
fields with `purge="false"`:

```xml
<registry>
  <records interface="senaite.app.spotlight.controlpanel.ISpotlightControlPanel"
           prefix="senaite.app.spotlight">
    <value key="commands" purge="false">
      <element>
        <value key="command_id">my-action</value>
        <value key="title">My Action</value>
        <value key="url">${portal_url}/my-view</value>
      </element>
    </value>
  </records>
</registry>
```


## Customizing the Search

The spotlight search calls an multi adapter to get the search results.

This adapter needs to implement the `ISpotlightSearchAdapter` and adapts the
context and the request. It must be implemented that it returns a dictionary
containing the search results when calling it.

The results dictionary has to provide at least a list of `items`, where each
item is a dictionary containing the following data:

```python
{
    "id": id,
    "title": title,
    "title_or_id": title or id,
    "description": description,
    "url": url,
    "parent_title": parent_title,
    "parent_url": parent_url,
    "icon": icon,
}
```

A simple implementation looks like this:

```python
dummy_item = {
    "id": "test",
    "title": "Test Item",
    "title_or_id": "Test Item",
    "description": "A search result item",
    "url": "",
    "parent_title": "",
    "parent_url": "",
    "icon": "",
}

@implementer(ISpotlightSearchAdapter)
class MySpotlightSearchAdapter(object):
    """Spotlight Search Adapter
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        items = [dummy_item]

        return {
            "count": len(items),
            "items": items,
      }
```

And is registered like this:

```xml
<!-- A custom Spotlight Search Adapter -->
<adapter
    for="*
        .interfaces.IMyBrowserLayer"
    factory=".adapters.MySpotlightSearchAdapter" />
```

Note that the custom adapter needs to be more specific than the default adapter.
Therefore, adapting it either to your custom browser layer or to a specific
content type interface.


## Development

The JavaScript code for `senaite.app.spotlight` is built via
[Webpack](https://webpack.js.org/). To setup the development environment, go to
the root of this package install the required dependencies with `yarn`:

```shell
$ yarn install
```

Note: You need to have `node` installed.

The React source code is located at `webpack/app` and is built into
`src/senaite/app/spotlight/static/js`.

After this, you can start watching for changes in the code files:

```shell
$ yarn watch
```

When you are done, you can create a production build of the JavaScript with this command:

```shell
$ yarn build
```


## License

**SENAITE.APP.SPOTLIGHT** Copyright (C) RIDING BYTES & NARALABS

This program is free software; you can redistribute it and/or modify it under
the terms of the [GNU General Public License version
2](https://github.com/senaite/senaite.app.spotlight/blob/master/LICENSE)
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
