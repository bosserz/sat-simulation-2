import { useEffect, useRef, useState } from "react";
import { formatDuration } from "../lib/format";

type TimerProps = {
  seconds?: number;
  onElapsed?: () => void;
};

export function Timer({ seconds = 0, onElapsed }: TimerProps) {
  const [left, setLeft] = useState(seconds);
  const onElapsedRef = useRef(onElapsed);
  onElapsedRef.current = onElapsed;

  useEffect(() => {
    // Count down against a wall-clock deadline so throttled/background tabs don't drift,
    // and fire immediately if time is already up when the timer mounts.
    const deadline = Date.now() + seconds * 1000;
    let fired = false;
    const tick = () => {
      const remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
      setLeft(remaining);
      if (remaining <= 0 && !fired) {
        fired = true;
        window.clearInterval(id);
        onElapsedRef.current?.();
      }
    };
    const id = window.setInterval(tick, 1000);
    tick();
    document.addEventListener("visibilitychange", tick);
    return () => {
      window.clearInterval(id);
      document.removeEventListener("visibilitychange", tick);
    };
  }, [seconds]);

  return <span className={left <= 60 ? "font-bold text-red-600" : "font-bold text-ink"}>{formatDuration(left)}</span>;
}
