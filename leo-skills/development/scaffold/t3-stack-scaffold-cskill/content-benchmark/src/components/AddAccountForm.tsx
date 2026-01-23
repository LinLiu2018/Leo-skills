"use client";

import { useState } from "react";
import { Modal, Input, Select, Textarea, Button } from "./ui";

const PLATFORMS = [
  { value: "小红书", label: "小红书" },
  { value: "抖音", label: "抖音" },
  { value: "公众号", label: "公众号" },
  { value: "视频号", label: "视频号" },
  { value: "B站", label: "B站" },
  { value: "快手", label: "快手" },
];

const CATEGORIES = [
  { value: "房产", label: "房产" },
  { value: "商业地产", label: "商业地产" },
  { value: "美食", label: "美食" },
  { value: "旅游", label: "旅游" },
  { value: "生活", label: "生活" },
  { value: "其他", label: "其他" },
];

interface AddAccountFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AccountFormData) => void;
}

export interface AccountFormData {
  platform: string;
  accountName: string;
  accountId?: string;
  followers?: number;
  category: string;
  style?: string;
  notes?: string;
}

export function AddAccountForm({ isOpen, onClose, onSubmit }: AddAccountFormProps) {
  const [form, setForm] = useState<AccountFormData>({
    platform: "小红书",
    accountName: "",
    category: "房产",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(form);
    setLoading(false);
    setForm({ platform: "小红书", accountName: "", category: "房产" });
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="添加对标账号">
      <form onSubmit={handleSubmit}>
        <Select
          label="平台"
          options={PLATFORMS}
          value={form.platform}
          onChange={(e) => setForm({ ...form, platform: e.target.value })}
        />
        <Input
          label="账号名称"
          required
          value={form.accountName}
          onChange={(e) => setForm({ ...form, accountName: e.target.value })}
          placeholder="输入账号名称"
        />
        <Input
          label="账号ID（选填）"
          value={form.accountId || ""}
          onChange={(e) => setForm({ ...form, accountId: e.target.value })}
          placeholder="账号唯一标识"
        />
        <Input
          label="粉丝数（选填）"
          type="number"
          value={form.followers || ""}
          onChange={(e) => setForm({ ...form, followers: Number(e.target.value) || undefined })}
          placeholder="粉丝数量"
        />
        <Select
          label="领域"
          options={CATEGORIES}
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
        />
        <Input
          label="风格特点（选填）"
          value={form.style || ""}
          onChange={(e) => setForm({ ...form, style: e.target.value })}
          placeholder="如：接地气、专业、幽默"
        />
        <Textarea
          label="备注（选填）"
          value={form.notes || ""}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
          placeholder="其他备注信息"
        />
        <div className="flex justify-end space-x-2 mt-4">
          <Button type="button" variant="secondary" onClick={onClose}>取消</Button>
          <Button type="submit" loading={loading}>添加</Button>
        </div>
      </form>
    </Modal>
  );
}
