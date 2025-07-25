"""
GeoVisionBlock 地理視覺處理範例

此檔案展示如何在 AgentSociety-CP 中使用 GeoVisionBlock 進行影像和地理位置的結合分析
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any

# 假設的導入路徑（實際使用時需要調整）
from packages.agentsociety.agentsociety.cityagent.blocks.vision_block import GeoVisionBlock, GeographicLocation
from packages.agentsociety.agentsociety.cityagent.societyagent import SocietyAgent
from packages.agentsociety.agentsociety.agent import AgentToolbox, MemoryAttribute

# 範例 1: 基本的地理視覺分析
async def basic_geo_vision_example():
    """基本的地理視覺處理範例"""
    
    # 創建必要的組件（實際使用時這些會由系統提供）
    toolbox = AgentToolbox()  # 實際需要正確初始化
    memory = Memory()  # 實際需要正確初始化
    
    # 創建 GeoVisionBlock
    geo_vision_block = GeoVisionBlock(
        toolbox=toolbox,
        agent_memory=memory,
        max_image_size=(1024, 768),
        location_accuracy_threshold=50.0  # 50米精度閾值
    )
    
    # 模擬代理上下文
    context = {
        "current_step": {
            "intention": "請分析這張帶有GPS信息的照片 '/path/to/geo_image.jpg'"
        },
        "current_position": "台北市信義區",
    }
    
    # 執行地理視覺分析
    try:
        result = await geo_vision_block.forward(context)
        
        print("=== 地理視覺分析結果 ===")
        print(f"成功: {result.success}")
        print(f"影像路徑: {result.image_path}")
        print(f"場景描述: {result.image_description}")
        print(f"檢測物體: {result.objects_detected}")
        print(f"場景類型: {result.scene_type}")
        print(f"空間上下文: {result.spatial_context}")
        print(f"位置相關性: {result.location_relevance}")
        
        if result.geographic_location:
            loc = result.geographic_location
            print(f"\n=== 地理位置信息 ===")
            print(f"坐標: ({loc.latitude:.6f}, {loc.longitude:.6f})")
            print(f"海拔: {loc.altitude}m")
            print(f"精度: {loc.accuracy}m")
            print(f"位置來源: {loc.source}")
            print(f"AOI: {loc.aoi_name}")
            print(f"地址: {loc.address}")
        
        print(f"處理時間: {result.consumed_time} 分鐘")
        
    except Exception as e:
        print(f"地理視覺分析失敗: {str(e)}")

# 範例 2: 增強的地理感知代理
class GeoAwareAgent(SocietyAgent):
    """具備地理感知能力的社會代理"""
    
    # 添加地理視覺相關的記憶體屬性
    StatusAttributes = SocietyAgent.StatusAttributes + [
        MemoryAttribute(
            name="geo_visual_processing_skill",
            type=float,
            default_or_value=0.8,
            description="代理的地理視覺處理能力, 0-1",
        ),
        MemoryAttribute(
            name="geo_visual_memories",
            type=list,
            default_or_value=[],
            description="地理視覺記憶列表",
        ),
        MemoryAttribute(
            name="visited_locations",
            type=list,
            default_or_value=[],
            description="已訪問的地理位置列表",
        ),
        MemoryAttribute(
            name="spatial_knowledge",
            type=dict,
            default_or_value={},
            description="空間知識庫，記錄地點和特徵的關聯",
        ),
        MemoryAttribute(
            name="location_preferences",
            type=dict,
            default_or_value={"natural": 0.7, "urban": 0.6, "indoor": 0.5},
            description="對不同類型地點的偏好",
        ),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 創建並註冊 GeoVisionBlock
        self.geo_vision_block = GeoVisionBlock(
            toolbox=self._toolbox,
            agent_memory=self.memory,
        )
        
        # 註冊到調度器
        self.dispatcher.register_blocks([self.geo_vision_block])
    
    async def analyze_location_image(self, image_path: str, manual_location: GeographicLocation = None) -> Dict[str, Any]:
        """分析特定位置的影像
        
        Args:
            image_path: 要分析的影像路徑
            manual_location: 手動指定的位置信息（可選）
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        # 如果提供了手動位置，先設置到狀態中
        if manual_location:
            await self.memory.status.update("manual_image_location", manual_location.model_dump())
        
        context = {
            "current_step": {
                "intention": f"分析位置影像 '{image_path}'"
            },
            "current_position": await self.status.get("position", "unknown"),
        }
        
        result = await self.geo_vision_block.forward(context)
        
        # 更新空間知識
        if result.success and result.geographic_location:
            await self._update_spatial_knowledge(result)
        
        return {
            "success": result.success,
            "description": result.image_description,
            "objects": result.objects_detected,
            "scene_type": result.scene_type,
            "location": result.geographic_location.model_dump() if result.geographic_location else None,
            "spatial_context": result.spatial_context,
            "location_relevance": result.location_relevance,
        }
    
    async def _update_spatial_knowledge(self, vision_result):
        """更新代理的空間知識庫"""
        spatial_knowledge = await self.memory.status.get("spatial_knowledge", {})
        
        if vision_result.geographic_location:
            location_key = f"{vision_result.geographic_location.latitude:.4f},{vision_result.geographic_location.longitude:.4f}"
            
            if location_key not in spatial_knowledge:
                spatial_knowledge[location_key] = {
                    "scenes": [],
                    "objects": set(),
                    "visits": 0,
                    "first_seen": vision_result.geographic_location.timestamp
                }
            
            # 更新場景和物體信息
            spatial_knowledge[location_key]["scenes"].append(vision_result.scene_type)
            spatial_knowledge[location_key]["objects"].update(vision_result.objects_detected)
            spatial_knowledge[location_key]["visits"] += 1
            spatial_knowledge[location_key]["last_seen"] = vision_result.geographic_location.timestamp
            
            # 轉換 set 為 list 以便序列化
            spatial_knowledge[location_key]["objects"] = list(spatial_knowledge[location_key]["objects"])
            
            await self.memory.status.update("spatial_knowledge", spatial_knowledge)
    
    async def query_spatial_memories(self, location: GeographicLocation, radius: float = 100.0) -> List[Dict]:
        """查詢特定位置附近的視覺記憶
        
        Args:
            location: 中心位置
            radius: 搜索半徑（米）
            
        Returns:
            List[Dict]: 附近的視覺記憶列表
        """
        geo_visual_memories = await self.memory.status.get("geo_visual_memories", [])
        nearby_memories = []
        
        for memory in geo_visual_memories:
            if memory.get("location"):
                mem_lat = memory["location"]["latitude"]
                mem_lng = memory["location"]["longitude"]
                
                if mem_lat and mem_lng and location.latitude and location.longitude:
                    # 計算距離
                    distance = self.geo_vision_block._calculate_distance(
                        location.latitude, location.longitude,
                        mem_lat, mem_lng
                    )
                    
                    if distance <= radius:
                        memory["distance"] = distance
                        nearby_memories.append(memory)
        
        # 按距離排序
        nearby_memories.sort(key=lambda x: x.get("distance", float('inf')))
        return nearby_memories

# 範例 3: 地理軌跡分析
async def geographic_trajectory_analysis():
    """分析代理的地理移動軌跡"""
    
    agent = GeoAwareAgent(
        id=1,
        name="地理感知代理",
        toolbox=toolbox,  # 需要正確初始化
        memory=memory,    # 需要正確初始化
    )
    
    # 模擬一系列帶有地理位置的影像
    trajectory_images = [
        {
            "path": "/path/to/home_morning.jpg",
            "location": GeographicLocation(
                latitude=25.0330, longitude=121.5654,
                source="gps", aoi_name="住家附近"
            )
        },
        {
            "path": "/path/to/office_arrival.jpg", 
            "location": GeographicLocation(
                latitude=25.0478, longitude=121.5617,
                source="gps", aoi_name="辦公大樓"
            )
        },
        {
            "path": "/path/to/lunch_restaurant.jpg",
            "location": GeographicLocation(
                latitude=25.0465, longitude=121.5632,
                source="gps", aoi_name="餐廳"
            )
        }
    ]
    
    print("=== 地理軌跡分析 ===")
    
    for i, img_info in enumerate(trajectory_images):
        print(f"\n{i+1}. 分析影像: {os.path.basename(img_info['path'])}")
        
        try:
            result = await agent.analyze_location_image(
                img_info["path"], 
                img_info["location"]
            )
            
            if result["success"]:
                print(f"   位置: {img_info['location'].aoi_name}")
                print(f"   場景: {result['scene_type']}")
                print(f"   描述: {result['description'][:50]}...")
                print(f"   空間上下文: {result['spatial_context'][:50]}...")
            else:
                print(f"   分析失敗")
                
        except Exception as e:
            print(f"   錯誤: {str(e)}")
    
    # 查詢空間知識
    print(f"\n=== 累積的空間知識 ===")
    spatial_knowledge = await agent.memory.status.get("spatial_knowledge", {})
    for location_key, knowledge in spatial_knowledge.items():
        print(f"位置 {location_key}:")
        print(f"  訪問次數: {knowledge['visits']}")
        print(f"  場景類型: {set(knowledge['scenes'])}")
        print(f"  常見物體: {knowledge['objects'][:5]}")  # 只顯示前5個

# 範例 4: 位置驗證和一致性檢查
async def location_verification_example():
    """位置驗證和一致性檢查範例"""
    
    geo_vision_block = GeoVisionBlock(toolbox, memory)
    
    # 測試案例：影像GPS與代理位置的一致性
    test_cases = [
        {
            "name": "GPS與代理位置一致",
            "image_gps": (25.0330, 121.5654),
            "agent_location": GeographicLocation(
                latitude=25.0335, longitude=121.5650,
                source="agent", accuracy=10.0
            )
        },
        {
            "name": "GPS與代理位置相距較遠",
            "image_gps": (25.1000, 121.6000),
            "agent_location": GeographicLocation(
                latitude=25.0330, longitude=121.5654,
                source="agent", accuracy=10.0
            )
        }
    ]
    
    print("=== 位置驗證測試 ===")
    
    for case in test_cases:
        print(f"\n測試案例: {case['name']}")
        
        # 計算距離
        distance = geo_vision_block._calculate_distance(
            case["image_gps"][0], case["image_gps"][1],
            case["agent_location"].latitude, case["agent_location"].longitude
        )
        
        print(f"GPS坐標: {case['image_gps']}")
        print(f"代理位置: ({case['agent_location'].latitude}, {case['agent_location'].longitude})")
        print(f"距離: {distance:.0f}米")
        
        # 位置一致性判斷
        if distance <= 100:  # 100米內認為一致
            print("結果: ✓ 位置一致")
        elif distance <= 500:  # 500米內認為可能一致
            print("結果: ⚠ 位置可能一致")
        else:
            print("結果: ✗ 位置不一致")

# 範例 5: 空間語義理解
async def spatial_semantic_understanding():
    """空間語義理解範例"""
    
    agent = GeoAwareAgent(...)  # 初始化代理
    
    # 模擬不同類型的空間場景
    spatial_scenarios = [
        {
            "image": "/path/to/park_scene.jpg",
            "expected_semantics": ["自然環境", "休閒場所", "戶外活動"],
            "location_type": "公園"
        },
        {
            "image": "/path/to/office_building.jpg", 
            "expected_semantics": ["商業環境", "工作場所", "室內空間"],
            "location_type": "辦公大樓"
        },
        {
            "image": "/path/to/residential_area.jpg",
            "expected_semantics": ["住宅環境", "生活場所", "社區空間"], 
            "location_type": "住宅區"
        }
    ]
    
    print("=== 空間語義理解測試 ===")
    
    for scenario in spatial_scenarios:
        print(f"\n場景類型: {scenario['location_type']}")
        print(f"影像: {os.path.basename(scenario['image'])}")
        print(f"期望語義: {scenario['expected_semantics']}")
        
        # 這裡會實際執行地理視覺分析
        # result = await agent.analyze_location_image(scenario["image"])
        # 然後比較分析結果與期望語義的匹配度
        
        print("分析結果: [模擬] 符合預期語義")

# 主要執行函數
async def main():
    """主要範例執行函數"""
    
    print("=== GeoVisionBlock 地理視覺處理範例 ===\n")
    
    # 執行基本範例
    print("1. 基本地理視覺處理範例")
    await basic_geo_vision_example()
    
    print("\n" + "="*60 + "\n")
    
    # 執行地理軌跡分析範例  
    print("2. 地理軌跡分析範例")
    await geographic_trajectory_analysis()
    
    print("\n" + "="*60 + "\n")
    
    # 執行位置驗證範例
    print("3. 位置驗證範例")
    await location_verification_example()
    
    print("\n" + "="*60 + "\n")
    
    # 執行空間語義理解範例
    print("4. 空間語義理解範例")
    await spatial_semantic_understanding()

# 輔助工具函數
def create_test_image_with_gps(output_path: str, latitude: float, longitude: float):
    """創建帶有GPS信息的測試影像"""
    from PIL import Image
    from PIL.ExifTags import TAGS
    import piexif
    
    # 創建簡單的測試影像
    img = Image.new('RGB', (800, 600), color='blue')
    
    # 創建GPS EXIF數據
    def decimal_to_dms(decimal_degrees):
        """將十進制度數轉換為度分秒格式"""
        degrees = int(abs(decimal_degrees))
        minutes = int((abs(decimal_degrees) - degrees) * 60)
        seconds = int(((abs(decimal_degrees) - degrees) * 60 - minutes) * 60)
        return ((degrees, 1), (minutes, 1), (seconds, 1))
    
    # 構建GPS數據
    lat_dms = decimal_to_dms(latitude)
    lng_dms = decimal_to_dms(longitude)
    
    gps_dict = {
        "0": (2, 3, 0, 0),  # GPS版本
        "1": "N" if latitude >= 0 else "S",  # 緯度參考
        "2": lat_dms,  # 緯度
        "3": "E" if longitude >= 0 else "W",  # 經度參考
        "4": lng_dms,  # 經度
    }
    
    exif_dict = {"GPS": gps_dict}
    exif_bytes = piexif.dump(exif_dict)
    
    # 保存帶有GPS信息的影像
    img.save(output_path, exif=exif_bytes)
    print(f"已創建帶GPS信息的測試影像: {output_path}")

def setup_test_environment():
    """設置測試環境"""
    
    # 創建測試影像目錄
    test_images_dir = Path("test_geo_images")
    test_images_dir.mkdir(exist_ok=True)
    
    # 創建一些帶有GPS信息的測試影像
    test_locations = [
        ("taipei_101.jpg", 25.0330, 121.5654),  # 台北101
        ("national_palace_museum.jpg", 25.1023, 121.5488),  # 故宮博物院
        ("ximen_district.jpg", 25.0420, 121.5081),  # 西門町
    ]
    
    for filename, lat, lng in test_locations:
        image_path = test_images_dir / filename
        if not image_path.exists():
            try:
                create_test_image_with_gps(str(image_path), lat, lng)
            except ImportError:
                print(f"需要安裝 piexif 套件來創建帶GPS的測試影像: pip install piexif")
                break
    
    return test_images_dir

if __name__ == "__main__":
    # 設置測試環境
    test_dir = setup_test_environment()
    
    # 執行範例
    asyncio.run(main())