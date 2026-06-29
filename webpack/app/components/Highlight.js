import React from "react";

import { escapeRegExp } from "../utils";


// Render `text` with every occurrence of `term` wrapped in <mark>
const Highlight = ({ text, term, enabled }) => {
  const value = text || "";
  if (!enabled || !term) {
    return <span>{value}</span>;
  }
  const pattern = new RegExp("(" + escapeRegExp(term) + ")", "ig");
  // splitting on a capturing group keeps the matches at the odd indices
  const parts = value.split(pattern);
  return (
    <span>
      {parts.map((part, index) =>
        index % 2 === 1 ? (
          <mark key={index} className="spotlight-highlight">
            {part}
          </mark>
        ) : (
          <span key={index}>{part}</span>
        )
      )}
    </span>
  );
};

export default Highlight;
