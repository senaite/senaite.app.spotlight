<div align="center">

  <a href="https://github.com/senaite/senaite.core.spotlight">
    <img src="static/logo.png" alt="senaite.core.spotlight" height="128" />
  </a>

  <p>MacOS like Spotlight search for SENAITE</p>

  <div>
    <a href="https://pypi.python.org/pypi/senaite.core.spotlight">
      <img src="https://img.shields.io/pypi/v/senaite.core.spotlight.svg?style=flat-square" alt="pypi-version" />
    </a>
    <a href="https://github.com/senaite/senaite.core.spotlight/pulls">
      <img src="https://img.shields.io/github/issues-pr/senaite/senaite.core.spotlight.svg?style=flat-square" alt="open PRs" />
    </a>
    <a href="https://github.com/senaite/senaite.core.spotlight/issues">
      <img src="https://img.shields.io/github/issues/senaite/senaite.core.spotlight.svg?style=flat-square" alt="open Issues" />
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

Quickly find contents in SENAITE by pressing `Ctrl-Space` and start typing.

See the screencast how to use it: https://www.youtube.com/watch?v=AIA5atToc-c


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

The JavaScript code for `senaite.core.spotlight` is built via
[Webpack](https://webpack.js.org/). To setup the development environment, go to
the root of this package install the required dependencies with `yarn`:

```shell
$ yarn install
```

Note: You need to have `node` installed.

The JavaScript code is located at `src/senaite/core/spotlight/static/src`.

After this, you can start watching for changes in the code files:

```shell
$ yarn watch
```

When you are done, you can create a production build of the JavaScript with this command:

```shell
$ yarn build
```


## License

**SENAITE.CORE.SPOTLIGHT** Copyright (C) 2019-2020 RIDING BYTES & NARALABS

This program is free software; you can redistribute it and/or modify it under
the terms of the [GNU General Public License version
2](https://github.com/senaite/senaite.core.spotlight/blob/master/LICENSE)
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
