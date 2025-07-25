"""
VisionBlock 使用範例

此檔案展示如何在 AgentSociety-CP 中使用 VisionBlock 進行影像處理
"""

import asyncio
import os
from pathlib import Path

# 假設的導入路徑（實際使用時需要調整）
from packages.agentsociety.agentsociety.cityagent.blocks.vision_block import VisionBlock
from packages.agentsociety.agentsociety.cityagent.societyagent import SocietyAgent
from packages.agentsociety.agentsociety.agent import AgentToolbox, MemoryAttribute

# 範例 1: 基本的 VisionBlock 使用
async def basic_vision_example():
    """基本的視覺處理範例"""
    
    # 創建必要的組件（實際使用時這些會由系統提供）
    toolbox = AgentToolbox()  # 實際需要正確初始化
    memory = Memory()  # 實際需要正確初始化
    
    # 創建 VisionBlock
    vision_block = VisionBlock(
        toolbox=toolbox,
        agent_memory=memory,
        max_image_size=(800, 600)  # 自定義影像大小限制
    )
    
    # 模擬代理上下文
    context = {
        "current_step": {
            "intention": "請分析這張照片 '/path/to/image.jpg'"
        },
        "current_position": "在家",
    }
    
    # 執行視覺分析
    try:
        result = await vision_block.forward(context)
        
        print("=== 視覺分析結果 ===")
        print(f"成功: {result.success}")
        print(f"影像路徑: {result.image_path}")
        print(f"場景描述: {result.image_description}")
        print(f"檢測物體: {result.objects_detected}")
        print(f"場景類型: {result.scene_type}")
        print(f"處理時間: {result.consumed_time} 分鐘")
        
    except Exception as e:
        print(f"視覺分析失敗: {str(e)}")

# 範例 2: 整合到 SocietyAgent 中
class VisionEnhancedAgent(SocietyAgent):
    """增強了視覺能力的社會代理"""
    
    # 添加視覺相關的記憶體屬性
    StatusAttributes = SocietyAgent.StatusAttributes + [
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
            description="視覺記憶列表",
        ),
        MemoryAttribute(
            name="last_analyzed_image",
            type=str,
            default_or_value="",
            description="最後分析的影像路徑",
        ),
        MemoryAttribute(
            name="preferred_image_types",
            type=list,
            default_or_value=["nature", "people", "objects"],
            description="偏好的影像類型",
        ),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 創建並註冊 VisionBlock
        self.vision_block = VisionBlock(
            toolbox=self._toolbox,
            agent_memory=self.memory,
        )
        
        # 註冊到調度器
        self.dispatcher.register_blocks([self.vision_block])
    
    async def analyze_environment_visually(self, image_path: str) -> dict:
        """分析環境的視覺方法
        
        Args:
            image_path: 要分析的影像路徑
            
        Returns:
            dict: 分析結果
        """
        context = {
            "current_step": {
                "intention": f"分析環境影像 '{image_path}'"
            },
            "current_position": await self.status.get("position", "unknown"),
        }
        
        result = await self.vision_block.forward(context)
        
        return {
            "success": result.success,
            "description": result.image_description,
            "objects": result.objects_detected,
            "scene_type": result.scene_type,
        }

# 範例 3: 批量影像處理
async def batch_image_processing_example():
    """批量處理多張影像的範例"""
    
    # 假設的影像檔案列表
    image_files = [
        "/path/to/image1.jpg",
        "/path/to/image2.png", 
        "/path/to/image3.jpg",
    ]
    
    # 創建視覺增強代理
    agent = VisionEnhancedAgent(
        id=1,
        name="視覺代理",
        toolbox=toolbox,  # 需要正確初始化
        memory=memory,    # 需要正確初始化
    )
    
    results = []
    
    for image_path in image_files:
        if os.path.exists(image_path):
            try:
                result = await agent.analyze_environment_visually(image_path)
                results.append({
                    "image": image_path,
                    "result": result
                })
                print(f"✓ 已處理: {os.path.basename(image_path)}")
                
            except Exception as e:
                print(f"✗ 處理失敗 {os.path.basename(image_path)}: {str(e)}")
        else:
            print(f"⚠ 檔案不存在: {image_path}")
    
    return results

# 範例 4: 視覺記憶查詢
async def visual_memory_query_example():
    """查詢視覺記憶的範例"""
    
    agent = VisionEnhancedAgent(...)  # 初始化代理
    
    # 查詢所有視覺記憶
    visual_memories = await agent.memory.status.get("visual_memories", [])
    
    print("=== 視覺記憶查詢 ===")
    for i, memory in enumerate(visual_memories):
        print(f"{i+1}. 影像: {memory.get('path', 'unknown')}")
        print(f"   描述: {memory.get('description', 'no description')[:50]}...")
        print(f"   時間: {memory.get('timestamp', 'unknown')}")
        print()
    
    # 查詢特定場景類型的記憶
    outdoor_memories = []
    for memory in visual_memories:
        # 這裡需要實際的記憶體查詢機制
        if "outdoor" in memory.get('description', '').lower():
            outdoor_memories.append(memory)
    
    print(f"找到 {len(outdoor_memories)} 個戶外場景記憶")

# 範例 5: 錯誤處理和容錯機制
async def error_handling_example():
    """錯誤處理和容錯機制範例"""
    
    vision_block = VisionBlock(toolbox, memory)
    
    # 測試各種錯誤情況
    test_cases = [
        {
            "name": "不存在的檔案",
            "context": {
                "current_step": {
                    "intention": "分析影像 '/nonexistent/image.jpg'"  
                }
            }
        },
        {
            "name": "不支援的格式",
            "context": {
                "current_step": {
                    "intention": "分析影像 '/path/to/document.pdf'"
                }
            }
        },
        {
            "name": "沒有影像路徑",
            "context": {
                "current_step": {
                    "intention": "我想要看一些圖片"
                }
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n測試案例: {case['name']}")
        try:
            result = await vision_block.forward(case['context'])
            print(f"結果: {'成功' if result.success else '失敗'}")
            print(f"評估: {result.evaluation}")
            
        except Exception as e:
            print(f"異常: {str(e)}")

# 主要執行函數
async def main():
    """主要範例執行函數"""
    
    print("=== VisionBlock 使用範例 ===\n")
    
    # 執行基本範例
    print("1. 基本視覺處理範例")
    await basic_vision_example()
    
    print("\n" + "="*50 + "\n")
    
    # 執行批量處理範例  
    print("2. 批量影像處理範例")
    await batch_image_processing_example()
    
    print("\n" + "="*50 + "\n")
    
    # 執行視覺記憶查詢範例
    print("3. 視覺記憶查詢範例")
    await visual_memory_query_example()
    
    print("\n" + "="*50 + "\n")
    
    # 執行錯誤處理範例
    print("4. 錯誤處理範例")
    await error_handling_example()

# 輔助工具函數
def setup_test_environment():
    """設置測試環境"""
    
    # 創建測試影像檔案（如果不存在）
    test_images_dir = Path("test_images")
    test_images_dir.mkdir(exist_ok=True)
    
    # 這裡可以創建一些測試影像檔案
    # 或者下載範例影像
    
    return test_images_dir

if __name__ == "__main__":
    # 設置測試環境
    test_dir = setup_test_environment()
    
    # 執行範例
    asyncio.run(main())