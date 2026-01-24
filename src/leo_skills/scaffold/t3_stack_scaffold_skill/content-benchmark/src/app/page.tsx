"use client";

import { useState, useMemo } from "react";
import { AddAccountForm, type AccountFormData } from "@/components/AddAccountForm";
import { AddContentForm, type ContentFormData } from "@/components/AddContentForm";
import { AnalysisForm, type AnalysisFormData } from "@/components/AnalysisForm";
import { RewriteForm, type RewriteFormData } from "@/components/RewriteForm";
import { ContentDetail } from "@/components/ContentDetail";
import { FilterBar, type FilterState } from "@/components/FilterBar";

// 模拟数据
const initialAccounts = [
  { id: "1", platform: "小红书", accountName: "房产小王子", category: "房产", followers: 50000, style: "接地气、真实分享", contentCount: 12 },
  { id: "2", platform: "抖音", accountName: "宁波买房攻略", category: "房产", followers: 120000, style: "专业分析、数据说话", contentCount: 8 },
  { id: "3", platform: "公众号", accountName: "商业地产观察", category: "商业地产", followers: 30000, style: "深度长文、案例分析", contentCount: 15 },
];

const initialContents = [
  { id: "1", accountId: "1", title: "宁波这个板块要爆了！内行人都在偷偷买", content: "最近很多粉丝私信问我，宁波哪个板块最有潜力？今天就给大家揭秘一个内行人都在关注的区域...", likes: 5200, comments: 328, shares: 156, contentType: "短视频", account: { platform: "小红书", accountName: "房产小王子" } },
  { id: "2", accountId: "1", title: "买商铺千万别踩这5个坑，血泪教训", content: "作为一个在商业地产摸爬滚打10年的老兵，今天把我踩过的坑全部分享给大家...", likes: 3800, comments: 245, shares: 89, contentType: "图文", account: { platform: "小红书", accountName: "房产小王子" } },
  { id: "3", accountId: "2", title: "2024宁波最值得投资的3个区域", content: "根据最新的城市规划和土地出让数据，我整理了2024年宁波最具投资价值的三个区域...", likes: 8900, comments: 567, shares: 234, contentType: "短视频", account: { platform: "抖音", accountName: "宁波买房攻略" } },
  { id: "4", accountId: "3", title: "菜场摊位投资回报率深度分析", content: "很多人问我菜场摊位值不值得投资？今天用数据说话，给大家算一笔账...", likes: 2100, comments: 156, shares: 78, contentType: "文章", account: { platform: "公众号", accountName: "商业地产观察" } },
];

const platformColors: Record<string, { bg: string; text: string; icon: string; gradient: string }> = {
  "小红书": { bg: "bg-red-50", text: "text-red-600", icon: "📕", gradient: "from-red-500 to-pink-500" },
  "抖音": { bg: "bg-gray-900", text: "text-white", icon: "🎵", gradient: "from-gray-800 to-gray-900" },
  "公众号": { bg: "bg-green-50", text: "text-green-600", icon: "💬", gradient: "from-green-500 to-emerald-500" },
  "视频号": { bg: "bg-orange-50", text: "text-orange-600", icon: "📹", gradient: "from-orange-500 to-amber-500" },
  "B站": { bg: "bg-pink-50", text: "text-pink-600", icon: "📺", gradient: "from-pink-500 to-rose-500" },
  "快手": { bg: "bg-orange-50", text: "text-orange-500", icon: "⚡", gradient: "from-orange-400 to-yellow-500" },
};

export default function Home() {
  const [activeTab, setActiveTab] = useState<"contents" | "rewrites">("contents");
  const [accounts, setAccounts] = useState(initialAccounts);
  const [contents, setContents] = useState(initialContents);
  const [rewrites, setRewrites] = useState<any[]>([
    { id: "1", title: "宁波东部新城这个楼盘，懂行的都在看", body: "最近很多粉丝问我东部新城还能不能买？作为深耕宁波楼市8年的从业者，今天给大家分析一下...", angle: "宁波本地化", targetAudience: "宁波购房者", status: "draft", contentId: "1" },
  ]);

  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showAddContent, setShowAddContent] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [showRewrite, setShowRewrite] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [selectedContent, setSelectedContent] = useState<any>(null);
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({ platform: "", contentType: "", sortBy: "likes", searchQuery: "" });

  // 筛选和排序内容
  const filteredContents = useMemo(() => {
    let result = [...contents];

    // 按账号筛选
    if (selectedAccount) {
      result = result.filter(c => c.accountId === selectedAccount);
    }

    // 按平台筛选
    if (filters.platform) {
      result = result.filter(c => c.account?.platform === filters.platform);
    }

    // 按类型筛选
    if (filters.contentType) {
      result = result.filter(c => c.contentType === filters.contentType);
    }

    // 搜索
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      result = result.filter(c => c.title.toLowerCase().includes(query));
    }

    // 排序
    result.sort((a, b) => {
      switch (filters.sortBy) {
        case "likes": return (b.likes || 0) - (a.likes || 0);
        case "comments": return (b.comments || 0) - (a.comments || 0);
        case "shares": return (b.shares || 0) - (a.shares || 0);
        default: return 0;
      }
    });

    return result;
  }, [contents, selectedAccount, filters]);

  const platforms = [...new Set(contents.map(c => c.account?.platform).filter(Boolean))] as string[];
  const contentTypes = [...new Set(contents.map(c => c.contentType))];

  const handleAddAccount = async (data: AccountFormData) => {
    const newAccount = { ...data, id: Date.now().toString(), contentCount: 0 };
    setAccounts([newAccount, ...accounts]);
  };

  const handleAddContent = async (data: ContentFormData) => {
    const account = accounts.find(a => a.id === data.accountId);
    const newContent = {
      ...data,
      id: Date.now().toString(),
      account: account ? { platform: account.platform, accountName: account.accountName } : undefined
    };
    setContents([newContent, ...contents]);
  };

  const handleAnalysis = async (data: AnalysisFormData) => {
    console.log("拆解分析:", data);
  };

  const handleRewrite = async (data: RewriteFormData) => {
    const newRewrite = { ...data, id: Date.now().toString(), status: "draft", createdAt: new Date() };
    setRewrites([newRewrite, ...rewrites]);
  };

  const openDetail = (content: any) => {
    setSelectedContent(content);
    setShowDetail(true);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* 顶部导航 */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                <span className="text-white text-xl">🎯</span>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                  对标拆解仿写
                </h1>
                <p className="text-xs text-gray-400">收集爆款 → 拆解套路 → 仿写变现</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                <span>导入</span>
              </button>
              <button className="px-4 py-2 text-sm bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:shadow-lg hover:shadow-blue-500/25 transition-all flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <span>导出报告</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* 数据概览卡片 */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <StatCard icon="👤" title="对标账号" value={accounts.length} trend="+2 本周" gradient="from-blue-500 to-cyan-500" />
          <StatCard icon="📝" title="收集内容" value={contents.length} trend="+5 本周" gradient="from-emerald-500 to-teal-500" />
          <StatCard icon="🔍" title="拆解分析" value={12} trend="+3 本周" gradient="from-purple-500 to-pink-500" />
          <StatCard icon="✍️" title="仿写内容" value={rewrites.length} trend="+1 本周" gradient="from-orange-500 to-red-500" />
        </div>

        {/* 主内容区 */}
        <div className="flex gap-6">
          {/* 左侧：账号列表 */}
          <div className="w-72 flex-shrink-0">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden sticky top-24">
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <h2 className="font-semibold text-gray-800">对标账号</h2>
                <button
                  onClick={() => setShowAddAccount(true)}
                  className="w-8 h-8 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition flex items-center justify-center"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              </div>
              <div className="divide-y divide-gray-50 max-h-[calc(100vh-300px)] overflow-y-auto">
                <button
                  onClick={() => setSelectedAccount(null)}
                  className={`w-full p-4 text-left hover:bg-gray-50 transition ${!selectedAccount ? 'bg-blue-50 border-l-4 border-blue-500' : ''}`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex items-center justify-center">
                      <span>📊</span>
                    </div>
                    <div>
                      <div className="font-medium text-gray-800">全部内容</div>
                      <div className="text-xs text-gray-400">{contents.length} 条内容</div>
                    </div>
                  </div>
                </button>
                {accounts.map((account) => {
                  const colors = platformColors[account.platform] || { bg: "bg-gray-50", text: "text-gray-600", icon: "📱", gradient: "from-gray-400 to-gray-500" };
                  const accountContents = contents.filter(c => c.accountId === account.id);
                  return (
                    <button
                      key={account.id}
                      onClick={() => setSelectedAccount(account.id)}
                      className={`w-full p-4 text-left hover:bg-gray-50 transition ${selectedAccount === account.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''}`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 bg-gradient-to-br ${colors.gradient} rounded-xl flex items-center justify-center shadow-sm`}>
                          <span className="text-white text-sm">{colors.icon}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-800 truncate">{account.accountName}</div>
                          <div className="flex items-center space-x-2 text-xs text-gray-400">
                            <span>{account.platform}</span>
                            <span>·</span>
                            <span>{(account.followers / 10000).toFixed(1)}w粉</span>
                            <span>·</span>
                            <span>{accountContents.length}条</span>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* 右侧：内容区 */}
          <div className="flex-1">
            {/* 标签页 */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex bg-gray-100 rounded-xl p-1">
                {[
                  { key: "contents", label: "爆款内容", icon: "🔥", count: filteredContents.length },
                  { key: "rewrites", label: "我的仿写", icon: "✍️", count: rewrites.length },
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key as any)}
                    className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center space-x-2 ${
                      activeTab === tab.key
                        ? "bg-white text-gray-900 shadow-sm"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                    <span className={`px-1.5 py-0.5 rounded text-xs ${activeTab === tab.key ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-500'}`}>
                      {tab.count}
                    </span>
                  </button>
                ))}
              </div>
              {activeTab === "contents" && (
                <button
                  onClick={() => setShowAddContent(true)}
                  className="px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-sm font-medium rounded-xl hover:shadow-lg hover:shadow-emerald-500/25 transition-all flex items-center space-x-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>收集内容</span>
                </button>
              )}
            </div>

            {/* 筛选栏 */}
            {activeTab === "contents" && (
              <FilterBar
                platforms={platforms}
                contentTypes={contentTypes}
                onFilterChange={setFilters}
              />
            )}

            {/* 内容列表 */}
            {activeTab === "contents" && (
              <>
                {filteredContents.length === 0 ? (
                  <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center">
                    <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <span className="text-4xl">📭</span>
                    </div>
                    <h3 className="font-semibold text-gray-800 mb-2">没有找到内容</h3>
                    <p className="text-gray-400 text-sm mb-4">
                      {filters.searchQuery ? "尝试其他关键词" : "点击上方按钮收集第一条爆款内容"}
                    </p>
                    <button
                      onClick={() => setShowAddContent(true)}
                      className="px-4 py-2 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition"
                    >
                      收集内容
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    {filteredContents.map((content) => {
                      const colors = platformColors[content.account?.platform || ""] || { bg: "bg-gray-50", text: "text-gray-600", icon: "📱", gradient: "from-gray-400 to-gray-500" };
                      return (
                        <div
                          key={content.id}
                          onClick={() => openDetail(content)}
                          className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-xl hover:shadow-gray-200/50 hover:border-gray-200 hover:-translate-y-1 transition-all cursor-pointer group"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-gradient-to-r ${colors.gradient} text-white shadow-sm`}>
                              {colors.icon} {content.account?.platform}
                            </span>
                            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">{content.contentType}</span>
                          </div>
                          <h3 className="font-semibold text-gray-800 mb-3 line-clamp-2 group-hover:text-blue-600 transition">
                            {content.title}
                          </h3>
                          <p className="text-sm text-gray-400 line-clamp-2 mb-4">
                            {content.content || "暂无正文内容"}
                          </p>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4 text-sm text-gray-400">
                              <span className="flex items-center">
                                <span className="text-red-400 mr-1">❤️</span>
                                {(content.likes || 0).toLocaleString()}
                              </span>
                              <span className="flex items-center">
                                <span className="mr-1">💬</span>
                                {(content.comments || 0).toLocaleString()}
                              </span>
                              <span className="flex items-center">
                                <span className="mr-1">🔄</span>
                                {(content.shares || 0).toLocaleString()}
                              </span>
                            </div>
                            <div className="opacity-0 group-hover:opacity-100 transition">
                              <span className="text-xs text-blue-500">点击查看详情 →</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            )}

            {activeTab === "rewrites" && (
              <div className="space-y-4">
                {rewrites.length === 0 ? (
                  <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-orange-100 to-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <span className="text-4xl">✍️</span>
                    </div>
                    <h3 className="font-semibold text-gray-800 mb-2">还没有仿写内容</h3>
                    <p className="text-gray-400 text-sm">从爆款内容中选择一条开始仿写吧</p>
                  </div>
                ) : (
                  rewrites.map((rewrite) => (
                    <div key={rewrite.id} className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-lg hover:shadow-gray-200/50 transition-all">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-3">
                            <span className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                              rewrite.status === "published"
                                ? "bg-green-100 text-green-600"
                                : "bg-gray-100 text-gray-500"
                            }`}>
                              {rewrite.status === "published" ? "✅ 已发布" : "📝 草稿"}
                            </span>
                            {rewrite.angle && (
                              <span className="px-2.5 py-1 bg-blue-50 text-blue-600 rounded-lg text-xs font-medium">
                                🎯 {rewrite.angle}
                              </span>
                            )}
                            {rewrite.targetAudience && (
                              <span className="px-2.5 py-1 bg-purple-50 text-purple-600 rounded-lg text-xs font-medium">
                                👥 {rewrite.targetAudience}
                              </span>
                            )}
                          </div>
                          <h3 className="font-semibold text-gray-800 mb-2">{rewrite.title}</h3>
                          <p className="text-gray-500 text-sm line-clamp-2">{rewrite.body}</p>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <button className="p-2.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button className="p-2.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-xl transition">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                          <button className="p-2.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 弹窗 */}
      <AddAccountForm isOpen={showAddAccount} onClose={() => setShowAddAccount(false)} onSubmit={handleAddAccount} />
      <AddContentForm isOpen={showAddContent} onClose={() => setShowAddContent(false)} onSubmit={handleAddContent} accounts={accounts} />
      <AnalysisForm isOpen={showAnalysis} onClose={() => setShowAnalysis(false)} onSubmit={handleAnalysis} content={selectedContent} />
      <RewriteForm isOpen={showRewrite} onClose={() => setShowRewrite(false)} onSubmit={handleRewrite} content={selectedContent} />

      {/* 内容详情抽屉 */}
      <ContentDetail
        isOpen={showDetail}
        onClose={() => setShowDetail(false)}
        content={selectedContent}
        onAnalyze={() => { setShowDetail(false); setShowAnalysis(true); }}
        onRewrite={() => { setShowDetail(false); setShowRewrite(true); }}
      />
    </main>
  );
}

function StatCard({ icon, title, value, trend, gradient }: { icon: string; title: string; value: number; trend: string; gradient: string }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-xl hover:shadow-gray-200/50 hover:-translate-y-1 transition-all cursor-pointer">
      <div className="flex items-start justify-between">
        <div className={`w-12 h-12 bg-gradient-to-br ${gradient} rounded-xl flex items-center justify-center shadow-lg`}>
          <span className="text-xl filter drop-shadow text-white">{icon}</span>
        </div>
        <span className="text-xs text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full font-medium">{trend}</span>
      </div>
      <div className="mt-4">
        <div className="text-3xl font-bold text-gray-800">{value}</div>
        <div className="text-sm text-gray-400 mt-1">{title}</div>
      </div>
    </div>
  );
}
