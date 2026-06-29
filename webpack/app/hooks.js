import { useCallback, useEffect, useMemo, useState } from "react";

import {
  formatHotkey,
  loadPref,
  parseHotkey,
  removePref,
  savePref,
} from "./utils";


// Resolve the trigger hotkey as a per-user override stored in localStorage,
// defaulting to the global hotkey from the control panel. Also exposes a
// "record" flow that captures the next key combo and persists it.
//
// :param globalHotkey: the configured default hotkey definition
// :returns: { hotkey (parsed), hotkeyStr, recording, overridden,
//             startRecording, reset }
export const usePersonalHotkey = (globalHotkey) => {
  const stored = loadPref("hotkey", null);
  const [hotkeyStr, setHotkeyStr] = useState(stored || globalHotkey);
  const [overridden, setOverridden] = useState(stored != null);
  const [recording, setRecording] = useState(false);

  const hotkey = useMemo(() => parseHotkey(hotkeyStr), [hotkeyStr]);

  // while recording, capture the next combo (capture phase, so it wins over
  // the search input); Escape cancels
  useEffect(() => {
    if (!recording) {
      return undefined;
    }
    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        setRecording(false);
        return;
      }
      const combo = formatHotkey(event);
      if (!combo) {
        return;
      }
      event.preventDefault();
      savePref("hotkey", combo);
      setHotkeyStr(combo);
      setOverridden(true);
      setRecording(false);
    };
    document.addEventListener("keydown", onKeyDown, true);
    return () => document.removeEventListener("keydown", onKeyDown, true);
  }, [recording]);

  const reset = useCallback(() => {
    removePref("hotkey");
    setHotkeyStr(globalHotkey);
    setOverridden(false);
  }, [globalHotkey]);

  return {
    hotkey,
    hotkeyStr,
    recording,
    overridden,
    startRecording: useCallback(() => setRecording(true), []),
    reset,
  };
};
