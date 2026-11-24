import React from 'react';
import katex from 'katex';

export default function MathRenderer({ text, className = '' }) {
  if (!text) return null;

  // Split by $$ ... $$ (display) first, then $ ... $ (inline)
  const renderMathContent = (raw) => {
    // Regular expression matching $$...$$ or $...$
    const regex = /(\$\$[\s\S]+?\$\$|\$[^\$]+?\$)/g;
    const parts = raw.split(regex);

    return parts.map((part, idx) => {
      if (part.startsWith('$$') && part.endsWith('$$')) {
        const math = part.slice(2, -2).trim();
        try {
          const html = katex.renderToString(math, {
            displayMode: true,
            throwOnError: false,
            output: 'html'
          });
          return <span key={idx} dangerouslySetInnerHTML={{ __html: html }} className="block my-2" />;
        } catch (e) {
          return <span key={idx} className="text-red-500">{part}</span>;
        }
      } else if (part.startsWith('$') && part.endsWith('$')) {
        const math = part.slice(1, -1).trim();
        try {
          const html = katex.renderToString(math, {
            displayMode: false,
            throwOnError: false,
            output: 'html'
          });
          return <span key={idx} dangerouslySetInnerHTML={{ __html: html }} />;
        } catch (e) {
          return <span key={idx} className="text-red-500">{part}</span>;
        }
      }
      return <span key={idx}>{part}</span>;
    });
  };

  return <span className={className}>{renderMathContent(text)}</span>;
}
