# GeoVisionBlock 地理視覺整合指南

## 📋 概述

本指南說明如何將 GeoVisionBlock（地理視覺處理區塊）整合到 AgentSociety-CP 系統中，讓代理具備結合地理位置的影像讀取、分析和空間理解能力。

## 🎯 GeoVisionBlock 功能特性

### 核心功能
- **影像讀取**: 支援多種格式 (JPG, PNG, BMP, GIF, TIFF, WebP)
- **GPS提取**: 自動從影像EXIF數據提取地理坐標
- **位置關聯**: 結合代理當前位置和AOI信息
- **地理分析**: 使用 LLM 進行地理語境化的影像理解
- **空間語義**: 理解場景的地理意義和空間關係
- **位置驗證**: 驗證影像位置與代理位置的一致性
- **軌跡記錄**: 記錄代理的視覺-地理移動軌跡

### 地理功能特點
- **多源定位**: 支援GPS、代理位置、AOI等多種位置來源
- **空間分析**: 計算距離、查詢附近AOI、分析空間關係
- **位置精度**: 評估不同位置來源的精度和可信度
- **地理上下文**: 構建豐富的地理環境描述
- **空間記憶**: 將地理視覺信息整合到記憶體系統

### 技術特點
- **自動路徑提取**: 從代理意圖中智能提取影像路徑
- **EXIF解析**: 自動解析影像的GPS元數據
- **坐標轉換**: 支援不同坐標系統間的轉換
- **空間計算**: 使用Haversine公式計算球面距離
- **錯誤容錯**: 完善的錯誤處理和後備機制
- **記憶體整合**: 與代理記憶體系統無縫整合

## 🔧 安裝和配置

### Step 1: 檢查依賴套件

確保系統已安裝必要的 Python 套件：

```bash
pip install Pillow  # 影像處理
pip install base64  # Base64 編碼（通常內建）
```

### Step 2: 部署 GeoVisionBlock 檔案

將更新的 `vision_block.py` 檔案放置到正確位置：

```
packages/agentsociety/agentsociety/cityagent/blocks/vision_block.py
```

### Step 3: 更新模組匯出

修改 `blocks/__init__.py` 檔案：

```python
from .cognition_block import CognitionBlock
from .economy_block import EconomyBlock
from .mobility_block import MobilityBlock
from .needs_block import NeedsBlock
from .other_block import OtherBlock
from .plan_block import PlanBlock
from .social_block import SocialBlock
from .vision_block import GeoVisionBlock  # 新增這行

__all__ = [
    "MobilityBlock",
    "CognitionBlock", 
    "PlanBlock",
    "NeedsBlock",
    "SocialBlock",
    "EconomyBlock",
    "OtherBlock",
    "GeoVisionBlock",  # 新增這行
]
```

### Step 4: 更新代理記憶體配置

在 `SocietyAgent` 中添加視覺相關的記憶體屬性：

```python
class SocietyAgent(CitizenAgentBase):
    StatusAttributes = [
        # 現有屬性...
        
        # 視覺相關屬性
        MemoryAttribute(
            name="visual_processing_skill",
            type=float,
            default_or_value=0.7,
            description="代理的視覺處理能力, 0-1",
        ),
        MemoryAttribute(
            name="visual_memories",
            type=list,
            default_or_value=[],
            description="視覺記憶列表，儲存最近分析的影像信息",
        ),
        MemoryAttribute(
            name="last_analyzed_image",
            type=str,
            default_or_value="",
            description="最後分析的影像檔案路徑",
        ),
        MemoryAttribute(
            name="last_scene_type",
            type=str,
            default_or_value="",
            description="最後識別的場景類型",
        ),
        MemoryAttribute(
            name="current_image_path",
            type=str,
            default_or_value="",
            description="當前要處理的影像路徑",
        ),
    ]
```

### Step 5: 註冊 VisionBlock 到代理

修改 `SocietyAgent` 的初始化方法：

```python
from .blocks import VisionBlock  # 新增導入

class SocietyAgent(CitizenAgentBase):
    def __init__(self, ...):
        super().__init__(...)
        
        # 創建 VisionBlock 實例
        self.vision_block = VisionBlock(
            toolbox=self._toolbox,
            agent_memory=self.memory,
            max_image_size=(1024, 1024)  # 可自定義影像大小限制
        )
        
        # 將 VisionBlock 加入到 blocks 列表
        if blocks is None:
            blocks = []
        blocks.append(self.vision_block)
        
        # 註冊到調度器（通常自動處理）
        self.dispatcher.register_blocks([self.vision_block])
```

## 🚀 使用方法

### 基本使用範例

```python
# 代理接收包含影像路徑的意圖
intention = "請幫我分析這張照片 '/Users/user/photos/vacation.jpg'"

# 系統會自動：
# 1. BlockDispatcher 識別這是視覺相關任務
# 2. 選擇 VisionBlock 處理
# 3. VisionBlock 提取影像路徑
# 4. 載入和分析影像
# 5. 返回分析結果
```

### 支援的意圖格式

VisionBlock 可以處理以下類型的意圖：

```python
intentions = [
    "分析影像 '/path/to/image.jpg'",
    "看看這張照片 'C:\\Users\\photos\\image.png'",
    "請描述圖片 './relative/path/image.jpeg'",
    "幫我理解這個場景 '/home/user/scene.bmp'",
    "分析環境照片 '/data/images/environment.tiff'"
]
```

### 程式化使用

```python
# 直接設置影像路徑到代理狀態
await agent.memory.status.update("current_image_path", "/path/to/image.jpg")

# 然後發送視覺分析意圖
await agent.memory.status.update("current_plan", {
    "steps": [{"intention": "分析當前影像"}],
    "index": 0
})

# 執行代理行為
result = await agent.forward()
```

## 📊 輸出格式

VisionBlock 返回 `VisionBlockOutput` 格式：

```python
{
    "success": bool,                    # 執行是否成功
    "evaluation": str,                  # 簡短評估描述
    "consumed_time": int,               # 處理時間（分鐘）
    "node_id": str,                     # 記憶體節點ID
    "image_path": str,                  # 處理的影像路徑
    "image_description": str,           # 詳細影像描述
    "objects_detected": List[str],      # 檢測到的物體列表
    "scene_type": str,                  # 場景類型
    "visual_memory_id": str             # 視覺記憶ID
}
```

## 🔍 進階配置

### 自定義 LLM 提示

```python
CUSTOM_VISION_PROMPT = """
作為專業的影像分析師，請詳細分析提供的影像。

分析重點：
- 技術品質（清晰度、構圖、光線）
- 藝術價值（美感、創意、表現力）
- 實用信息（時間、地點、人物、活動）

當前任務: ${context.current_step.intention}

請提供專業的分析報告...
"""

vision_block = VisionBlock(
    toolbox=toolbox,
    agent_memory=memory,
    vision_prompt=CUSTOM_VISION_PROMPT
)
```

### 影像處理設定

```python
# 創建具有自定義設定的 VisionBlock
vision_block = VisionBlock(
    toolbox=toolbox,
    agent_memory=memory,
    max_image_size=(512, 512),  # 較小的影像尺寸以提高處理速度
)

# 或使用輔助函數
from vision_block import create_vision_block_with_custom_settings

vision_block = create_vision_block_with_custom_settings(
    toolbox=toolbox,
    memory=memory,
    supported_formats={'.jpg', '.png'},  # 只支援特定格式
    max_image_size=(2048, 2048)          # 支援更大的影像
)
```

## 🧪 測試和驗證

### 單元測試

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from vision_block import VisionBlock

@pytest.mark.asyncio
async def test_vision_block_basic():
    # 模擬依賴
    toolbox = MagicMock()
    toolbox.llm.atext_request = AsyncMock(
        return_value='{"description": "一張美麗的風景照", "objects": ["樹木", "天空"], "scene_type": "自然風景"}'
    )
    
    memory = MagicMock()
    memory.status.get = AsyncMock(return_value=[])
    memory.status.update = AsyncMock()
    memory.stream.add = AsyncMock(return_value="vision_node_123")
    
    # 創建測試實例
    vision_block = VisionBlock(toolbox=toolbox, agent_memory=memory)
    
    # 模擬測試影像存在
    import os
    os.path.exists = MagicMock(return_value=True)
    
    # 模擬上下文
    context = {
        "current_step": {"intention": "分析影像 '/test/image.jpg'"}
    }
    
    # 執行測試
    result = await vision_block.forward(context)
    
    # 驗證結果
    assert result.success == True
    assert result.image_path == "/test/image.jpg"
    assert "風景" in result.image_description
```

### 整合測試

```python
async def test_vision_integration():
    """測試 VisionBlock 在完整系統中的整合"""
    
    # 創建包含 VisionBlock 的代理
    agent = SocietyAgent(
        id=1,
        name="視覺測試代理",
        toolbox=toolbox,
        memory=memory,
        blocks=[VisionBlock(toolbox, memory)]
    )
    
    # 設置測試影像
    test_image_path = "/path/to/test_image.jpg"
    await agent.memory.status.update("current_image_path", test_image_path)
    
    # 設置視覺分析任務
    await agent.memory.status.update("current_plan", {
        "steps": [{"intention": f"分析影像 '{test_image_path}'"}],
        "index": 0
    })
    
    # 執行代理
    result = await agent.forward()
    
    # 驗證整合結果
    visual_memories = await agent.memory.status.get("visual_memories")
    assert len(visual_memories) > 0
    assert visual_memories[-1]["path"] == test_image_path
```

## ⚠️ 注意事項和限制

### LLM 支援要求

- **視覺模型**: 需要支援視覺分析的 LLM（如 GPT-4V、Claude 3 等）
- **API 配置**: 確保 LLM 客戶端正確配置視覺功能
- **Token 限制**: 注意影像處理會消耗較多 Token

### 影像處理限制

- **檔案大小**: 建議影像檔案小於 20MB
- **解析度**: 系統會自動調整過大的影像
- **格式支援**: 目前支援常見的點陣圖格式，不支援向量圖

### 安全考量

- **路徑驗證**: 系統會驗證影像路徑的安全性
- **檔案存取**: 確保代理有適當的檔案讀取權限
- **隱私保護**: 處理敏感影像時需要額外注意

### 性能考量

- **處理時間**: 視覺分析通常需要較長時間
- **記憶體使用**: 大影像會佔用較多記憶體
- **併發限制**: 避免同時處理過多影像

## 🔧 故障排除

### 常見問題

1. **影像載入失敗**
   ```python
   # 檢查影像路徑和權限
   import os
   print(f"檔案存在: {os.path.exists(image_path)}")
   print(f"檔案權限: {os.access(image_path, os.R_OK)}")
   ```

2. **LLM 不支援視覺**
   ```python
   # 檢查 LLM 配置
   if not hasattr(llm, 'supports_vision'):
       print("LLM 可能不支援視覺功能")
   ```

3. **記憶體不足**
   ```python
   # 調整影像大小限制
   vision_block = VisionBlock(
       toolbox=toolbox,
       agent_memory=memory,
       max_image_size=(512, 512)  # 較小的尺寸
   )
   ```

### 除錯模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# VisionBlock 會輸出詳細的除錯信息
```

## 📚 更多資源

- [AgentSociety-CP 官方文檔](./docs/)
- [Block 系統架構說明](./agent_architecture_diagram.md)
- [如何新增 Block 指南](./HOW_TO_ADD_NEW_BLOCK.md)
- [使用範例檔案](./vision_block_example.py)

---

**版本**: v1.0  
**最後更新**: 2024年  
**維護者**: AgentSociety-CP 開發團隊

如有問題或需要協助，請參考系統文檔或聯繫開發團隊。