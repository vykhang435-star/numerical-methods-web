import React, { useState } from 'react';
import MathRenderer from './MathRenderer';
import MarkdownView from './MarkdownView';
import { Lightbulb, CheckCircle2, Flame, Eye, EyeOff, Send, RotateCcw, AlertTriangle, XCircle, Trophy } from 'lucide-react';

export const resolveImagePath = (src) => {
  if (!src) return '';
  if (src.startsWith('http://') || src.startsWith('https://')) return src;
  const base = import.meta.env.BASE_URL || '/';
  const cleanBase = base.endsWith('/') ? base : `${base}/`;
  const cleanSrc = src.startsWith('/') ? src.slice(1) : src;
  return `${cleanBase}${cleanSrc}`;
};

export default function ExerciseCard({ problem, index }) {
  // Layer states
  const [showHint, setShowHint] = useState(false);
  const [activeStep, setActiveStep] = useState(0); // 0: none, 1: step 1, 2: step 2, 3: step 3
  const [activeTooltip, setActiveTooltip] = useState(null);

  // Student Practice Input State
  const [userAnswer, setUserAnswer] = useState('');
  const [evalResult, setEvalResult] = useState(null); // null | { status: 'correct' | 'close' | 'wrong', diffPercent: number, userVal: number }

  const {
    id,
    source_problem,
    method_tag,
    exam_focus,
    problem_en,
    glossary = {},
    hint,
    steps = [],
    final_answer,
    expected_numeric_value,
    numeric_target_label,
    figure_image
  } = problem;
  const isDirectFEM = ['Beam Element', '1D Bar Element', '2D Plane Truss Element'].includes(method_tag);

  // Render problem_en with glossary highlights
  const renderGlossaryProblem = () => {
    if (!glossary || Object.keys(glossary).length === 0) {
      return <MathRenderer text={problem_en} />;
    }

    const terms = Object.keys(glossary).sort((a, b) => b.length - a.length);
    const escapedTerms = terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const termRegex = new RegExp(`\\b(${escapedTerms.join('|')})\\b`, 'gi');

    // Split text into tokens by display math ($$...$$), inline math ($...$) and plain text
    const mathTokens = problem_en.split(/(\$\$[\s\S]+?\$\$|\$[^\$]+?\$)/g);

    return mathTokens.map((segment, sIdx) => {
      if ((segment.startsWith('$$') && segment.endsWith('$$')) || (segment.startsWith('$') && segment.endsWith('$'))) {
        return <MathRenderer key={sIdx} text={segment} />;
      }

      // In plain text, highlight glossary words
      const words = segment.split(termRegex);
      return words.map((word, wIdx) => {
        const lower = word.toLowerCase();
        const matchedKey = terms.find(t => t.toLowerCase() === lower);

        if (matchedKey) {
          const translation = glossary[matchedKey];
          const isCurrent = activeTooltip === `${sIdx}-${wIdx}`;

          return (
            <span
              key={wIdx}
              className="relative inline-block border-b-2 border-dashed border-sky-400 text-sky-800 bg-sky-50 px-1 rounded cursor-pointer hover:bg-sky-100 transition-colors"
              onClick={() => setActiveTooltip(isCurrent ? null : `${sIdx}-${wIdx}`)}
              onMouseEnter={() => setActiveTooltip(`${sIdx}-${wIdx}`)}
              onMouseLeave={() => setActiveTooltip(null)}
              title={`${matchedKey}: ${translation}`}
            >
              {word}
              {isCurrent && (
                <span className="absolute z-30 bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2.5 py-1 text-xs font-medium text-white bg-slate-900 rounded-md shadow-lg whitespace-nowrap pointer-events-none animate-fadeIn">
                  💡 {translation}
                  <span className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900" />
                </span>
              )}
            </span>
          );
        }
        return <span key={wIdx}>{word}</span>;
      });
    });
  };

  // Evaluate student answer
  const handleCheckAnswer = (e) => {
    if (e) e.preventDefault();
    if (!userAnswer.trim()) return;

    // Clean user input: replace commas with dots, remove spaces
    const cleanStr = userAnswer.replace(/,/g, '.').trim();
    const isDecimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(cleanStr);
    const userNum = numeric_target_label
      ? (isDecimal ? Number(cleanStr) : NaN)
      : parseFloat(cleanStr.replace(/[^\d.-]/g, ''));

    if (!Number.isFinite(userNum)) {
      setEvalResult({ status: 'invalid', message: 'Vui lòng nhập một số hợp lệ (ví dụ: 5.625).' });
      return;
    }

    // Determine target value: either expected_numeric_value or extracted from final_answer
    let target = expected_numeric_value;
    if (target === undefined || target === null) {
      const match = final_answer ? final_answer.match(/[-+]?\d*\.?\d+/) : null;
      target = match ? parseFloat(match[0]) : null;
    }

    if (target === null || isNaN(target)) {
      setEvalResult({ status: 'unknown', message: 'Đã lưu đáp số. Hãy mở Bước 3 để đối chiếu.' });
      return;
    }

    const diffAbs = Math.abs(userNum - target);
    const denom = Math.abs(target) > 1e-6 ? Math.abs(target) : 1.0;
    const diffPercent = (diffAbs / denom) * 100.0;

    if (diffPercent <= 1.0 || (!numeric_target_label && diffAbs <= 0.02)) {
      setEvalResult({
        status: 'correct',
        userVal: userNum,
        targetVal: target,
        diffPercent: diffPercent.toFixed(2)
      });
    } else if (diffPercent <= 5.0 || (!numeric_target_label && diffAbs <= 0.1)) {
      setEvalResult({
        status: 'close',
        userVal: userNum,
        targetVal: target,
        diffPercent: diffPercent.toFixed(2)
      });
    } else {
      setEvalResult({
        status: 'wrong',
        userVal: userNum,
        targetVal: target,
        diffPercent: diffPercent.toFixed(2)
      });
    }
  };

  const handleResetAnswer = () => {
    setUserAnswer('');
    setEvalResult(null);
  };

  const toggleAll = () => {
    if (activeStep === 3) {
      setActiveStep(0);
      setShowHint(false);
    } else {
      setActiveStep(3);
      setShowHint(true);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 bg-slate-50/70 border-b border-slate-100 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2.5 flex-wrap">
          <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-200 text-slate-700">
            #{index + 1}
          </span>
          <span className="text-xs font-medium text-slate-500 font-mono">
            {source_problem}
          </span>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-sky-100 text-sky-800 border border-sky-200">
            {method_tag}
          </span>
          {exam_focus && (
            <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
              <Flame size={12} className="text-amber-600 fill-amber-500" />
              Trọng tâm thi ME2091
            </span>
          )}
        </div>

        <button
          onClick={toggleAll}
          className="text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center gap-1 py-1 px-2 rounded hover:bg-slate-200/50 transition-colors"
        >
          {activeStep === 3 ? (
            <>
              <EyeOff size={14} /> Thu gọn lời giải
            </>
          ) : (
            <>
              <Eye size={14} /> Mở toàn bộ đáp án
            </>
          )}
        </button>
      </div>

      {/* Problem Content */}
      <div className="p-5 space-y-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1">
            Đề bài gốc (English)
            <span className="text-[11px] font-normal normal-case text-slate-400">
              (chạm từ gạch chân để xem nghĩa kỹ thuật)
            </span>
          </div>
          <div className="text-base text-slate-800 leading-relaxed font-normal bg-slate-50/50 p-3.5 rounded-lg border border-slate-100">
            {renderGlossaryProblem()}
          </div>
        </div>

        {/* Problem Figure / Diagram if available */}
        {figure_image && (
          <div className="p-3 bg-white rounded-lg border border-slate-200/90 shadow-2xs space-y-2">
            <div className="text-[11px] font-semibold text-slate-500 flex items-center gap-1.5">
              <span>🖼️ Sơ đồ bài toán / Problem Diagram:</span>
            </div>
            <div className="flex justify-center bg-slate-50/50 p-2 rounded border border-slate-100">
              <img
                src={resolveImagePath(figure_image)}
                alt={source_problem}
                className="max-h-64 object-contain rounded hover:scale-105 transition-transform duration-200"
                loading="lazy"
              />
            </div>
          </div>
        )}

        {/* Self Practice Answer Box */}
        {expected_numeric_value !== null && <div className="bg-gradient-to-r from-sky-50/80 to-slate-50/80 p-3.5 rounded-lg border border-sky-100 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-sky-900 flex items-center gap-1.5">
              {numeric_target_label
                ? <MathRenderer text={`✍️ Kiểm tra ${numeric_target_label}`} />
                : <span>✍️ Tự bấm máy & Điền đáp số kiểm tra:</span>}
            </span>
            <span className="text-[11px] text-slate-500">
              {numeric_target_label ? '(Có thể nhập dạng 1.23e-4)' : '(Làm tròn 4 chữ số thập phân)'}
            </span>
          </div>

          <form onSubmit={handleCheckAnswer} className="flex items-center gap-2 flex-wrap">
            <div className="relative flex-1 min-w-[200px]">
              <input
                type="text"
                placeholder="Nhập giá trị xấp xỉ của bạn (vd: 5.6250)"
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                className="w-full px-3 py-1.5 text-xs font-mono bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              className="px-3 py-1.5 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-colors"
            >
              <Send size={12} /> Kiểm tra đáp số
            </button>
            {evalResult && (
              <button
                type="button"
                onClick={handleResetAnswer}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-200/60 transition-colors"
                title="Nhập lại"
              >
                <RotateCcw size={14} />
              </button>
            )}
          </form>

          {/* Feedback Banner */}
          {evalResult && (
            <div className="animate-fadeIn pt-1">
              {evalResult.status === 'correct' && (
                <div className="flex items-center gap-2 p-2.5 bg-emerald-100/80 border border-emerald-300 rounded-lg text-xs text-emerald-900 font-medium">
                  <Trophy size={16} className="text-emerald-600 flex-shrink-0" />
                  <div>
                    🎉 <strong>Xuất sắc, chính xác!</strong> Đáp số bạn nhập (<code>{evalResult.userVal}</code>) khớp với kết quả kiểm chứng (độ lệch {evalResult.diffPercent}%).
                  </div>
                </div>
              )}
              {evalResult.status === 'close' && (
                <div className="flex items-center gap-2 p-2.5 bg-amber-100/80 border border-amber-300 rounded-lg text-xs text-amber-900 font-medium">
                  <AlertTriangle size={16} className="text-amber-600 flex-shrink-0" />
                  <div>
                    ⚠️ <strong>Rất gần đáp số!</strong> Độ lệch ~{evalResult.diffPercent}%. Hãy kiểm tra lại số vòng lặp hoặc quy tắc làm tròn 4 chữ số thập phân.
                  </div>
                </div>
              )}
              {evalResult.status === 'wrong' && (
                <div className="flex items-center gap-2 p-2.5 bg-rose-100/80 border border-rose-300 rounded-lg text-xs text-rose-900 font-medium">
                  <XCircle size={16} className="text-rose-600 flex-shrink-0" />
                  <div>
                    ❌ <strong>Chưa chính xác</strong> (Độ lệch {evalResult.diffPercent}%). Bấm vào <strong>[1. Xem Gợi ý]</strong> hoặc <strong>[2. Bước 1: Công thức]</strong> để dò lại từng bước nhé!
                  </div>
                </div>
              )}
              {evalResult.status === 'invalid' && (
                <div className="text-xs text-rose-600 font-medium">
                  ⚠️ {evalResult.message}
                </div>
              )}
              {evalResult.status === 'unknown' && (
                <div className="text-xs text-sky-700 font-medium">
                  ℹ️ {evalResult.message}
                </div>
              )}
            </div>
          )}
        </div>}

        {/* Action Buttons: Active Recall Progression */}
        <div className="pt-2 flex flex-wrap items-center gap-2 border-t border-slate-100">
          <button
            onClick={() => setShowHint(!showHint)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              showHint
                ? 'bg-amber-100 text-amber-900 border border-amber-300'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <Lightbulb size={14} className={showHint ? 'text-amber-600' : 'text-slate-500'} />
            {showHint ? 'Ẩn Gợi ý' : '1. Xem Gợi ý'}
          </button>

          <button
            onClick={() => setActiveStep(activeStep >= 1 ? 0 : 1)}
            className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeStep >= 1
                ? 'bg-sky-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            2. Bước 1: Công thức
          </button>

          <button
            onClick={() => setActiveStep(activeStep >= 2 ? 1 : 2)}
            className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeStep >= 2
                ? 'bg-sky-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            {isDirectFEM ? '3. Bước 2: Lập hệ' : '3. Bước 2: Bảng lặp số'}
          </button>

          <button
            onClick={() => setActiveStep(activeStep >= 3 ? 2 : 3)}
            className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeStep >= 3
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <CheckCircle2 size={13} />
            4. Bước 3 & Đáp số
          </button>
        </div>

        {/* Revealed Layers */}
        {showHint && hint && (
          <div className="bg-amber-50/80 border border-amber-200/80 rounded-lg p-3.5 text-xs text-amber-900 animate-fadeIn">
            <div className="font-semibold text-amber-800 mb-1 flex items-center gap-1.5">
              <Lightbulb size={14} className="text-amber-600" />
              Gợi ý phương pháp & Điều kiện dừng:
            </div>
            <MathRenderer text={hint} />
          </div>
        )}

        {activeStep >= 1 && steps[0] && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 animate-fadeIn">
            <MarkdownView content={steps[0]} />
          </div>
        )}

        {activeStep >= 2 && steps[1] && (
          <div className="bg-white border-2 border-sky-200 rounded-lg p-4 shadow-inner animate-fadeIn">
            <div className="text-xs font-bold text-sky-800 uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <span>{isDirectFEM ? 'Lập hệ và áp điều kiện biên:' : '📊 Bảng tính toán lặp số học (Kiểm chứng từ Python):'}</span>
            </div>
            <MarkdownView content={steps[1]} />
          </div>
        )}

        {activeStep >= 3 && (
          <div className="space-y-3 animate-fadeIn">
            {steps[2] && (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                <MarkdownView content={steps[2]} />
              </div>
            )}

            {final_answer && (
              <div className="bg-emerald-50 border-2 border-emerald-300 rounded-lg p-3.5 flex items-center justify-between flex-wrap gap-2 text-emerald-950">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={18} className="text-emerald-600" />
                  <span className="font-semibold text-xs uppercase tracking-wider text-emerald-800">
                    Đáp số cuối cùng:
                  </span>
                </div>
                <div className="font-mono font-bold text-sm bg-white px-3 py-1 rounded border border-emerald-200 text-emerald-900">
                  <MathRenderer text={`$${final_answer}$`} />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
