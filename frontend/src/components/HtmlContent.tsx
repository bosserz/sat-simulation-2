import { useEffect, useRef } from "react";
import { typesetMath } from "../lib/mathjax";

type HtmlContentProps = {
  html?: string | number | null;
  className?: string;
};

export function HtmlContent({ html, className = "" }: HtmlContentProps) {
  const ref = useRef<HTMLDivElement>(null);
  const content = html == null ? "" : String(html);

  useEffect(() => {
    typesetMath(ref.current);
  }, [content]);

  return <div ref={ref} className={className} dangerouslySetInnerHTML={{ __html: content }} />;
}
