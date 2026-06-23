import React from "react";

import CommandItem from "./CommandItem";
import ResultItem from "./ResultItem";
import StateItem from "./StateItem";
import { _t } from "../utils";


// Renders the command, result and state-suggestion sections. The active index
// is global across all sections so keyboard navigation is continuous:
// commands first, then results, then state suggestions.
const ResultList = ({
  commands,
  results,
  suggestions,
  term,
  highlight,
  activeIndex,
  activeRef,
  onHover,
  onSelect,
}) => {
  suggestions = suggestions || [];
  const hasCommands = commands.length > 0;
  const hasResults = results.length > 0;
  const hasSuggestions = suggestions.length > 0;

  if (!hasCommands && !hasResults && !hasSuggestions) {
    return (
      <div className="spotlight-empty text-muted">
        {_t("No results found")}
      </div>
    );
  }

  return (
    <div className="spotlight-results">
      {hasCommands ? (
        <div className="spotlight-section">
          <div className="spotlight-section-title">{_t("Commands")}</div>
          {commands.map((command, index) => (
            <CommandItem
              key={command.id}
              command={command}
              term={term}
              highlight={highlight}
              active={activeIndex === index}
              rowRef={activeIndex === index ? activeRef : null}
              onHover={() => onHover(index)}
              onSelect={() => onSelect({ type: "command", payload: command })}
            />
          ))}
        </div>
      ) : null}

      {hasResults ? (
        <div className="spotlight-section">
          <div className="spotlight-section-title">
            {_t("Results")} <span className="text-muted">({results.length})</span>
          </div>
          {results.map((item, index) => {
            const globalIndex = commands.length + index;
            return (
              <ResultItem
                key={item.uid || item.url || globalIndex}
                item={item}
                term={term}
                highlight={highlight}
                active={activeIndex === globalIndex}
                rowRef={activeIndex === globalIndex ? activeRef : null}
                onHover={() => onHover(globalIndex)}
                onSelect={() => onSelect({ type: "result", payload: item })}
              />
            );
          })}
        </div>
      ) : null}

      {hasSuggestions ? (
        <div className="spotlight-section">
          <div className="spotlight-section-title">{_t("States")}</div>
          {suggestions.map((state, index) => {
            const globalIndex = commands.length + results.length + index;
            return (
              <StateItem
                key={state.id}
                state={state}
                term={term}
                highlight={highlight}
                active={activeIndex === globalIndex}
                rowRef={activeIndex === globalIndex ? activeRef : null}
                onHover={() => onHover(globalIndex)}
                onSelect={() => onSelect({ type: "state", payload: state })}
              />
            );
          })}
        </div>
      ) : null}
    </div>
  );
};

export default ResultList;
