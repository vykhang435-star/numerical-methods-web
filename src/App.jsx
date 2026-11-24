import React, { useState, useMemo } from 'react';
import syllabusData from '../data/syllabus_map.json';

// Import all chapter datasets
import ch01Data from '../data/ch01_errors.json';
import ch02Data from '../data/ch02_roots.json';
import ch03Data from '../data/ch03_linear_systems.json';
import ch04Data from '../data/ch04_interpolation.json';
import ch05Data from '../data/ch05_calculus.json';
import ch06Data from '../data/ch06_ode.json';
import ch07Data from '../data/ch07_fem.json';

import Sidebar from './components/Sidebar';
import ExerciseCard from './components/ExerciseCard';
import MathRenderer from './components/MathRenderer';
import { Search, Sparkles, Flame, AlertCircle } from 'lucide-react';

const CHAPTER_DATA_MAP = {
  ch01_errors: ch01Data,
  ch02_roots: ch02Data,
  ch03_linear_systems: ch03Data,
  ch04_interpolation: ch04Data,
  ch05_calculus: ch05Data,
  ch06_ode: ch06Data,
  ch07_fem: ch07Data
};

export default function App() {
  const [selectedChapterId, setSelectedChapterId] = useState('ch02_roots');
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [examOnly, setExamOnly] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Selected chapter metadata
  const currentChapter = useMemo(() => {
    return syllabusData.chapters.find(c => c.chapter_id === selectedChapterId) || syllabusData.chapters[0];
  }, [selectedChapterId]);

  // Chapter item counts for badges
  const chapterCounts = useMemo(() => {
    const counts = {};
    for (const [key, data] of Object.entries(CHAPTER_DATA_MAP)) {
      counts[key] = Array.isArray(data) ? data.length : 0;
    }
    return counts;
  }, []);

  // Raw problems of selected chapter
  const currentChapterProblems = useMemo(() => {
    return CHAPTER_DATA_MAP[selectedChapterId] || [];
  }, [selectedChapterId]);

  // Available methods for current chapter
  const availableMethods = useMemo(() => {
    const set = new Set(currentChapterProblems.map(p => p.method_tag));
    return Array.from(set);
  }, [currentChapterProblems]);

  // Filtered problems
  const filteredProblems = useMemo(() => {
    return currentChapterProblems.filter(item => {
      if (examOnly && !item.exam_focus) return false;
      if (selectedMethod && item.method_tag !== selectedMethod) return false;
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesEn = item.problem_en.toLowerCase().includes(query);
        const matchesSource = item.source_problem.toLowerCase().includes(query);
        const matchesMethod = item.method_tag.toLowerCase().includes(query);
        if (!matchesEn && !matchesSource && !matchesMethod) return false;
      }
      return true;
    });
  }, [currentChapterProblems, examOnly, selectedMethod, searchQuery]);

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <Sidebar
        chapters={syllabusData.chapters}
        chapterCounts={chapterCounts}
        selectedChapterId={selectedChapterId}
        onSelectChapter={(id) => {
          setSelectedChapterId(id);
          setSelectedMethod(null);
        }}
        methods={availableMethods}
        selectedMethod={selectedMethod}
        onSelectMethod={setSelectedMethod}
        examOnly={examOnly}
        onToggleExamOnly={setExamOnly}
      />

      {/* Main Content */}
      <main className="flex-1 min-w-0 flex flex-col">
        {/* Top Header */}
        <header className="sticky top-0 z-20 bg-white/95 backdrop-blur-sm border-b border-slate-200 px-8 py-4">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                  {currentChapter.title_vi}
                </h2>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-mono">
                  {currentChapter.chapter_id}
                </span>
              </div>
              <div className="flex items-center gap-2 flex-wrap text-xs text-slate-500 mt-1">
                <span>{currentChapter.title_en}</span>
                {currentChapter.lecture_ref && (
                  <>
                    <span>•</span>
                    <span className="font-medium text-sky-800 bg-sky-50 px-2 py-0.5 rounded border border-sky-200 flex items-center gap-1 text-[11px]">
                      📖 Bài giảng KLG: {currentChapter.lecture_ref}
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Quick Search */}
            <div className="relative w-72">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Tìm bài tập, từ khóa, công thức..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 bg-slate-50 hover:bg-white focus:bg-white border border-slate-200 rounded-lg text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all"
              />
            </div>
          </div>
        </header>

        {/* Content Body */}
        <div className="flex-1 p-8 max-w-5xl space-y-6">
          {/* Chapter Outline & Learning Outcomes Banner */}
          <div className="bg-gradient-to-r from-sky-50 via-white to-slate-50 border border-sky-100 rounded-xl p-5 shadow-xs">
            <div className="text-xs font-bold text-sky-900 uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <Sparkles size={14} className="text-sky-600" />
              Chuẩn đầu ra & Dạng bài thi ME2091
            </div>
            <div className="space-y-1.5">
              {currentChapter.learning_outcomes.map((lo, idx) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-slate-700 leading-relaxed">
                  <span className="text-sky-500 font-bold">•</span>
                  <span>{lo}</span>
                </div>
              ))}
            </div>

            {/* Exam Patterns Pills */}
            {currentChapter.exam_patterns && currentChapter.exam_patterns.length > 0 && (
              <div className="mt-4 pt-3 border-t border-sky-100/70 flex flex-wrap gap-2 items-center">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Dạng bài trọng điểm:
                </span>
                {currentChapter.exam_patterns.map((pat, pIdx) => (
                  <span
                    key={pIdx}
                    className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-md bg-white border border-slate-200 text-slate-700 shadow-2xs"
                  >
                    <Flame size={11} className="text-amber-500" />
                    {pat.pattern_name}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Display Problems List for Selected Chapter */}
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500 px-1">
              <span>
                Hiển thị <strong>{filteredProblems.length}</strong> bài tập luyện giải (
                {examOnly ? 'chế độ trọng tâm thi' : 'toàn bộ bài tập đã kiểm chứng số học'})
              </span>
              <span className="font-mono text-[11px] text-sky-700 bg-sky-50 px-2 py-0.5 rounded">
                ✓ Số liệu lặp kiểm chứng Python (numpy/math)
              </span>
            </div>

            {filteredProblems.length > 0 ? (
              <div className="space-y-5">
                {filteredProblems.map((prob, idx) => (
                  <ExerciseCard key={prob.id} problem={prob} index={idx} />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-500 space-y-2">
                <AlertCircle size={32} className="mx-auto text-slate-400" />
                <p className="font-medium">Không tìm thấy bài tập phù hợp với bộ lọc hiện tại.</p>
                <p className="text-xs">Hãy thử tắt nút "Chỉ hiện bài trọng tâm thi" hoặc xóa bộ lọc phương pháp tính.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
