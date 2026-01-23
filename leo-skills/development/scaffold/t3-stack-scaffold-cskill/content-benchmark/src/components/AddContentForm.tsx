"use client";

import { useState } from "react";
import { Modal, Input, Select, Textarea, Button } from "./ui";

const CONTENT_TYPES = [
  { value: "短视频", label: "短视频" },
  { value: "图文", label: "图文" },
  { value: "文章", label: "文章" },
  { value: "直播切片", label: "直播切片" },
];

interface AddContentFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ContentFormData) => void;
  accounts: { id: string; accountName: string; platform: string }[];
}

export interface ContentFormData {
  accountId: string;
  title: string;
  content?: string;
  contentType: string;
  likes?: number;
  comments?: number;
  shares?: number;
  sourceUrl?: string;
}

export function AddContentForm({ isOpen, onClose, onSubmit, accounts }: AddContentFormProps) {
  const [form, setForm] = useState<ContentFormData>({
    accountId: accounts[0]?.id || "",
    title: "",
    contentType: "短视频",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(form);
    setLoading(false);
    setForm({ accountId: accounts[0]?.id || "", title: "", contentType: "短视频" });
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="收集爆款内容">
      <form onSubmit={handleSubmit}>
        <Select
          label="所属账号"
          options={accounts.map((a) => ({ value: a.id, label: `${a.platform} - ${a.accountName}` }))}
          value={form.accountId}
          onChange={(e) => setForm({ ...form, accountId: e.target.value })}
        />
        <Input
          label="标题"
          required
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          placeholder="爆款内容标题"
        />
        <Select
          label="内容类型"
          options={CONTENT_TYPES}
          value={form.contentType}
          onChange={(e) => setForm({ ...form, contentType: e.target.value })}
        />
        <Textarea
          label="内容正文（选填）"
          value={form.content || ""}
          onChange={(e) => setForm({ ...form, content: e.target.value })}
          placeholder="复制内容正文"
        />
        <div className="grid grid-cols-3 gap-2">
          <Input
            label="点赞数"
            type="number"
            value={form.likes || ""}
            onChange={(e) => setForm({ ...form, likes: Number(e.target.value) || undefined })}
          />
          <Input
            label="评论数"
            type="number"
            value={form.comments || ""}
            onChange={(e) => setForm({ ...form, comments: Number(e.target.value) || undefined })}
          />
          <Input
            label="分享数"
            type="number"
            value={form.shares || ""}
            onChange={(e) => setForm({ ...form, shares: Number(e.target.value) || undefined })}
          />
        </div>
        <Input
          label="原文链接（选填）"
          value={form.sourceUrl || ""}
          onChange={(e) => setForm({ ...form, sourceUrl: e.target.value })}
          placeholder="https://..."
        />
        <div className="flex justify-end space-x-2 mt-4">
          <Button type="button" variant="secondary" onClick={onClose}>取消</Button>
          <Button type="submit" loading={loading}>收集</Button>
        </div>
      </form>
    </Modal>
  );
}
