---
title: 專案結構
description: "定義專案的檔案組織、命名慣例和架構規範。"
inclusion: always
---

# 專案結構

## 整體組織架構

AgentSociety 採用單體倉庫 (Monorepo) 結構，使用 UV workspace 管理多個相關套件。

```
AgentSociety-CP/
├── .ai-rules/              # AI 助手指導文件
├── packages/               # 核心套件目錄
│   ├── agentsociety/       # 主要框架套件
│   ├── agentsociety-community/  # 社區版本
│   └── agentsociety-benchmark/  # 基準測試套件
├── frontend/               # React 前端應用
├── docs/                   # 專案文檔
├── examples/               # 範例程式和配置
├── dev-docs/              # 開發者文檔
├── scripts/               # 構建和部署腳本
└── static/                # 靜態資源
```

## 核心套件結構

### packages/agentsociety/ (主要框架)

```
agentsociety/
├── agentsociety/
│   ├── agent/              # 代理核心模組
│   │   ├── agent.py        # 主要代理類別
│   │   ├── agent_base.py   # 代理基底類別
│   │   ├── block.py        # 執行塊定義
│   │   ├── context.py      # 上下文管理
│   │   ├── memory_config_generator.py  # 記憶配置生成器
│   │   └── toolbox.py      # 工具箱功能
│   ├── cityagent/          # 城市代理專門化
│   │   ├── blocks/         # 各種行為塊
│   │   │   ├── cognition_block.py    # 認知塊
│   │   │   ├── economy_block.py      # 經濟塊
│   │   │   ├── mobility_block.py     # 移動塊
│   │   │   ├── needs_block.py        # 需求塊
│   │   │   ├── plan_block.py         # 規劃塊
│   │   │   ├── social_block.py       # 社交塊
│   │   │   └── vision_block.py       # 視覺塊
│   │   ├── societyagent.py    # 社會代理
│   │   ├── bankagent.py       # 銀行代理
│   │   └── governmentagent.py # 政府代理
│   ├── environment/        # 環境管理
│   │   ├── sim/            # 模擬服務
│   │   ├── economy/        # 經濟系統
│   │   └── utils/          # 環境工具
│   ├── webapi/             # Web API 服務
│   │   ├── api/            # API 端點
│   │   └── models/         # 數據模型
│   ├── simulation/         # 模擬引擎
│   ├── storage/            # 數據存儲
│   ├── llm/               # LLM 整合
│   └── configs/           # 配置管理
└── pyproject.toml         # 套件配置
```

## 前端結構

### frontend/ (React 應用)

```
frontend/
├── src/
│   ├── components/         # 可重用組件
│   │   ├── Auth.tsx        # 認證組件
│   │   ├── Editor.ts       # 編輯器組件
│   │   └── MonacoPromptEditor.tsx  # Monaco 編輯器
│   ├── pages/             # 頁面組件
│   │   ├── Agent/         # 代理管理頁面
│   │   ├── Experiment/    # 實驗管理頁面
│   │   ├── Home/          # 首頁
│   │   ├── Map/           # 地圖視覺化
│   │   └── Replay/        # 重播功能
│   ├── i18n/              # 國際化
│   │   └── locales/       # 語言文件
│   │       ├── en/        # 英文
│   │       └── zh/        # 中文
│   ├── types/             # TypeScript 型別定義
│   └── utils/             # 工具函數
├── public/                # 靜態資源
└── package.json           # 前端依賴配置
```

## 文檔結構

### docs/ (專案文檔)

```
docs/
├── 01-quick-start/        # 快速開始指南
├── 02-version-1.5/        # 版本更新說明
├── 03-configurations/     # 配置說明
├── 04-experiment-design/  # 實驗設計
├── 05-custom-agents/      # 客製化代理
├── 06-webui/             # Web 介面說明
├── 07-use-case/          # 使用案例
├── 08-advanced-usage/    # 進階用法
├── _static/              # 文檔靜態資源
└── apidocs/              # API 文檔
```

## 範例和開發文檔

### examples/ (範例程式)

```
examples/
├── UBI/                   # 基本收入實驗
├── hurricane_impact/      # 颶風影響模擬
├── inflammatory_message/  # 煽動性訊息研究
├── polarization/          # 極化現象研究
├── prospect_theory/       # 前景理論實驗
└── config_templates/      # 配置範本
```

### dev-docs/ (開發者文檔)

```
dev-docs/
├── HOW_TO_ADD_NEW_BLOCK.md      # 新增區塊指南
├── agent_architecture_diagram.md # 代理架構圖表
├── VISION_BLOCK_INTEGRATION_GUIDE.md # 視覺區塊整合指南
└── *.py                         # 範例程式碼
```

## 命名慣例

### Python 檔案和模組
- **檔案名稱**：使用 snake_case（如：`agent_base.py`）
- **類別名稱**：使用 PascalCase（如：`SocietyAgent`）
- **函數和變數**：使用 snake_case（如：`get_memory_config`）
- **常數**：使用 UPPER_SNAKE_CASE（如：`DEFAULT_CONFIG`）

### TypeScript/React 檔案
- **檔案名稱**：使用 PascalCase 或 camelCase（如：`AgentTemplate.tsx`）
- **組件名稱**：使用 PascalCase（如：`MonacoPromptEditor`）
- **函數和變數**：使用 camelCase（如：`getCurrentAgent`）

### 目錄結構規則
- **套件目錄**：使用 kebab-case（如：`agentsociety-community`）
- **模組目錄**：使用 snake_case（如：`city_agent`）
- **功能分組**：按功能領域組織（如：`blocks/`, `api/`, `models/`）

## 配置檔案組織

### 環境配置
- **開發環境**：`.env.development`
- **生產環境**：`.env.production`
- **範例配置**：`examples/config_templates/`

### 套件配置
- **Python 套件**：`pyproject.toml`
- **前端套件**：`package.json`
- **工作空間**：根目錄的 `pyproject.toml`

## 資源檔案管理

### 靜態資源
- **圖片和媒體**：`static/` 或 `public/`
- **圖標和 UI 資源**：`frontend/public/icon/`
- **文檔圖片**：`docs/_static/`

### 國際化資源
- **前端翻譯**：`frontend/src/i18n/locales/`
- **文檔多語言**：`docs/` 中的語言特定文件

## 測試檔案組織

雖然專案中沒有明顯的測試目錄，但建議的測試結構：

```
tests/
├── unit/              # 單元測試
├── integration/       # 整合測試
├── e2e/              # 端到端測試
└── fixtures/         # 測試數據和配置
```

## 部署和構建檔案

```
scripts/
├── build_docker.sh    # Docker 構建腳本
├── gen_docs.sh        # 文檔生成腳本
└── rebuild_frontend.sh # 前端重建腳本
```

## 新增功能的檔案放置規則

### 新增代理塊 (Agent Block)
- 核心塊：`packages/agentsociety/agentsociety/cityagent/blocks/`
- 社區塊：`packages/agentsociety-community/agentsociety_community/blocks/`

### 新增 API 端點
- API 實現：`packages/agentsociety/agentsociety/webapi/api/`
- 數據模型：`packages/agentsociety/agentsociety/webapi/models/`

### 新增前端頁面
- 頁面組件：`frontend/src/pages/[功能名稱]/`
- 共用組件：`frontend/src/components/`

### 新增實驗範例
- 範例程式：`examples/[實驗名稱]/`
- 配置範本：`examples/config_templates/`