<div align="center">

  <a href="https://github.com/senaite/senaite.core.spotlight">
    <img src="static/logo.png" alt="senaite.core.spotlight" height="128" />
  </a>

  <p>MacOS like Spotlight search for SENAITE</p>

  <div>
    <a href="https://pypi.python.org/pypi/senaite.core.spotlight">
      <img src="https://img.shields.io/pypi/v/senaite.core.spotlight.svg?style=flat-square" alt="pypi-version" />
    </a>
    <a href="https://travis-ci.org/senaite/senaite.core.spotlight">
      <img src="https://img.shields.io/travis/senaite/senaite.core.spotlight.svg?style=flat-square" alt="travis-ci" />
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
context and the request and returns a dictionary containing the search Vresults
when calling it.

The results dictionary has to provide at least a list of `items`, where each
item is a dictionary containing this information:

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

A simple implementation looks like this:

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

And get registered like this:

    <!-- A custom Spotlight Search Adapter -->
    <adapter
        for="*
            .interfaces.IMyBrowserLayer"
        factory=".adapters.MySpotlightSearchAdapter" />
