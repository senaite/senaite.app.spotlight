import React from "react";

import Highlight from "./Highlight";


// A single command palette action row
const CommandItem = ({
  command,
  term,
  highlight,
  active,
  rowRef,
  onSelect,
  onHover,
}) => {
  const className = active
    ? "spotlight-command spotlight-command--active"
    : "spotlight-command";

  return (
    <a
      ref={rowRef}
      href={command.url || "#"}
      className={className}
      onMouseEnter={onHover}
      onClick={(event) => {
        event.preventDefault();
        onSelect();
      }}
    >
      <span className="spotlight-command-icon">
        <i className={command.icon || "fas fa-terminal"} />
      </span>
      <span className="spotlight-command-title">
        <Highlight text={command.title} term={term} enabled={highlight} />
      </span>
      <span className="spotlight-command-badge badge badge-info">
        {"⌘"}
      </span>
    </a>
  );
};

export default CommandItem;
