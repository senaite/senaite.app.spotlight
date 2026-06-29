import React from "react";

import Highlight from "./Highlight";


// A single search result row
const ResultItem = ({
  item,
  term,
  highlight,
  active,
  rowRef,
  onSelect,
  onHover,
}) => {
  const className = active
    ? "spotlight-result spotlight-result--active"
    : "spotlight-result";

  return (
    <a
      ref={rowRef}
      href={item.url}
      className={className}
      onMouseEnter={onHover}
      onClick={(event) => {
        // let modifier clicks (new tab) behave natively
        if (event.metaKey || event.ctrlKey) {
          return;
        }
        event.preventDefault();
        onSelect();
      }}
    >
      <span className="spotlight-result-icon">
        {item.icon ? (
          // icon is server-generated (api.get_icon), trusted HTML, not user
          // input. Do not point this at any user-controlled source.
          <span dangerouslySetInnerHTML={{ __html: item.icon }} />
        ) : (
          <i className="far fa-file" />
        )}
      </span>
      <span className="spotlight-result-main">
        <span className="spotlight-result-title">
          <Highlight text={item.title_or_id} term={term} enabled={highlight} />
          {item.secondary_id ? (
            <span className="spotlight-result-code">{item.secondary_id}</span>
          ) : null}
        </span>
        {item.description ? (
          <span className="spotlight-result-description">
            <Highlight
              text={item.description}
              term={term}
              enabled={highlight}
            />
          </span>
        ) : null}
      </span>
      <span className="spotlight-result-meta">
        {item.parent_title ? (
          <span className="spotlight-result-location">
            {item.parent_title}
          </span>
        ) : null}
        {item.review_state ? (
          <span className="spotlight-result-state badge badge-light">
            {item.review_state}
          </span>
        ) : null}
      </span>
    </a>
  );
};

export default ResultItem;
