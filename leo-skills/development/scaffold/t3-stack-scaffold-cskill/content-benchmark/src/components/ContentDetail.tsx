"use client";

import { useState } from "react";

interface ContentDetailProps {
  isOpen: boolean;
  onClose: () => void;
  content: {
    id: string;
    title: string;
    content?: string;
    contentType: string;
    likes?: number;
    comments?: number;
    shares?: number;
    sourceUrl?: string;
    account?: { platform: string; accountName: string };
  } | null;
  onAnalyze: () => void;
  onRewrite: () => void;
}

export function ContentDetail({ isOpen, onClose, content, onAnalyze, onRewrite }: ContentDetailProps) {
  const [activeTab, setActiveTab] = useState<"content" | "analysis" | "rewrite">("content");

  if (!isOpen || !content) return null;

  // 计算互动率
  const totalEngagement = (content.likes || 0) + (content.comments || 0) + (content.shares || 0);
  const engagementRate = content.likes ? ((content.comments || 0) / content.likes * 100).toFixed(1) : "0";

  return (
    <>
      {/* 遮罩层 */}
      <div
        className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />

      {/* 抽屉 */}
      <div className="fixed right-0 top-0 h-full w-[600px] bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-out overflow-hidden flex flex-col">
        {/* 头部 */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-start justify-between">
            <div className="flex-1 pr-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="px-2.5 py-1 bg-red-50 text-red-600 rounded-lg text-xs font-medium">
                  📕 {content.account?.platform}
                </span>
                <span className="px-2.5 py-1 bg-gray-100 text-gray-600 rounded-lg text-xs">
                  {content.contentType}
                </span>
              </div>
              <h2 className="text-xl font-bold text-gray-800 leading-tight">
                {content.title}
              </h2>
              <p className="text-sm text-gray-400 mt-2">
                来自 {content.account?.accountName}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* 数据指标 */}
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="text-center p-3 bg-gradient-to-br from-red-50 to-pink-50 rounded-xl">
              <div className="text-2xl font-bold text-red-600">{(content.likes || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-500 mt-1">点赞</div>
            </div>
            <div className="text-center p-3 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl">
              <div className="text-2xl font-bold text-blue-600">{(content.comments || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-500 mt-1">评论</div>
            </div>
            <div className="text-center p-3 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl">
              <div className="text-2xl font-bold text-green-600">{(content.shares || 0).toLocaleString()}</div>
              <div className="text-xs text-gray-500 mt-1">分享</div>
            </div>
            <div className="text-center p-3 bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl">
              <div className="text-2xl font-bold text-purple-600">{engagementRate}%</div>
              <div className="text-xs text-gray-500 mt-1">互动率</div>
            </div>
          </div>
        </div>

        {/* 标签页 */}
        <div className="px-6 pt-4 border-b border-gray-100">
          <div className="flex space-x-1">
            {[
              { key: "content", label: "内容详情", icon: "📄" },
              { key: "analysis", label: "拆解框架", icon: "🔍" },
              { key: "rewrite", label: "仿写指南", icon: "✍️" },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition ${
                  activeTab === tab.key
                    ? "bg-blue-50 text-blue-600 border-b-2 border-blue-600"
                    : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* 内容区 */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === "content" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <span className="w-1 h-4 bg-blue-500 rounded mr-2"></span>
                  内容正文
                </h3>
                <div className="bg-gray-50 rounded-xl p-4 text-gray-600 leading-relaxed">
                  {content.content || "暂无正文内容，点击编辑添加"}
                </div>
              </div>

              {content.sourceUrl && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <span className="w-1 h-4 bg-green-500 rounded mr-2"></span>
                    原文链接
                  </h3>
                  <a
                    href={content.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600 text-sm break-all"
                  >
                    {content.sourceUrl}
                  </a>
                </div>
              )}

              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <span className="w-1 h-4 bg-orange-500 rounded mr-2"></span>
                  爆款指数分析
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">标题吸引力</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-orange-400 to-red-500 rounded-full" style={{ width: "85%" }}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-700">85</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">互动表现</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-blue-400 to-cyan-500 rounded-full" style={{ width: "72%" }}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-700">72</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">传播潜力</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full" style={{ width: "68%" }}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-700">68</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "analysis" && (
            <div className="space-y-4">
              <p className="text-sm text-gray-500 mb-4">
                使用以下框架拆解这条爆款内容，找出可复用的套路
              </p>

              {[
                { title: "🎣 开头钩子", desc: "前3秒/前2行如何抓住注意力？", placeholder: "分析开头使用了什么技巧吸引用户停留..." },
                { title: "📐 内容结构", desc: "整体框架是怎样的？", placeholder: "总分总/问题-方案-结果/故事线..." },
                { title: "💡 核心价值", desc: "提供了什么价值？", placeholder: "信息差/情绪价值/实用技巧/认知升级..." },
                { title: "😊 情绪触发", desc: "哪些点引发共鸣？", placeholder: "痛点共鸣/焦虑/好奇/认同感..." },
                { title: "📢 行动号召", desc: "如何引导用户互动？", placeholder: "评论区见/点赞收藏/关注不迷路..." },
              ].map((item, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-800">{item.title}</h4>
                    <span className="text-xs text-gray-400">{item.desc}</span>
                  </div>
                  <textarea
                    className="w-full bg-white border border-gray-200 rounded-lg p-3 text-sm text-gray-600 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={2}
                    placeholder={item.placeholder}
                  />
                </div>
              ))}

              <button
                onClick={onAnalyze}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-purple-500/25 transition-all"
              >
                💾 保存拆解分析
              </button>
            </div>
          )}

          {activeTab === "rewrite" && (
            <div className="space-y-4">
              <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-4 border border-orange-100">
                <h4 className="font-medium text-orange-800 mb-2">✨ 仿写建议</h4>
                <ul className="text-sm text-orange-700 space-y-1">
                  <li>• 保留爆款的结构框架，替换具体内容</li>
                  <li>• 结合宁波本地化元素，增加亲近感</li>
                  <li>• 使用相似的情绪触发点</li>
                  <li>• 标题可以借鉴句式，换关键词</li>
                </ul>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">仿写标题</label>
                <input
                  type="text"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="参考原标题，写出你的版本..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">仿写正文</label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                  rows={8}
                  placeholder="保留结构，替换内容..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">切入角度</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    placeholder="如：宁波本地化"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">目标受众</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    placeholder="如：宁波购房者"
                  />
                </div>
              </div>

              <button
                onClick={onRewrite}
                className="w-full py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all"
              >
                ✍️ 保存仿写
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
