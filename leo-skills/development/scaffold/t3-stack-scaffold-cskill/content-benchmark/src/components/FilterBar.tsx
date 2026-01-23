"use client";

import { useState } from "react";

interface FilterBarProps {
  platforms: string[];
  contentTypes: string[];
  onFilterChange: (filters: FilterState) => void;
}

export interface FilterState {
  platform: string;
  contentType: string;
  sortBy: string;
  searchQuery: string;
}

export function FilterBar({ platforms, contentTypes, onFilterChange }: FilterBarProps) {
  const [filters, setFilters] = useState<FilterState>({
    platform: "",
    contentType: "",
    sortBy: "likes",
    searchQuery: "",
  });
  const [isExpanded, setIsExpanded] = useState(false);

  const updateFilter = (key: keyof FilterState, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-4 mb-6">
      {/* 搜索栏 */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 relative">
          <svg
            className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="搜索标题关键词..."
            value={filters.searchQuery}
            onChange={(e) => updateFilter("searchQuery", e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
          />
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`px-4 py-3 rounded-xl font-medium text-sm transition flex items-center space-x-2 ${
            isExpanded ? "bg-blue-50 text-blue-600" : "bg-gray-50 text-gray-600 hover:bg-gray-100"
          }`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span>筛选</span>
          {(filters.platform || filters.contentType) && (
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
          )}
        </button>

        <select
          value={filters.sortBy}
          onChange={(e) => updateFilter("sortBy", e.target.value)}
          className="px-4 py-3 bg-gray-50 border-0 rounded-xl text-sm text-gray-600 focus:ring-2 focus:ring-blue-500 cursor-pointer"
        >
          <option value="likes">按点赞排序</option>
          <option value="comments">按评论排序</option>
          <option value="shares">按分享排序</option>
          <option value="newest">最新收集</option>
        </select>
      </div>

      {/* 展开的筛选器 */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">平台:</span>
            <div className="flex space-x-2">
              <FilterChip
                label="全部"
                active={!filters.platform}
                onClick={() => updateFilter("platform", "")}
              />
              {platforms.map((p) => (
                <FilterChip
                  key={p}
                  label={p}
                  active={filters.platform === p}
                  onClick={() => updateFilter("platform", p)}
                />
              ))}
            </div>
          </div>

          <div className="w-px h-6 bg-gray-200"></div>

          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">类型:</span>
            <div className="flex space-x-2">
              <FilterChip
                label="全部"
                active={!filters.contentType}
                onClick={() => updateFilter("contentType", "")}
              />
              {contentTypes.map((t) => (
                <FilterChip
                  key={t}
                  label={t}
                  active={filters.contentType === t}
                  onClick={() => updateFilter("contentType", t)}
                />
              ))}
            </div>
          </div>

          {(filters.platform || filters.contentType) && (
            <>
              <div className="w-px h-6 bg-gray-200"></div>
              <button
                onClick={() => {
                  const newFilters = { ...filters, platform: "", contentType: "" };
                  setFilters(newFilters);
                  onFilterChange(newFilters);
                }}
                className="text-sm text-red-500 hover:text-red-600"
              >
                清除筛选
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function FilterChip({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
        active
          ? "bg-blue-500 text-white"
          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
      }`}
    >
      {label}
    </button>
  );
}
