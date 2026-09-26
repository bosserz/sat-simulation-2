declare global {
  interface Window {
    MathJax?: {
      typesetPromise?: (elements?: Element[]) => Promise<void>;
    };
  }
}

export function typesetMath(root?: Element | null) {
  if (!root || !window.MathJax?.typesetPromise) return;
  window.MathJax.typesetPromise([root]).catch(() => undefined);
}
