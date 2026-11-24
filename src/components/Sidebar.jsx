import React from 'react';
import { BookOpen, Flame, Filter, Award } from 'lucide-react';

export default function Sidebar({
  chapters = [],
  chapterCounts = {},
  selectedChapterId,
  onSelectChapter,
  methods = [],
  selectedMethod,
  onSelectMethod,
  examOnly,
  onToggleExamOnly
}) {
  return (
    <aside className="w-80 flex-shrink-0 bg-white border-r border-slate-200 min-h-screen p-5 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Brand / Course Info */}
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center font-bold text-sm shadow-sm">
              ∑
            </span>
            <div>
              <h1 className="font-bold text-slate-900 text-base leading-tight">ME2091</h1>
              <p className="text-xs text-slate-500 font-medium">Phương Pháp Số • HCMUT</p>
            </div>
          </div>
          <div className="mt-3 px-3 py-2 bg-slate-50 rounded-lg border border-slate-100 text-xs text-slate-600 space-y-1">
            <div className="flex items-center gap-1.5 text-slate-700 font-medium">
              <Award size={13} className="text-sky-600" />
              <span>Giáo trình: Chapra & Canale</span>
            </div>
            <p className="text-[11px] text-slate-400">Numerical Methods for Engineers</p>
          </div>
        </div>

        {/* Exam Focus Filter Toggle */}
        <div className="pt-1">
          <label className="flex items-center justify-between p-3 rounded-xl border border-amber-200/90 bg-amber-50/60 hover:bg-amber-50 cursor-pointer transition-all shadow-sm">
            <div className="flex items-center gap-2">
              <Flame size={18} className="text-amber-500 fill-amber-400" />
              <div>
                <div className="text-xs font-bold text-amber-950">Chế độ Ôn thi</div>
                <div className="text-[11px] text-amber-700">Chỉ hiện bài trọng tâm thi</div>
              </div>
            </div>
            <input
              type="checkbox"
              checked={examOnly}
              onChange={(e) => onToggleExamOnly(e.target.checked)}
              className="w-4 h-4 text-sky-600 rounded border-amber-300 focus:ring-sky-500 cursor-pointer"
            />
          </label>
        </div>

        {/* Chapters list */}
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
            <BookOpen size={13} />
            Danh sách chương ({chapters.length})
          </div>
          <div className="space-y-1">
            {chapters.map((ch) => {
              const isSelected = ch.chapter_id === selectedChapterId;
              const count = chapterCounts[ch.chapter_id] || 0;

              return (
                <button
                  key={ch.chapter_id}
                  onClick={() => onSelectChapter(ch.chapter_id)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-xs font-medium transition-all flex items-start justify-between gap-2 ${
                    isSelected
                      ? 'bg-sky-50 text-sky-900 border border-sky-200 font-semibold shadow-xs'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 border border-transparent'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="truncate">{ch.title_vi}</div>
                    <div className="text-[11px] text-slate-400 font-normal truncate">
                      {ch.title_en}
                    </div>
                  </div>
                  {count > 0 && (
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold flex-shrink-0 ${
                      isSelected
                        ? 'bg-sky-600 text-white'
                        : 'bg-slate-100 text-slate-700 border border-slate-200'
                    }`}>
                      {count} bài
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Methods Filter */}
        {methods.length > 0 && (
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Filter size={13} />
                Phương pháp tính
              </span>
              {selectedMethod && (
                <button
                  onClick={() => onSelectMethod(null)}
                  className="text-[11px] text-sky-600 hover:underline normal-case font-normal"
                >
                  Xóa lọc
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {methods.map((method) => {
                const isSelected = selectedMethod === method;
                return (
                  <button
                    key={method}
                    onClick={() => onSelectMethod(isSelected ? null : method)}
                    className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                      isSelected
                        ? 'bg-sky-600 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {method}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="pt-6 border-t border-slate-100 text-xs text-slate-400 space-y-1">
        <p className="font-medium text-slate-600">Đại học Bách Khoa TP.HCM</p>
        <p className="text-[11px]">Đề cương ME2091 • Bộ môn Thiết kế máy</p>
      </div>
    </aside>
  );
}
