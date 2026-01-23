"use client";

import { useState } from "react";
import { Modal, Input, Textarea, Button } from "./ui";

interface RewriteFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: RewriteFormData) => void;
  content: { id: string; title: string } | null;
}

export interface RewriteFormData {
  contentId: string;
  title: string;
  body: string;
  angle?: string;
  targetAudience?: string;
}

export function RewriteForm({ isOpen, onClose, onSubmit, content }: RewriteFormProps) {
  const [form, setForm] = useState<Omit<RewriteFormData, "contentId">>({ title: "", body: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content) return;
    setLoading(true);
    await onSubmit({ ...form, contentId: content.id });
    setLoading(false);
    setForm({ title: "", body: "" });
    onClose();
  };

  if (!content) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`仿写：${content.title}`}>
      <form onSubmit={handleSubmit}>
        <Input
          label="仿写标题"
          required
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          placeholder="你的标题"
        />
        <Textarea
          label="仿写正文"
          required
          value={form.body}
          onChange={(e) => setForm({ ...form, body: e.target.value })}
          placeholder="你的内容..."
          rows={8}
        />
        <Input
          label="切入角度（选填）"
          value={form.angle || ""}
          onChange={(e) => setForm({ ...form, angle: e.target.value })}
          placeholder="如：宁波本地化、商铺投资"
        />
        <Input
          label="目标受众（选填）"
          value={form.targetAudience || ""}
          onChange={(e) => setForm({ ...form, targetAudience: e.target.value })}
          placeholder="如：宁波购房者、商铺投资者"
        />
        <div className="flex justify-end space-x-2 mt-4">
          <Button type="button" variant="secondary" onClick={onClose}>取消</Button>
          <Button type="submit" loading={loading}>保存仿写</Button>
        </div>
      </form>
    </Modal>
  );
}
