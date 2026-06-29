import React from "react";

import { _t } from "../utils";


// Narrowing bar: catalog scope chips on the left, sort selector on the right
const ScopeBar = ({ catalogs, scope, onScope, sortBy, onSort }) => {
  const renderChip = (key, label) => {
    const active = scope === key;
    const className = active
      ? "btn btn-sm btn-primary spotlight-chip"
      : "btn btn-sm btn-outline-secondary spotlight-chip";
    return (
      <button
        key={key || "all"}
        type="button"
        className={className}
        onClick={() => onScope(key)}
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
          renderChip(catalog.name, catalog.label || catalog.name)
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
