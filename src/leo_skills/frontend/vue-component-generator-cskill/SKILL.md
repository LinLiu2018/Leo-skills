# Vue3组件生成器 Skill

## 技能描述

生成Vue3组件代码，支持Composition API和TypeScript。

## 激活词

- "生成Vue组件"
- "创建Vue组件"
- "Vue3组件"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| component_name | string | 是 | 组件名称（PascalCase） |
| props | list | 否 | 属性定义列表 |
| emits | list | 否 | 事件列表 |
| slots | list | 否 | 插槽列表 |
| features | list | 否 | 特性（loading/lifecycle/computed/watch） |

## 输出

- `ComponentName.vue` - Vue组件文件
- `ComponentName.types.ts` - TypeScript类型定义
- `ComponentName.spec.ts` - 单元测试文件
- `index.ts` - 导出文件

## 使用示例

### 示例1：基础组件

```
生成Vue组件
组件名：UserCard
属性：name(string), avatar(string), role(string)
```

### 示例2：带事件的组件

```
生成Vue组件
组件名：DataTable
属性：data(array), columns(array)
事件：row-click, page-change
特性：loading, pagination
```

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-14
