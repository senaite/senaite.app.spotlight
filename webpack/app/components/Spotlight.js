import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import ResultList from "./ResultList";
import ScopeBar from "./ScopeBar";
import SearchField from "./SearchField";
import { getCommands, search as searchAPI } from "../api";
import { usePersonalHotkey } from "../hooks";
import {
  _t,
  displayHotkey,
  filterCommands,
  loadPref,
  matchHotkey,
  narrowResults,
  parseQuery,
  resolveScope,
  savePref,
  sortResults,
} from "../utils";


const Spotlight = ({ config }) => {
  const catalogs = config.catalogs || [];
  const commandsConfig = config.commands || [];
  const highlight = config.highlight !== false;
  const minChars = config.min_chars || 2;
  const debounceMs = config.debounce || 200;

  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [scope, setScope] = useState(null);
  const [sortBy, setSortBy] = useState(loadPref("sortBy", "relevance"));
  const [dynamicCommands, setDynamicCommands] = useState([]);

  const inputRef = useRef(null);
  const activeRef = useRef(null);
  const requestToken = useRef(0);
  const debounceTimer = useRef(null);
  const dynamicLoaded = useRef(false);

  // trigger hotkey: per-user localStorage override, default to the global one
  const {
    hotkey, hotkeyStr, recording, overridden,
    startRecording, reset: resetHotkey,
  } = usePersonalHotkey(config.hotkey);
  // all query interpretation (term, prefix, state token, command/state modes)
  // lives in parseQuery
  const {
    term, prefix, state, commandMode, commandTerm, stateMode, statePartial,
  } = useMemo(() => parseQuery(query), [query]);
  const effectiveScope = resolveScope(catalogs, scope, prefix);

  // browse mode: an empty term while scoped to a single catalog lists its
  // first results (the catalog chips / "s:" prefix act as a browse affordance)
  const browsing =
    !commandMode && !stateMode && !term && Boolean(effectiveScope);

  // states to suggest: scoped to the active catalog, else the union of all
  const scopedStates = useMemo(() => {
    if (effectiveScope) {
      const cat = catalogs.find((c) => c.name === effectiveScope);
      return (cat && cat.states) || [];
    }
    const seen = {};
    const out = [];
    catalogs.forEach((c) =>
      (c.states || []).forEach((s) => {
        if (!seen[s.id]) {
          seen[s.id] = true;
          out.push(s);
        }
      })
    );
    return out;
  }, [catalogs, effectiveScope]);

  const suggestions = useMemo(() => {
    if (!stateMode) {
      return [];
    }
    const needle = statePartial.toLowerCase();
    if (!needle) {
      return scopedStates;
    }
    return scopedStates.filter(
      (s) =>
        s.id.toLowerCase().indexOf(needle) >= 0 ||
        (s.title || "").toLowerCase().indexOf(needle) >= 0
    );
  }, [stateMode, statePartial, scopedStates]);

  const commands = useMemo(() => {
    if (stateMode) {
      return [];
    }
    if (commandMode) {
      // the "/" palette also lists the lazily looked-up dynamic commands
      const all = commandsConfig.concat(dynamicCommands);
      return commandTerm ? filterCommands(all, commandTerm) : all;
    }
    // outside command mode, commands only show in the unscoped ("All") view
    return effectiveScope ? [] : filterCommands(commandsConfig, term);
  }, [commandsConfig, dynamicCommands, term, commandMode, commandTerm,
    stateMode, effectiveScope]);

  const sortedResults = useMemo(
    // no catalog results in command or state-suggestion mode
    () => (commandMode || stateMode
      ? []
      : sortResults(narrowResults(results, term), sortBy)),
    [results, term, sortBy, commandMode, stateMode]
  );
  // single flat, ordered model of all selectable rows; keyboard navigation
  // and ResultList rendering share this exact order (commands, results, then
  // state suggestions)
  const entries = useMemo(() => [].concat(
    commands.map((payload) => ({ type: "command", payload })),
    sortedResults.map((payload) => ({ type: "result", payload })),
    suggestions.map((payload) => ({ type: "state", payload })),
  ), [commands, sortedResults, suggestions]);
  const total = entries.length;

  // Deep link to the standalone search page, carrying the typed term and the
  // active catalog scope (the listing reads "<form_id>_filter" with the
  // search view form_id of "search")
  const advancedSearchUrl = useMemo(() => {
    const params = [];
    // keep the "is:<state>" token in the filter so the listing search box
    // re-applies the same workflow state filter
    const filterValue = state ? (term + " is:" + state).trim() : term;
    if (filterValue) {
      params.push("search_filter=" + encodeURIComponent(filterValue));
    }
    if (effectiveScope) {
      params.push("search_review_state=" + encodeURIComponent(effectiveScope));
    }
    const query = params.length ? "?" + params.join("&") : "";
    return (config.search_url || "") + query;
  }, [config.search_url, term, state, effectiveScope]);

  // Run the actual search request, ignoring stale responses
  const runSearch = useCallback(
    (searchTerm, catalog, reviewState) => {
      const token = ++requestToken.current;
      setLoading(true);
      setError(null);
      searchAPI(config.api_url, {
        q: searchTerm,
        catalog: catalog || "",
        state: reviewState || "",
        limit: config.max_results,
      })
        .then((data) => {
          if (token !== requestToken.current) {
            return;
          }
          setResults(data.items || []);
          setLoading(false);
        })
        .catch((err) => {
          if (token !== requestToken.current) {
            return;
          }
          setError(err.message);
          setResults([]);
          setLoading(false);
        });
    },
    [config.api_url, config.max_results]
  );

  // Debounced search whenever the term or the scope changes
  useEffect(() => {
    if (!open) {
      return undefined;
    }
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    // command/state-suggestion mode show their own lists, no catalog search.
    // browse mode (empty term while scoped) bypasses the min-chars gate.
    if (commandMode || stateMode || (!browsing && term.length < minChars)) {
      setResults([]);
      setLoading(false);
      return undefined;
    }
    debounceTimer.current = setTimeout(() => {
      runSearch(term, effectiveScope, state);
    }, debounceMs);
    return () => clearTimeout(debounceTimer.current);
  }, [term, effectiveScope, state, commandMode, stateMode, browsing, open,
    minChars, debounceMs, runSearch]);

  // Lazily fetch the dynamic commands the first time the command palette is
  // opened, so the (permission filtered) setup lookup only runs on demand
  useEffect(() => {
    if (!commandMode || dynamicLoaded.current || !config.commands_url) {
      return;
    }
    dynamicLoaded.current = true;
    getCommands(config.commands_url)
      .then((data) => setDynamicCommands(data.commands || []))
      .catch(() => {
        dynamicLoaded.current = false;
      });
  }, [commandMode, config.commands_url]);

  // Keep the active index within bounds when the entry set changes
  useEffect(() => {
    setActiveIndex((index) => {
      if (total === 0) {
        return 0;
      }
      return Math.min(index, total - 1);
    });
  }, [total]);

  // Scroll the active row into view when navigating with the keyboard
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ block: "nearest" });
    }
  }, [activeIndex]);

  const close = useCallback(() => {
    setOpen(false);
    setQuery("");
    setResults([]);
    setError(null);
    setScope(null);
    setActiveIndex(0);
  }, []);

  const openOverlay = useCallback(() => {
    setOpen(true);
    // focus on the next tick once the input is mounted
    window.setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 0);
  }, []);

  // Global hotkey listener to toggle the overlay
  useEffect(() => {
    const onKeyDown = (event) => {
      // suspended while the user is recording a new personal hotkey
      if (recording) {
        return;
      }
      if (matchHotkey(event, hotkey)) {
        event.preventDefault();
        setOpen((value) => {
          if (value) {
            return false;
          }
          window.setTimeout(() => {
            if (inputRef.current) {
              inputRef.current.focus();
            }
          }, 0);
          return true;
        });
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [hotkey, recording]);

  // Allow other parts of the UI to open the spotlight programmatically
  useEffect(() => {
    window.senaite = window.senaite || {};
    window.senaite.spotlight = { open: openOverlay, close };
    return () => {
      if (window.senaite) {
        delete window.senaite.spotlight;
      }
    };
  }, [openOverlay, close]);

  const navigateTo = useCallback((url) => {
    if (url) {
      window.location.href = url;
    }
  }, []);

  const selectEntry = useCallback(
    (entry) => {
      if (!entry) {
        return;
      }
      if (entry.type === "state") {
        // complete the trailing "is:<partial>" token with the chosen state
        const id = entry.payload.id;
        setQuery((q) => q.replace(/(^|\s)is:\S*$/i, "$1is:" + id + " "));
        if (inputRef.current) {
          inputRef.current.focus();
        }
        return;
      }
      if (entry.type === "command") {
        const url = (entry.payload.url || "").replace(
          "${portal_url}",
          config.portal_url || ""
        );
        navigateTo(url);
      } else {
        navigateTo(entry.payload.url);
      }
    },
    [config.portal_url, navigateTo]
  );

  const entryAt = useCallback(
    (index) => entries[index] || null,
    [entries]
  );

  const onSort = useCallback((value) => {
    setSortBy(value);
    savePref("sortBy", value);
  }, []);

  const onInputKeyDown = useCallback(
    (event) => {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIndex((index) => (total ? (index + 1) % total : 0));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex((index) => (total ? (index - 1 + total) % total : 0));
      } else if (event.key === "Enter") {
        event.preventDefault();
        selectEntry(entryAt(activeIndex));
      } else if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    },
    [total, activeIndex, selectEntry, entryAt, close]
  );

  if (!open) {
    return null;
  }

  return (
    <div
      className="spotlight-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          close();
        }
      }}
    >
      <div className="spotlight-panel" role="dialog" aria-modal="true">
        <SearchField
          value={query}
          inputRef={inputRef}
          onChange={setQuery}
          onKeyDown={onInputKeyDown}
          onClear={() => {
            setQuery("");
            if (inputRef.current) {
              inputRef.current.focus();
            }
          }}
        />
        <ScopeBar
          catalogs={catalogs}
          scope={scope}
          onScope={setScope}
          sortBy={sortBy}
          onSort={onSort}
        />
        <div className="spotlight-body">
          {error ? (
            <div className="spotlight-error text-danger">{error}</div>
          ) : null}
          {commandMode || stateMode || browsing
            || term.length >= minChars ? (
            <ResultList
              commands={commands}
              results={sortedResults}
              suggestions={suggestions}
              term={commandMode ? commandTerm : stateMode ? statePartial : term}
              highlight={highlight}
              activeIndex={activeIndex}
              activeRef={activeRef}
              onHover={setActiveIndex}
              onSelect={selectEntry}
            />
          ) : (
            <div className="spotlight-hint text-muted">
              <div className="spotlight-hint-title">
                {_t("Type to search across the system")}
              </div>
              <ul className="spotlight-hint-tips">
                <li>
                  <code>/</code> {_t("list commands")}
                </li>
                <li>
                  <code>s:water</code> {_t("scope to a catalog by prefix")}
                </li>
                <li>
                  <code>is:received</code> {_t("filter by workflow state")}
                </li>
              </ul>
            </div>
          )}
        </div>
        <div className="spotlight-footer text-muted">
          <span><kbd>↑</kbd><kbd>↓</kbd> {_t("to navigate")}</span>
          <span><kbd>↵</kbd> {_t("to open")}</span>
          <span><kbd>esc</kbd> {_t("to close")}</span>
          <div className="spotlight-footer-right">
            {loading ? (
              <span className="spotlight-loading">{_t("Searching ...")}</span>
            ) : null}
            <span className="spotlight-hotkey">
              <button
                type="button"
                className="spotlight-hotkey-set"
                onClick={startRecording}
                title={_t("Click to set your personal shortcut")}
              >
                <i className="fas fa-keyboard" />{" "}
                {recording ? _t("Press keys ...") : displayHotkey(hotkeyStr)}
              </button>
              {overridden && !recording ? (
                <button
                  type="button"
                  className="spotlight-hotkey-reset"
                  onClick={resetHotkey}
                  title={_t("Reset to the default shortcut")}
                >
                  <i className="fas fa-times" />
                </button>
              ) : null}
            </span>
            {config.search_url ? (
              <a
                className="spotlight-advanced"
                href={advancedSearchUrl}
                title={_t("Open the advanced search")}
              >
                <i className="fas fa-sliders-h" /> {_t("Advanced search")}
              </a>
            ) : null}
            {config.can_manage && config.settings_url ? (
              <a
                className="spotlight-settings"
                href={config.settings_url}
                title={_t("Spotlight settings")}
              >
                <i className="fas fa-cog" /> {_t("Settings")}
              </a>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Spotlight;
