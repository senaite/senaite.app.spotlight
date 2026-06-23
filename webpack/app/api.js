/* SENAITE.APP.SPOTLIGHT search API client */


// Read the plone.protect CSRF token rendered into the page
const getCSRFToken = () => {
  const el = document.querySelector("#protect-script");
  return (el && el.dataset.token) || "";
};


// POST helper that sends/receives JSON and includes the CSRF token
const postJSON = (url, data) => {
  const init = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-TOKEN": getCSRFToken(),
    },
    body: JSON.stringify(data || {}),
    credentials: "include",
  };
  return fetch(new Request(url, init)).then((response) => {
    if (!response.ok) {
      return response.json().then((json) => {
        throw new Error(json.error || "Spotlight search failed");
      });
    }
    return response.json();
  });
};


// Run a spotlight search against the JSON API search route
//
// :param apiUrl: fully qualified search endpoint
// :param params: {q, limit, catalog, state} query parameters
export const search = (apiUrl, params) => {
  return postJSON(apiUrl, params);
};


// Fetch the dynamic (lazily looked-up) command palette actions
export const getCommands = (url) => {
  return postJSON(url, {});
};
