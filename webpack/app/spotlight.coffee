import { Model, View, Collection } from "backbone"
import { template, debounce, each } from "underscore"
import "./spotlight.scss"


###* DOCUMENT READY ENTRY POINT ###
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** SENAITE.APP.SPOTLIGHT::DOMContentLoaded: --> Loading Spotlight Controller"

  window.app ?= {}
  window.app.spotlight = new Spotlight()


class Spotlight
  constructor: ->
    @map = {}
    @document = $(document)
    @spotlight = $("#spotlight")
    @controller = new SpotlightController()

    # configure the overlay
    @overlay = @spotlight.overlay
      onLoad: (event) ->
        console.debug "***spotlight_overlay.onLoad***"
        el = $(event.target)
        $("#spotlight-search-field", el).focus()
        el.draggable()
      mask:
        color: 'black'
        opacity: '0.6'

    me = this

    @document.on "keydown keyup", (event) ->
      me.onSpotlightKey(event)

    # The spotlight button in the nav-bar
    $("#spotlight-trigger a").on "click", (event) ->
      console.debug "Spotlight trigger button clicked"
      event.preventDefault()
      if document.URL.endsWith "spotlight"
        $("#spotlight-search-field", me.spotlight).focus()
      else
        me.spotlightOverlay()

    $(".spotlight-overlay #spotlight-clear-button").on "click", (event) ->
      console.log "Clear button of the overlay clicked"
      event.preventDefault()
      me.spotlightOverlay()

  spotlightOverlay: ->
    if document.URL.endsWith "spotlight"
      console.debug "Spotlight overlay disabled on spotlight view"
      return yes
    # XXX: why?
    if not @overlay.isOpened?
      @overlay = @overlay.overlay()
    if @overlay.isOpened()
      @overlay.close()
    else
      @overlay.load()

  onSpotlightKey: (event) ->
    code = event.keyCode
    return unless code in [17, 32]
    @map[code] = event.type is 'keydown'
    if @map[17] and @map[32]
      console.debug "Ctrl-Space detected -> Trigger Spotlight"
      @spotlightOverlay()


### MODELS ###

# Single search result
class SearchResult extends Model
  defaults:
    id: ""
    title: ""
    url: ""
    icon: ""
    title_or_id: ""
    parent_title: ""
    parent_url: ""

# Collection of search results
class SearchResults extends Collection
  model: SearchResult


### VIEWS ###

# Renders a single search result
class ResultView extends View
  tagName: "tr"
  template: template $('#item-template').html()

  render: ->
    @$el.html @template @model.toJSON()
    return @


# Renders all search results
class ResultsView extends View
  tagName: "table"
  className: "table table-sm results-table"
  id: "search-results"

  template: template $('#results-template').html()

  initialize: ->
    # this is triggered when a new set of results is loaded into the collection.
    @collection.bind "results:changed", @render, @

  render: ->
    @$el.html @template @collection.toJSON()
    # @$el.attr "style", "width:100%"

    @collection.each (result, index) ->
      @addResult result, index
    , this

    return @

  addResult: (model, index) ->
    className = if index % 2 == 0 then "even" else "odd"
    view = new ResultView model: model, className: className
    @$el.append view.render().el


# The search view wraps all other views below and does not render itself
class SearchView extends View
  el: "#spotlight"

  initialize: ->
    # all results will be rendered by this view
    @resultsView ?= new ResultsView collection: @collection

  events:
    "keyup #spotlight-search-field": "onKeyup"
    "keypress #spotlight-search-field": "onKeyup"
    "click #spotlight-clear-button": "onClear"

  onClear: (event) =>
    event.preventDefault()
    @$("#spotlight-search-field").val("")
    @trigger "query:changed", ""

  onKeyup: (event) =>
    # special key handling
    code = event.keyCode or event.which
    if code in [13, 38, 40]
      event.preventDefault()
      event.stopPropagation()
      return @selectRow event
    value = @$("#spotlight-search-field").val()
    @trigger "query:changed", value

  selectRow: (event) ->
    code = event.keyCode
    table = $(".spotlight-overlay #search-results")
    results = $("tbody tr", table)

    # Nothing to select, because we have no results
    return unless results.length > 0

    # search for selected rows in the search results
    active = $("tr.selected", table)

    # Nothing selected so far, choose the first row
    if active.length == 0
      results.first().addClass "selected"
      return true

    # KEY UP
    if code == 38
      next = active.prev()

    # KEY DOWN
    else if code is 40
      next = active.next()

    # ENTER
    else if code is 13
      href = $("a.link", active).attr("href")
      console.log "Navigate to #{href}"
      location.href = href
      return true

    # deselect the current active row
    active.removeClass "selected"
    # select the next possible row
    next.addClass "selected"

    return true

  render: ->
    # render the results view table into the search-results-wrapper
    @$("#search-results-wrapper").html @resultsView.el


### CONTROLLERS ###

class SpotlightController extends View
  el: $("#spotlight")

  initialize: ->
    console.debug "SpotlightController initialized"

    # The holding collection for all search results
    @searchResults ?= new SearchResults()

    # Initialize a single search view and pass in the collection instance.
    # Backbone will take care that his will be accessbile as `this.collection`
    # on the view
    @searchView ?= new SearchView collection: @searchResults

    # render the main view
    @searchView.render()

    # debounce the search to avoid request flooding
    @lazySearch = debounce(@search, 500)

    # The view notifies us when the user entered something in the search field
    @searchView.bind "query:changed", @lazySearch, @

  get_csrf_token: () ->
    ###
     * Get the plone.protect CSRF token
     * Note: The fields won't save w/o that token set
    ###
    return document.querySelector("#protect-script").dataset.token

  get_portal_url: ->
    ###
     * Get the portal URL
    ###
    return document.body.dataset.portalUrl

  get_api_url: (endpoint) ->
    ###
     * Build API URL for the given endpoint
     * @param {string} endpoint
     * @returns {string}
    ###
    url = @get_portal_url()
    api_endpoint = "@@API/spotlight"
    params = location.search
    return "#{url}/#{api_endpoint}/#{endpoint}#{params}"

  get_json: (url, options) ->
    ###
     * Fetch Ajax API resource from the server
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
    ###
    options ?= {}

    method = options.method or "POST"
    data = JSON.stringify(options.data) or "{}"

    init =
      method: method
      headers:
        "Content-Type": "application/json"
        "X-CSRF-TOKEN": @get_csrf_token()
      body: if method is "POST" then data else null
      credentials: "include"

    request = new Request(url, init)
    return fetch(request).then (response) ->
      if response.status isnt 200
        return response.json().then (json) ->
          throw new Error(json.error or "Unknown Error")
      else
        return response.json()

  # Executest the search and adds the results to the collection
  search: (query) ->
    # reset the collection
    @searchResults.reset()

    # URL to query
    url = @get_api_url "search"
    console.log url

    # prepare  the query
    options =
      data:
        q: query
        limit: 5

    me = this

    # execute the search
    promise = @get_json(url, options)

    promise.then (data) ->

      each data.items, (result, index) ->
        searchResult = new SearchResult(result)
        # add the new search result to the collection
        me.searchResults.add searchResult

      # trigger finished event
      me.searchResults.trigger "results:changed"
