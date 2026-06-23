import React from "react";

import Highlight from "./Highlight";


// A single workflow-state autocomplete suggestion row
const StateItem = ({ state, term, highlight, active, rowRef, onSelect,
  onHover }) => {
  const className = active
    ? "spotlight-state spotlight-state--active"
    : "spotlight-state";

  return (
    <a
      ref={rowRef}
      href="#"
      className={className}
      onMouseEnter={onHover}
      onClick={(event) => {
        event.preventDefault();
        onSelect();
      }}
    >
      <span className="spotlight-state-icon">
        <i className="fas fa-filter" />
      </span>
      <span className="spotlight-state-title">
        <Highlight text={state.title} term={term} enabled={highlight} />
      </span>
      <span className="spotlight-state-id text-muted">{state.id}</span>
    </a>
  );
};

export default StateItem;
