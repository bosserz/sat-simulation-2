export type HighlightTarget = "passage" | "question";

export type TextHighlight = {
  id: number;
  target: HighlightTarget;
  start_offset: number;
  end_offset: number;
  selected_text: string;
};

export type HighlightSelection = Omit<TextHighlight, "id">;

function textNodes(root: Node): Text[] {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes: Text[] = [];
  while (walker.nextNode()) nodes.push(walker.currentNode as Text);
  return nodes;
}

// Character offset of (node, nodeOffset) within the concatenated text of root.
function offsetWithin(root: Node, node: Node, nodeOffset: number): number {
  const range = document.createRange();
  range.selectNodeContents(root);
  range.setEnd(node, nodeOffset);
  return range.toString().length;
}

function locate(root: Node, offset: number): { node: Text; offset: number } | null {
  const nodes = textNodes(root);
  let remaining = offset;
  for (const node of nodes) {
    const len = node.nodeValue?.length || 0;
    if (remaining <= len) return { node, offset: remaining };
    remaining -= len;
  }
  return null;
}

export function readSelection(containers: Record<HighlightTarget, HTMLElement | null>): HighlightSelection | null {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) return null;
  const range = selection.getRangeAt(0);
  for (const target of ["passage", "question"] as const) {
    const container = containers[target];
    if (!container || !container.contains(range.startContainer) || !container.contains(range.endContainer)) continue;
    const start_offset = offsetWithin(container, range.startContainer, range.startOffset);
    const end_offset = offsetWithin(container, range.endContainer, range.endOffset);
    const selected_text = selection.toString().trim();
    if (end_offset <= start_offset || !selected_text) return null;
    return { target, start_offset, end_offset, selected_text };
  }
  return null;
}

export function applyHighlights(container: HTMLElement, highlights: TextHighlight[]) {
  // Apply from the end so earlier offsets are unaffected by inserted marks.
  const sorted = [...highlights].sort((a, b) => b.start_offset - a.start_offset);
  for (const highlight of sorted) {
    const start = locate(container, highlight.start_offset);
    const end = locate(container, highlight.end_offset);
    if (!start || !end) continue;
    const range = document.createRange();
    range.setStart(start.node, start.offset);
    range.setEnd(end.node, end.offset);
    const mark = document.createElement("mark");
    mark.className = "sat-highlight";
    mark.dataset.highlightId = String(highlight.id);
    mark.title = "Click to remove highlight";
    mark.appendChild(range.extractContents());
    range.insertNode(mark);
  }
}
