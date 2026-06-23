/* SENAITE.APP.SPOTLIGHT helper utilities */


// Map of modifier names to their KeyboardEvent property
const MODIFIERS = {
  control: "ctrlKey",
  ctrl: "ctrlKey",
  meta: "metaKey",
  cmd: "metaKey",
  command: "metaKey",
  shift: "shiftKey",
  alt: "altKey",
  option: "altKey",
};


// Parse a hotkey definition like "Control+Space" or "Meta+k" into a
// descriptor: {modifiers: ["ctrlKey"], key: "space"}
export const parseHotkey = (definition) => {
  const parts = (definition || "")
    .split("+")
    .map((part) => part.trim().toLowerCase())
    .filter(Boolean);
  const modifiers = [];
  let key = "";
  parts.forEach((part) => {
    if (MODIFIERS[part]) {
      modifiers.push(MODIFIERS[part]);
    } else {
      key = part;
    }
  });
  return { modifiers, key };
};


// Normalize a KeyboardEvent key to a lowercase token comparable to a hotkey
const eventKey = (event) => {
  if (event.code === "Space" || event.key === " ") {
    return "space";
  }
  return (event.key || "").toLowerCase();
};


// Check whether a KeyboardEvent matches a parsed hotkey descriptor
export const matchHotkey = (event, hotkey) => {
  if (!hotkey || !hotkey.key) {
    return false;
  }
  if (eventKey(event) !== hotkey.key) {
    return false;
  }
  const all = ["ctrlKey", "metaKey", "shiftKey", "altKey"];
  return all.every((modifier) => {
    const required = hotkey.modifiers.includes(modifier);
    return Boolean(event[modifier]) === required;
  });
};


// Build a hotkey definition (e.g. "Control+Space") from a KeyboardEvent.
// Returns null for an incomplete combo: a modifier key alone, or a key
// pressed without any modifier (which would trigger constantly).
const MODIFIER_KEY_NAMES = ["Control", "Meta", "Shift", "Alt"];

export const formatHotkey = (event) => {
  let key = event.key;
  if (event.code === "Space" || key === " ") {
    key = "Space";
  }
  if (MODIFIER_KEY_NAMES.indexOf(key) >= 0) {
    return null;
  }
  const mods = [];
  if (event.ctrlKey) mods.push("Control");
  if (event.metaKey) mods.push("Meta");
  if (event.shiftKey) mods.push("Shift");
  if (event.altKey) mods.push("Alt");
  if (!mods.length) {
    return null;
  }
  if (key.length === 1) {
    key = key.toUpperCase();
  }
  return mods.concat(key).join("+");
};


// Render a hotkey definition with the usual modifier symbols, e.g.
// "Control+Space" -> "⌃Space", "Meta+K" -> "⌘K"
const HOTKEY_SYMBOLS = {
  control: "⌃", ctrl: "⌃", meta: "⌘", cmd: "⌘", command: "⌘",
  shift: "⇧", alt: "⌥", option: "⌥",
};

export const displayHotkey = (definition) => {
  return (definition || "")
    .split("+")
    .map((part) => HOTKEY_SYMBOLS[part.trim().toLowerCase()] || part.trim())
    .join("");
};


// Escape a string for safe use inside a regular expression
export const escapeRegExp = (value) => {
  return (value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
};


// Split a query into {term, prefix}. A prefix is a short alphanumeric token
// followed by a colon, e.g. "s:water" -> {term: "water", prefix: "s"}.
export const splitPrefix = (query) => {
  const value = (query || "").trim();
  const index = value.indexOf(":");
  if (index < 0) {
    return { term: value, prefix: null };
  }
  const prefix = value.slice(0, index).trim();
  const term = value.slice(index + 1).trim();
  if (/^[a-z0-9]{1,3}$/i.test(prefix)) {
    return { term, prefix };
  }
  return { term: value, prefix: null };
};


// Split a query into {term, state}. A state filter is an "is:<state>" token
// anywhere in the query, e.g. "CA20 is:received" -> {term: "CA20",
// state: "received"}.
export const splitState = (query) => {
  const value = (query || "").trim();
  const re = /(^|\s)is:(\S+)/i;
  const match = value.match(re);
  if (!match) {
    return { term: value, state: null };
  }
  const state = match[2];
  const term = value.replace(re, " ").replace(/\s+/g, " ").trim();
  return { term, state };
};


// Parse the raw query into its modes and tokens. Centralizes all query
// interpretation so the component does not have to:
//   - command mode: query starts with "/", optional "/add" filter text
//   - state autocomplete: a trailing "is:<partial>" token
//   - state filter + catalog prefix tokens are stripped from the term
export const parseQuery = (query) => {
  const raw = query || "";
  const commandMode = raw.trimStart().startsWith("/");
  const commandTerm = commandMode ? raw.trim().slice(1).trim() : "";
  // strip the state token first so "is:" is not read as a catalog prefix,
  // then strip the catalog prefix
  const afterState = splitState(raw);
  const { term, prefix } = splitPrefix(afterState.term);
  // a trailing "is:<partial>" (only outside command mode) triggers the
  // workflow-state autocomplete
  const stateMatch = commandMode ? null : raw.match(/(^|\s)is:(\S*)$/i);
  return {
    term,
    prefix,
    state: afterState.state,
    commandMode,
    commandTerm,
    stateMode: Boolean(stateMatch),
    statePartial: stateMatch ? stateMatch[2] : "",
  };
};


// Filter the configured commands by title and keywords
export const filterCommands = (commands, term) => {
  if (!term) {
    return [];
  }
  const needle = term.toLowerCase();
  return commands.filter((command) => {
    const haystack = [command.title]
      .concat(command.keywords || [])
      .join(" ")
      .toLowerCase();
    return haystack.indexOf(needle) >= 0;
  });
};


// Reduce a string to its lowercased alphanumeric characters
const normalizeAlnum = (value) =>
  (value || "").toLowerCase().replace(/[^a-z0-9]+/g, "");


// Narrow the (broad) server results to those that actually contain the typed
// term. The server neutralizes separators like "-" (so "CA-01-0" matches
// "CA-02-01"); this restores precise matching for single token / barcode like
// queries. Multi word queries are left untouched to keep fuzzy search.
export const narrowResults = (results, term) => {
  if (!term || /\s/.test(term)) {
    return results;
  }
  const needle = normalizeAlnum(term);
  if (!needle) {
    return results;
  }
  return results.filter((item) => {
    const haystack = normalizeAlnum(
      [item.title_or_id, item.title, item.description, item.id,
        item.parent_title].filter(Boolean).join(" ")
    );
    return haystack.indexOf(needle) >= 0;
  });
};


// Apply the client side sorting to the result set
export const sortResults = (results, sortBy) => {
  if (sortBy === "relevance") {
    return results;
  }
  const key = sortBy === "type" ? "portal_type" : "title_or_id";
  return results
    .slice()
    .sort((a, b) => (a[key] || "").localeCompare(b[key] || ""));
};


// Resolve the catalog to scope the search to: the manual scope first, then
// the prefix token typed into the search field
export const resolveScope = (catalogs, scope, prefix) => {
  if (scope) {
    return scope;
  }
  if (prefix) {
    const match = catalogs.find((catalog) => catalog.prefix === prefix);
    if (match) {
      return match.name;
    }
  }
  return null;
};


// Translate a message using the global SENAITE message factory if available
export const _t = (msgid) => {
  if (typeof window._t === "function") {
    return window._t(msgid);
  }
  return msgid;
};


// localStorage backed key/value helpers, namespaced to the spotlight
const STORAGE_PREFIX = "senaite.spotlight.";

export const loadPref = (key, fallback) => {
  try {
    const raw = window.localStorage.getItem(STORAGE_PREFIX + key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch (error) {
    return fallback;
  }
};

export const savePref = (key, value) => {
  try {
    window.localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value));
  } catch (error) {
    /* ignore quota / private mode errors */
  }
};

export const removePref = (key) => {
  try {
    window.localStorage.removeItem(STORAGE_PREFIX + key);
  } catch (error) {
    /* ignore private mode errors */
  }
};
