import { useEffect, useState } from "react";
import { formatDuration } from "../lib/format";

type TimerProps = {
  seconds?: number;
  onElapsed?: () => void;
};

export function Timer({ seconds = 0, onElapsed }: TimerProps) {
  const [left, setLeft] = useState(seconds);

  useEffect(() => {
    setLeft(seconds);
  }, [seconds]);

  useEffect(() => {
    if (left <= 0) return;
    const id = window.setInterval(() => {
      setLeft((value) => {
        if (value <= 1) {
          window.clearInterval(id);
          onElapsed?.();
          return 0;
        }
        return value - 1;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, [left, onElapsed]);

  return <span className={left <= 60 ? "font-bold text-red-600" : "font-bold text-ink"}>{formatDuration(left)}</span>;
}
