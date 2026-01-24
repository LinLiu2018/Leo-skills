# WeChat Mini-program Specification

> **Usage**: Load this template for Mobile Agent tasks (Page/Component generation).

## 1. Directory Structure (Standard)
```
miniprogram/
  ├── components/       # Global components
  │   └── [comp-name]/
  ├── pages/            # Page logic
  │   └── [page-name]/
  │       ├── index.js
  │       ├── index.json
  │       ├── index.wxml
  │       └── index.wxss
  ├── utils/            # Utilities
  ├── app.js
  └── app.json
```

## 2. Naming Conventions
- **Files**: snake_case (e.g., `user_profile.js`) or kebab-case.
- **Components**: PascalCase in usage (e.g., `<UserProfile />`).
- **Classes**: BEM naming convention (e.g., `block__element--modifier`).

## 3. UI Guidelines (Vant Weapp)
- Use **Vant Weapp** for standard components.
- Primary Color: `#1989fa` (Default Blue).
- Font Size: 14px (Base), 16px (Title).

## 4. API Handling
- Use `wx.request` wrapper (e.g., `utils/request.js`).
- Base URL must be configured in `app.js`.

## 5. Security
- Use HTTPS only.
- Do not store secrets in frontend code.
