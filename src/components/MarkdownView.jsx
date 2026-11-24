import React from 'react';
import MathRenderer from './MathRenderer';

export default function MarkdownView({ content }) {
  if (!content) return null;

  // Check if content contains markdown table
  const lines = content.split('\n');
  const blocks = [];
  let currentTable = [];
  let inTable = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|') && line.endsWith('|')) {
      inTable = true;
      currentTable.push(line);
    } else {
      if (inTable) {
        blocks.push({ type: 'table', rows: currentTable });
        currentTable = [];
        inTable = false;
      }
      if (line.length > 0) {
        blocks.push({ type: 'text', text: lines[i] });
      }
    }
  }

  if (inTable && currentTable.length > 0) {
    blocks.push({ type: 'table', rows: currentTable });
  }

  return (
    <div className="space-y-2 text-slate-800 text-sm leading-relaxed">
      {blocks.map((block, bIdx) => {
        if (block.type === 'table') {
          // Parse markdown table rows
          const parsedRows = block.rows
            .filter(r => !r.includes(':---') && !r.includes('---'))
            .map(r => r.split('|').slice(1, -1).map(c => c.trim()));

          if (parsedRows.length === 0) return null;
          const [headers, ...dataRows] = parsedRows;

          return (
            <div key={bIdx} className="markdown-table-wrapper">
              <table className="markdown-table">
                <thead>
                  <tr>
                    {headers.map((h, hIdx) => (
                      <th key={hIdx}>
                        <MathRenderer text={h} />
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataRows.map((row, rIdx) => (
                    <tr key={rIdx}>
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="font-mono text-xs">
                          <MathRenderer text={cell} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        // Check if list item or bold header
        const text = block.text;
        const diagram = text.match(/^!\[([^\]]+)\]\((\/images\/logan_p4_\d+_shear_moment\.svg)\)$/);
        if (diagram) {
          return <img key={bIdx} src={diagram[2]} alt={diagram[1]} className="w-full max-w-3xl" loading="lazy" />;
        }
        if (text.startsWith('- ')) {
          return (
            <div key={bIdx} className="flex items-start gap-2 pl-2">
              <span className="text-sky-500 font-bold">•</span>
              <div className="flex-1">
                <MathRenderer text={text.slice(2)} />
              </div>
            </div>
          );
        }

        if (text.startsWith('**') && text.endsWith('**')) {
          return (
            <div key={bIdx} className="font-semibold text-slate-900 mt-2">
              <MathRenderer text={text.slice(2, -2)} />
            </div>
          );
        }

        return (
          <div key={bIdx}>
            <MathRenderer text={text} />
          </div>
        );
      })}
    </div>
  );
}
