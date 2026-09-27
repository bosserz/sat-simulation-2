import { forwardRef, useEffect, useImperativeHandle, useRef, type MouseEvent } from "react";
import { applyHighlights, type TextHighlight } from "../lib/highlights";
import { typesetMath } from "../lib/mathjax";

type HtmlContentProps = {
  html?: string | number | null;
  className?: string;
  highlights?: TextHighlight[];
  onHighlightClick?: (id: number) => void;
};

export const HtmlContent = forwardRef<HTMLDivElement, HtmlContentProps>(function HtmlContent(
  { html, className = "", highlights, onHighlightClick },
  forwardedRef
) {
  const ref = useRef<HTMLDivElement>(null);
  const content = html == null ? "" : String(html);
  useImperativeHandle(forwardedRef, () => ref.current as HTMLDivElement);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (highlights) {
      // Reset to the original markup before re-applying marks so offsets stay stable.
      el.innerHTML = content;
      applyHighlights(el, highlights);
    }
    typesetMath(el);
  }, [content, highlights]);

  function handleClick(event: MouseEvent<HTMLDivElement>) {
    if (!onHighlightClick) return;
    const mark = (event.target as HTMLElement).closest<HTMLElement>("mark.sat-highlight");
    if (mark?.dataset.highlightId) onHighlightClick(Number(mark.dataset.highlightId));
  }

  return <div ref={ref} className={className} onClick={handleClick} dangerouslySetInnerHTML={{ __html: content }} />;
});
