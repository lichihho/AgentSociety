---
title: 技術架構
description: "定義專案的技術棧、架構模式和開發實踐。"
inclusion: always
---

# 技術架構

## 核心技術棧

### 後端技術
- **Python 3.11+**：主要開發語言
- **FastAPI**：Web 框架和 API 服務
- **SQLAlchemy**：ORM 和數據庫抽象層
- **AsyncPG/AIOSQLite**：異步數據庫連接
- **Ray**：分佈式計算和多處理
- **gRPC**：微服務間通信
- **Pydantic**：數據驗證和序列化

### 前端技術
- **React 18**：前端框架
- **TypeScript**：型別安全的 JavaScript
- **Ant Design**：UI 組件庫
- **Vite**：構建工具和開發服務器
- **Deck.gl**：地理資訊視覺化
- **Mapbox GL**：地圖渲染引擎
- **MobX**：狀態管理

### 數據庫和存儲
- **PostgreSQL**：主要關聯型數據庫
- **SQLite**：輕量級數據庫（開發環境）
- **Qdrant**：向量數據庫（用於語義搜尋）
- **S3**：物件存儲服務

### AI/ML 技術
- **OpenAI API**：大型語言模型整合
- **支援多種 LLM**：Qwen、Deepseek 等
- **HuggingFace**：模型和嵌入向量服務
- **FastEmbed**：快速嵌入向量生成

## 架構模式

### 多層架構設計

1. **模型層 (Model Layer)**
   - 代理配置管理
   - 任務定義和執行控制
   - 日誌設定和結果聚合

2. **代理層 (Agent Layer)**
   - 多頭工作流管理
   - 記憶系統（靜態資料、工作記憶）
   - 推理塊、路由塊、行動塊

3. **訊息層 (Message Layer)**
   - P2P、P2G 和群組聊天
   - 訊息攔截和處理
   - 異步訊息傳遞

4. **環境層 (Environment Layer)**
   - 環境感知和互動處理
   - 城市地圖和交通系統整合
   - 訊息管理

5. **LLM 層**
   - 多模型支援和配置
   - 提示工程和執行監控
   - API 調用管理

6. **工具層 (Tool Layer)**
   - 字串處理和數據分析
   - 存儲和檢索機制
   - 排序和搜尋功能

## 開發工具和實踐

### 構建和包管理
- **UV**：現代 Python 包管理器
- **Hatchling**：Python 包構建後端
- **pnpm/npm**：前端包管理（推測）

### 程式碼品質
- **Ruff**：Python 程式碼格式化和檢查
- **ESLint**：JavaScript/TypeScript 程式碼檢查
- **TypeScript**：靜態型別檢查

### 容器化和部署
- **Docker**：容器化部署
- **Kubernetes**：容器編排（商業版）
- **Docker Compose**：本地開發環境

### 開發環境
- **Jupyter**：互動式開發和實驗
- **Monaco Editor**：瀏覽器內程式碼編輯
- **Vite HMR**：熱重載開發

## 專案結構模式

### 單體倉庫 (Monorepo)
- 使用 UV workspace 管理多個 Python 包
- 前端和後端代碼分離但統一管理
- 共享依賴和工具配置

### 包組織
```
packages/
├── agentsociety/           # 核心框架
├── agentsociety-community/ # 社區版本
└── agentsociety-benchmark/ # 基準測試
```

## API 設計原則

### RESTful API
- 遵循 REST 架構原則
- 使用 HTTP 狀態碼表示操作結果
- JSON 格式數據交換

### 異步優先
- 使用 asyncio 進行異步處理
- 支援高並發請求
- 非阻塞 I/O 操作

### 型別安全
- Pydantic 模型驗證
- TypeScript 前端型別定義
- 自動 API 文檔生成

## 效能考慮

### 擴展性設計
- Ray 框架支援分佈式計算
- 異步數據庫操作
- 快取策略優化

### 監控和日誌
- 結構化日誌記錄
- 效能指標收集
- 錯誤追蹤和報告

## 安全實踐

### 認證和授權
- Casdoor 集成 SSO
- JWT Token 驗證
- 角色基礎存取控制

### 數據保護
- 敏感資訊加密
- 安全的 API 端點
- 輸入驗證和清理