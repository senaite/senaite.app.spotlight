import React from "react";

import { _t } from "../utils";


// Narrowing bar: catalog scope chips on the left, sort selector on the right.
// `scope` is the list of selected catalog names (empty means "All"); Ctrl or
// Meta click toggles a catalog without clearing the others.
const ScopeBar = ({ catalogs, scope, onScope, sortBy, onSort }) => {
  const selected = scope || [];
  const renderChip = (key, label) => {
    const active = key === null ? selected.length === 0
      : selected.indexOf(key) >= 0;
    const className = active
      ? "btn btn-sm btn-primary spotlight-chip"
      : "btn btn-sm btn-outline-secondary spotlight-chip";
    return (
      <button
        key={key || "all"}
        type="button"
        className={className}
        onClick={(event) => onScope(key, event.ctrlKey || event.metaKey)}
        onContextMenu={(event) => {
          // macOS turns Ctrl+click into a context-menu event, so honor it
          // here as an additive toggle for the STRG+click multi-select
          if (event.ctrlKey) {
            event.preventDefault();
            onScope(key, true);
          }
        }}
      >
        {label}
      </button>
    );
  };

  return (
    <div className="spotlight-scopebar">
      <div className="spotlight-chips">
        {renderChip(null, _t("All"))}
        {catalogs.map((catalog) =>
          renderChip(catalog.name, _t(catalog.label || catalog.name))
        )}
      </div>
      <div className="spotlight-sort">
        <label className="spotlight-sort-label">{_t("Sort")}</label>
        <select
          className="custom-select custom-select-sm"
          value={sortBy}
          onChange={(event) => onSort(event.target.value)}
        >
          <option value="relevance">{_t("Relevance")}</option>
          <option value="title">{_t("Title")}</option>
          <option value="type">{_t("Type")}</option>
        </select>
      </div>
    </div>
  );
};

export default ScopeBar;
