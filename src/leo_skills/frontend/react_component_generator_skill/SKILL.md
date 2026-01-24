# React组件生成器 Skill

## 技能描述

生成React组件代码，支持Hooks和TypeScript。

## 激活词

- "生成React组件"
- "创建React组件"
- "React组件"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| component_name | string | 是 | 组件名称（PascalCase） |
| props | list | 否 | 属性定义列表 |
| hooks | list | 否 | 使用的hooks |
| features | list | 否 | 特性（loading/styled） |

## 输出

- `ComponentName.tsx` - React组件
- `ComponentName.types.ts` - TypeScript类型
- `ComponentName.test.tsx` - 测试文件
- `ComponentName.css` - 样式文件
- `index.ts` - 导出文件

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
