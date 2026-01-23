"use client";

import { useState } from "react";
import { Modal, Textarea, Button } from "./ui";

interface AnalysisFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AnalysisFormData) => void;
  content: { id: string; title: string } | null;
}

export interface AnalysisFormData {
  contentId: string;
  hookAnalysis?: string;
  structureAnalysis?: string;
  emotionAnalysis?: string;
  ctaAnalysis?: string;
  keyTakeaways?: string;
}

export function AnalysisForm({ isOpen, onClose, onSubmit, content }: AnalysisFormProps) {
  const [form, setForm] = useState<Omit<AnalysisFormData, "contentId">>({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content) return;
    setLoading(true);
    await onSubmit({ ...form, contentId: content.id });
    setLoading(false);
    setForm({});
    onClose();
  };

  if (!content) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`拆解分析：${content.title}`}>
      <form onSubmit={handleSubmit}>
        <Textarea
          label="开头钩子分析"
          value={form.hookAnalysis || ""}
          onChange={(e) => setForm({ ...form, hookAnalysis: e.target.value })}
          placeholder="分析开头如何吸引注意力..."
        />
        <Textarea
          label="内容结构分析"
          value={form.structureAnalysis || ""}
          onChange={(e) => setForm({ ...form, structureAnalysis: e.target.value })}
          placeholder="分析内容的组织结构..."
        />
        <Textarea
          label="情绪点分析"
          value={form.emotionAnalysis || ""}
          onChange={(e) => setForm({ ...form, emotionAnalysis: e.target.value })}
          placeholder="分析哪些点引发共鸣..."
        />
        <Textarea
          label="行动号召分析"
          value={form.ctaAnalysis || ""}
          onChange={(e) => setForm({ ...form, ctaAnalysis: e.target.value })}
          placeholder="分析如何引导用户行动..."
        />
        <Textarea
          label="核心要点总结"
          value={form.keyTakeaways || ""}
          onChange={(e) => setForm({ ...form, keyTakeaways: e.target.value })}
          placeholder="总结可复用的要点..."
        />
        <div className="flex justify-end space-x-2 mt-4">
          <Button type="button" variant="secondary" onClick={onClose}>取消</Button>
          <Button type="submit" loading={loading}>保存分析</Button>
        </div>
      </form>
    </Modal>
  );
}
