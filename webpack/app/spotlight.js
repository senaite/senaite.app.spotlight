import {
  Model,
  View,
  Collection
} from "backbone";

import {
  template,
  debounce,
  each
} from "underscore";

import "./spotlight.scss";

// Single search result model
class SearchResult extends Model {
  defaults() {
    return {
      id: "",
      title: "",
      url: "",
      icon: "",
      title_or_id: "",
      parent_title: "",
      parent_url: ""
    };
  }
}

// Collection of search results
class SearchResults extends Collection {
  get model() {
    return SearchResult;
  }
}

// View for a single result row
class ResultView extends View {
  get tagName() {
    return "tr";
  }

  get template() {
    return template($("#item-template").html());
  }

  render() {
    this.$el.html(this.template(this.model.toJSON()));
    return this;
  }
}

// View for the results table
class ResultsView extends View {

  get template() {
    return template($("#results-template").html());
  }
  initialize() {
    this.listenTo(this.collection, "results:changed", this.render);
  }

  render() {
    const data = {
      count: this.collection.length
    };
    this.$el.html(this.template(data));
    this.collection.each((result, index) => {
      this.addResult(result, index);
    });
    return this;
  }

  addResult(model, index) {
    const className = index % 2 === 0 ? "even" : "odd";
    const view = new ResultView({ model, className });
    this.$el.find("tbody").append(view.render().el);
  }
}

// Top-level search view
class SearchView extends View {
  get el() {
    return "#spotlight";
  }

  get events() {
    return {
      "keyup #spotlight-search-field": "onKeyup",
      "keypress #spotlight-search-field": "onKeyup",
      "click #spotlight-clear-button": "onClear"
    };
  }

  initialize() {
    this.resultsView = new ResultsView({ collection: this.collection });
  }

  onClear(event) {
    event.preventDefault();
    this.$("#spotlight-search-field").val("");
    this.trigger("query:changed", "");
  }

  onKeyup(event) {
    const code = event.keyCode || event.which;
    if ([13, 38, 40].includes(code)) {
      event.preventDefault();
      event.stopPropagation();
      return this.selectRow(event);
    }
    const value = this.$("#spotlight-search-field").val();
    this.trigger("query:changed", value);
  }

  selectRow(event) {
    const code = event.keyCode;
    const table = $(".spotlight-overlay #search-results");
    const results = $("tbody tr", table);
    if (results.length === 0) return;

    const active = $("tr.selected", table);
    if (active.length === 0) {
      results.first().addClass("selected");
      return;
    }

    let next;
    if (code === 38) {
      next = active.prev();
    }
    else if (code === 40) {
      next = active.next();
    }
    else if (code === 13) {
      const href = $("a.link", active).attr("href");
      if (href) location.href = href;
      return;
    }

    active.removeClass("selected");
    next.addClass("selected");
    next[0]?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  render() {
    this.$("#search-results-wrapper").html(this.resultsView.el);
    return this;
  }
}

// Search controller
class SpotlightController extends View {
  get el() {
    return "#spotlight";
  }

  initialize() {
    this.searchResults = new SearchResults();
    this.searchView = new SearchView({ collection: this.searchResults });
    this.searchView.render();
    this.lazySearch = debounce(this.search, 500);
    this.listenTo(this.searchView, "query:changed", this.lazySearch);
  }

  get_csrf_token() {
    return document.querySelector("#protect-script").dataset.token;
  }

  get_portal_url() {
    return document.body.dataset.portalUrl;
  }

  get_api_url(endpoint) {
    const base = this.get_portal_url();
    const params = location.search;
    return `${base}/@@API/spotlight/${endpoint}${params}`;
  }

  get_json(url, options = {}) {
    const data = JSON.stringify(options.data || {});
    const method = options.method || "POST";
    const init = {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": this.get_csrf_token()
      },
      body: method === "POST" ? data : null,
      credentials: "include"
    };
    return fetch(new Request(url, init)).then(res => {
      if (!res.ok) return res.json().then(json => { throw new Error(json.error || "Unknown error") });
      return res.json();
    });
  }

  search(query) {
    this.searchResults.reset();
    const url = this.get_api_url("search");
    const options = { data: { q: query, limit: 5 } };
    this.get_json(url, options).then(data => {
      each(data.items, result => this.searchResults.add(new SearchResult(result)));
      this.searchResults.trigger("results:changed");
    });
  }
}

// Spotlight entry point
class Spotlight {
  constructor() {
    this.map = {};
    this.spotlight = $("#spotlight");
    this.controller = new SpotlightController();

    // Modal support
    $("#spotlight").on("shown.bs.modal", () => {
      $("#spotlight-search-field").trigger("focus");
    });

    $(document).on("keydown keyup", (event) => this.onSpotlightKey(event));

    $(".spotlight-overlay #spotlight-clear-button").on("click", (event) => {
      event.preventDefault();
      this.toggleOverlay();
    });
  }

  toggleOverlay() {
    // don't show the modal on the spotlight browser view
    if (document.URL.endsWith("spotlight")) return true;
    const modal = $("#spotlight");
    modal.draggable();
    if (modal.hasClass("show")) {
      modal.modal("hide");
    } else {
      modal.modal("show");
    }
  }

  onSpotlightKey(event) {
    const code = event.keyCode;
    if (![17, 32].includes(code)) {
      return;
    }
    this.map[code] = event.type === "keydown";
    // make hotkey configurable
    if (this.map[17] && this.map[32]) {
      this.toggleOverlay();
    }
  }
}

// Entry point
$(function () {
  console.debug("*** SENAITE.APP.SPOTLIGHT::DOMContentLoaded: --> Loading Spotlight Controller");
  const spotlight = new Spotlight();
  window.senaite = window.senaite || {};
  window.senaite.core = window.senaite.core || {};
  window.senaite.core.spotlight = spotlight;

  // trigger the spotlight modal instead of navigating to the view
  // Unfortunately, this is a CMFAction in senaite.core and we hav a proper CSS id/class here
  $("a.nav-link i.fa-search").closest("a").on("click", function (event) {
    event.preventDefault();
    console.debug("Spotlight trigger clicked");
    if (document.URL.endsWith("spotlight")) {
      $("#spotlight-search-field").focus();
    } else {
      spotlight.toggleOverlay();
    }
  });
});
