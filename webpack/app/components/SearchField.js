import React from "react";

import { _t } from "../utils";


// The search input row with a leading icon and a clear button
const SearchField = ({ value, inputRef, onChange, onKeyDown, onClear }) => {
  return (
    <div className="spotlight-search-field">
      <i className="fas fa-search spotlight-search-icon" />
      <input
        ref={inputRef}
        type="text"
        className="form-control form-control-lg"
        autoComplete="off"
        spellCheck="false"
        autoFocus
        placeholder={_t("Type to search ...")}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={onKeyDown}
      />
      {value ? (
        <button
          type="button"
          className="btn btn-link spotlight-clear-button"
          onClick={onClear}
          tabIndex={-1}
        >
          <i className="fas fa-times" />
        </button>
      ) : null}
    </div>
  );
};

export default SearchField;
