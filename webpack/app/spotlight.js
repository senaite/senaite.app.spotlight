import React from "react";
import { createRoot } from "react-dom/client";

import Spotlight from "./components/Spotlight";
import "./spotlight.scss";


// Parse the JSON configuration rendered into the mount node
const parseConfig = (el) => {
  try {
    return JSON.parse(el.dataset.config || "{}");
  } catch (error) {
    console.error("Invalid spotlight configuration", error);
    return {};
  }
};


// Mount the spotlight React app into the configured container
const mount = () => {
  const el = document.getElementById("spotlight-root");
  if (!el) {
    return;
  }
  const config = parseConfig(el);
  const root = createRoot(el);
  root.render(<Spotlight config={config} />);

  // Open the overlay when the navbar search action is clicked. The action is
  // a CMFAction in senaite.core, so we hook it by its icon here.
  const trigger = document.querySelector("a.nav-link i.fa-search");
  if (trigger) {
    trigger.closest("a").addEventListener("click", (event) => {
      event.preventDefault();
      if (window.senaite && window.senaite.spotlight) {
        window.senaite.spotlight.open();
      }
    });
  }
};


document.addEventListener("DOMContentLoaded", mount);
