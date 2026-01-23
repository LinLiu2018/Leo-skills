import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "content-benchmark",
  description: "Created with T3 Stack",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
