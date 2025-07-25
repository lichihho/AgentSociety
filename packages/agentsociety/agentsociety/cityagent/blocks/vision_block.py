"""
地理視覺處理 Block - 處理影像讀取、分析和地理定位相關活動

此模組提供代理的視覺和地理感知能力，包括：
- 影像讀取和載入
- 影像內容分析和描述  
- 場景理解和物體識別
- 地理坐標關聯和位置記錄
- 視覺記憶儲存和檢索
- 空間語義理解
"""

import base64
import io
import os
from typing import Any, Optional, List, Tuple, Dict
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import json_repair
import datetime

from ...agent import (
    AgentToolbox,
    Block,
    FormatPrompt,
    DotDict,
)
from ...logger import get_logger
from ...memory import Memory
from ..sharing_params import SocietyAgentBlockOutput
from pydantic import BaseModel, Field

class GeographicLocation(BaseModel):
    """地理位置信息"""
    latitude: Optional[float] = Field(description="緯度")
    longitude: Optional[float] = Field(description="經度")
    altitude: Optional[float] = Field(description="海拔高度")
    accuracy: Optional[float] = Field(description="定位精度（米）")
    source: str = Field(description="位置來源：gps/agent/aoi/manual")
    aoi_id: Optional[int] = Field(description="關聯的AOI ID")
    aoi_name: Optional[str] = Field(description="AOI名稱")
    address: Optional[str] = Field(description="地址描述")
    timestamp: Optional[str] = Field(description="位置記錄時間")

class VisionBlockOutput(SocietyAgentBlockOutput):
    """地理視覺處理 Block 的輸出格式"""
    image_path: str = Field(description="處理的影像路徑")
    image_description: str = Field(description="影像內容描述")
    objects_detected: List[str] = Field(description="檢測到的物體列表")
    scene_type: str = Field(description="場景類型")
    geographic_location: Optional[GeographicLocation] = Field(description="地理位置信息")
    spatial_context: str = Field(description="空間上下文描述")
    visual_memory_id: Optional[str] = Field(description="視覺記憶ID")
    location_relevance: str = Field(description="位置相關性分析")

# LLM 地理視覺分析提示模板
GEO_VISION_ANALYSIS_PROMPT = """
作為一個智能代理的地理視覺系統，請分析提供的影像並結合地理位置信息提供詳細描述。

=== 代理狀態信息 ===
當前意圖: ${context.current_step.intention}
當前位置: ${context.current_position}
當前情感: ${status.emotion_types}
代理坐標: ${geographic_info.agent_coordinates}
當前AOI: ${geographic_info.current_aoi}

=== 地理上下文 ===
拍攝位置: ${geographic_info.image_location}
周邊AOI: ${geographic_info.nearby_aois}
地理環境: ${geographic_info.geographic_context}

請綜合分析影像內容和地理位置信息，提供以下詳細分析：

1. **視覺內容分析**
   - 整體場景描述
   - 主要物體、建築、人物
   - 場景類型（室內/室外、商業/住宅/自然等）
   - 環境特徵（天氣、光線、時間推測等）

2. **地理空間分析**
   - 場景與已知地理位置的一致性
   - 可識別的地理標誌或地標
   - 空間方向和視角分析
   - 與周邊AOI的關聯性

3. **語義理解**
   - 場景的功能和用途
   - 可能的活動類型
   - 社會和文化背景
   - 時間和季節特徵

4. **位置驗證**
   - 影像內容是否與GPS位置匹配
   - 可見地標是否與已知位置一致
   - 環境特徵是否符合地理預期

請以 JSON 格式回應：
{
    "description": "結合地理位置的詳細影像描述",
    "objects": ["物體1", "建築2", "地標3"],
    "scene_type": "場景類型",
    "geographic_consistency": "地理一致性評估",
    "spatial_landmarks": ["可識別的地標或特徵"],
    "location_confidence": 0.8,
    "spatial_context": "空間上下文描述",
    "functional_analysis": "場景功能分析",
    "temporal_indicators": "時間特徵指標",
    "relevance_to_intention": "與當前意圖的關聯性",
    "location_relevance": "位置相關性分析"
}
"""

class GeoVisionBlock(Block):
    """處理代理的地理視覺相關活動
    
    此 Block 負責管理代理的視覺和地理感知能力，包括：
    - 讀取和載入各種格式的影像
    - 提取影像EXIF地理標籤信息
    - 結合代理當前位置進行空間分析
    - 使用 LLM 進行地理語境化的影像分析
    - 關聯AOI和地理坐標信息
    - 將地理視覺信息儲存到記憶體系統
    - 處理空間語義理解和位置驗證
    """
    
    # 必要的類別屬性
    name = "GeoVisionBlock"
    description = "Handles geographic image analysis combining visual understanding with spatial location data, GPS coordinates, and AOI information"
    OutputType = VisionBlockOutput
    
    # 支援的影像格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    # 定義此 Block 可處理的動作類型
    actions = {
        "geo_image_analysis": "結合地理位置的影像分析",
        "spatial_scene_understanding": "空間場景理解和定位",
        "location_verification": "位置驗證和一致性檢查",
        "geographic_context_analysis": "地理上下文分析"
    }
    
    def __init__(
        self,
        toolbox: AgentToolbox,
        agent_memory: Memory,
        vision_prompt: str = GEO_VISION_ANALYSIS_PROMPT,
        max_image_size: tuple = (1024, 1024),
        location_accuracy_threshold: float = 100.0,  # 位置精度閾值（米）
    ):
        """初始化 GeoVisionBlock
        
        Args:
            toolbox: 代理工具箱，包含 LLM、環境等
            agent_memory: 代理記憶體系統
            vision_prompt: 地理視覺分析的 LLM 提示模板
            max_image_size: 最大影像尺寸限制 (width, height)
            location_accuracy_threshold: 位置精度閾值（米）
        """
        super().__init__(
            toolbox=toolbox,
            agent_memory=agent_memory,
        )
        self.geo_vision_prompt = FormatPrompt(
            template=vision_prompt,
            memory=agent_memory,
        )
        self.max_image_size = max_image_size
        self.location_accuracy_threshold = location_accuracy_threshold
    
    def _extract_gps_from_exif(self, image_path: str) -> Optional[Tuple[float, float, float]]:
        """從影像EXIF數據中提取GPS坐標
        
        Args:
            image_path: 影像檔案路徑
            
        Returns:
            Optional[Tuple[float, float, float]]: (緯度, 經度, 海拔) 或 None
        """
        try:
            with Image.open(image_path) as img:
                exifdata = img.getexif()
                
                if not exifdata:
                    return None
                
                gps_info = {}
                for tag_id in exifdata:
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "GPSInfo":
                        gps_data = exifdata[tag_id]
                        for gps_tag_id in gps_data:
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_info[gps_tag] = gps_data[gps_tag_id]
                
                if not gps_info:
                    return None
                
                # 解析GPS坐標
                def convert_to_degrees(value):
                    d, m, s = value
                    return d + (m / 60.0) + (s / 3600.0)
                
                latitude = None
                longitude = None
                altitude = None
                
                if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                    latitude = convert_to_degrees(gps_info['GPSLatitude'])
                    if gps_info['GPSLatitudeRef'] == 'S':
                        latitude = -latitude
                
                if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                    longitude = convert_to_degrees(gps_info['GPSLongitude'])
                    if gps_info['GPSLongitudeRef'] == 'W':
                        longitude = -longitude
                
                if 'GPSAltitude' in gps_info:
                    altitude = float(gps_info['GPSAltitude'])
                    if gps_info.get('GPSAltitudeRef', 0) == 1:
                        altitude = -altitude
                
                if latitude is not None and longitude is not None:
                    return (latitude, longitude, altitude)
                
                return None
                
        except Exception as e:
            get_logger().warning(f"無法提取EXIF GPS信息: {str(e)}")
            return None
    
    async def _get_agent_current_location(self) -> Optional[GeographicLocation]:
        """獲取代理當前的地理位置信息
        
        Returns:
            Optional[GeographicLocation]: 代理當前位置信息
        """
        try:
            # 從代理狀態獲取位置信息
            position = await self.memory.status.get("position", {})
            
            # 獲取AOI位置信息
            aoi_position = position.get("aoi_position")
            xy_position = position.get("xy_position")
            
            if aoi_position:
                aoi_id = aoi_position.get("aoi_id")
                # 從環境系統獲取AOI詳細信息
                if hasattr(self.environment, 'get_aoi_info'):
                    aoi_info = await self.environment.get_aoi_info(aoi_id)
                    if aoi_info:
                        return GeographicLocation(
                            latitude=aoi_info.get("center_lat"),
                            longitude=aoi_info.get("center_lng"),
                            accuracy=50.0,  # AOI中心點精度
                            source="aoi",
                            aoi_id=aoi_id,
                            aoi_name=aoi_info.get("name", f"AOI_{aoi_id}"),
                            timestamp=datetime.datetime.now().isoformat()
                        )
            
            # 如果有XY坐標，嘗試轉換為地理坐標
            if xy_position and hasattr(self.environment, 'map'):
                try:
                    # 這裡需要根據實際的地圖投影進行坐標轉換
                    x, y = xy_position.get("x"), xy_position.get("y")
                    if x is not None and y is not None:
                        # 假設環境有坐標轉換方法
                        if hasattr(self.environment.map, 'xy_to_latlng'):
                            lat, lng = self.environment.map.xy_to_latlng(x, y)
                            return GeographicLocation(
                                latitude=lat,
                                longitude=lng,
                                accuracy=10.0,  # XY坐標精度較高
                                source="agent",
                                timestamp=datetime.datetime.now().isoformat()
                            )
                except Exception as e:
                    get_logger().warning(f"坐標轉換失敗: {str(e)}")
            
            return None
            
        except Exception as e:
            get_logger().error(f"獲取代理位置失敗: {str(e)}")
            return None
    
    async def _get_nearby_aois(self, location: GeographicLocation, radius: float = 500.0) -> List[Dict]:
        """獲取指定位置附近的AOI信息
        
        Args:
            location: 中心位置
            radius: 搜索半徑（米）
            
        Returns:
            List[Dict]: 附近的AOI信息列表
        """
        try:
            if not location.latitude or not location.longitude:
                return []
            
            nearby_aois = []
            
            # 如果環境系統支援空間查詢
            if hasattr(self.environment, 'query_nearby_aois'):
                nearby_aois = await self.environment.query_nearby_aois(
                    location.latitude, 
                    location.longitude, 
                    radius
                )
            
            return nearby_aois
            
        except Exception as e:
            get_logger().warning(f"查詢附近AOI失敗: {str(e)}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """計算兩點間的距離（米）
        
        使用Haversine公式計算球面距離
        """
        try:
            import math
            
            R = 6371000  # 地球半徑（米）
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = (math.sin(delta_lat / 2) ** 2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * 
                 math.sin(delta_lon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            return R * c
            
        except Exception:
            return float('inf')
    
    async def _build_geographic_context(self, image_location: Optional[GeographicLocation], 
                                      agent_location: Optional[GeographicLocation]) -> Dict[str, Any]:
        """構建地理上下文信息
        
        Args:
            image_location: 影像拍攝位置
            agent_location: 代理當前位置
            
        Returns:
            Dict[str, Any]: 地理上下文信息
        """
        context = {
            "agent_coordinates": "未知",
            "current_aoi": "未知",
            "image_location": "未知",
            "nearby_aois": "無",
            "geographic_context": "無地理信息",
            "distance_from_agent": None
        }
        
        try:
            # 代理位置信息
            if agent_location:
                if agent_location.latitude and agent_location.longitude:
                    context["agent_coordinates"] = f"({agent_location.latitude:.6f}, {agent_location.longitude:.6f})"
                if agent_location.aoi_name:
                    context["current_aoi"] = agent_location.aoi_name
            
            # 影像位置信息
            if image_location:
                if image_location.latitude and image_location.longitude:
                    context["image_location"] = f"({image_location.latitude:.6f}, {image_location.longitude:.6f})"
                    
                    # 計算與代理的距離
                    if agent_location and agent_location.latitude and agent_location.longitude:
                        distance = self._calculate_distance(
                            agent_location.latitude, agent_location.longitude,
                            image_location.latitude, image_location.longitude
                        )
                        context["distance_from_agent"] = f"{distance:.0f}米"
                    
                    # 獲取附近AOI
                    nearby_aois = await self._get_nearby_aois(image_location)
                    if nearby_aois:
                        aoi_names = [aoi.get("name", f"AOI_{aoi.get('id')}") for aoi in nearby_aois[:5]]
                        context["nearby_aois"] = ", ".join(aoi_names)
            
            # 構建地理環境描述
            context_parts = []
            if context["agent_coordinates"] != "未知":
                context_parts.append(f"代理位於 {context['agent_coordinates']}")
            if context["current_aoi"] != "未知":
                context_parts.append(f"當前在 {context['current_aoi']}")
            if context["image_location"] != "未知":
                context_parts.append(f"影像拍攝於 {context['image_location']}")
            if context["distance_from_agent"]:
                context_parts.append(f"距離代理 {context['distance_from_agent']}")
            
            if context_parts:
                context["geographic_context"] = "；".join(context_parts)
            
        except Exception as e:
            get_logger().warning(f"構建地理上下文失敗: {str(e)}")
        
        return context
    
    def _validate_image_path(self, image_path: str) -> bool:
        """驗證影像路徑和格式
        
        Args:
            image_path: 影像檔案路徑
            
        Returns:
            bool: 路徑和格式是否有效
        """
        if not os.path.exists(image_path):
            get_logger().warning(f"影像檔案不存在: {image_path}")
            return False
            
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            get_logger().warning(f"不支援的影像格式: {file_ext}")
            return False
            
        return True
    
    def _load_and_process_image(self, image_path: str) -> Optional[str]:
        """載入和處理影像，轉換為 base64 編碼
        
        Args:
            image_path: 影像檔案路徑
            
        Returns:
            Optional[str]: base64 編碼的影像數據，失敗返回 None
        """
        try:
            # 載入影像
            with Image.open(image_path) as img:
                # 轉換為 RGB 模式（如果需要）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 調整影像大小（如果超過限制）
                if img.size[0] > self.max_image_size[0] or img.size[1] > self.max_image_size[1]:
                    img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                    get_logger().info(f"影像已調整大小至: {img.size}")
                
                # 轉換為 base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return img_base64
                
        except Exception as e:
            get_logger().error(f"影像處理失敗: {str(e)}")
            return None
    
    def _extract_image_path_from_intention(self, intention: str) -> Optional[str]:
        """從意圖描述中提取影像路徑
        
        Args:
            intention: 代理的意圖描述
            
        Returns:
            Optional[str]: 提取的影像路徑，未找到返回 None
        """
        # 常見的路徑提取模式
        import re
        
        # 匹配常見的檔案路徑格式
        path_patterns = [
            r'["\']([^"\']*\.(?:jpg|jpeg|png|bmp|gif|tiff|webp))["\']',  # 引號包圍的路徑
            r'(/[^\s]*\.(?:jpg|jpeg|png|bmp|gif|tiff|webp))',            # Unix 路徑
            r'([A-Za-z]:[^\s]*\.(?:jpg|jpeg|png|bmp|gif|tiff|webp))',   # Windows 路徑
            r'(\.?/[^\s]*\.(?:jpg|jpeg|png|bmp|gif|tiff|webp))',        # 相對路徑
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, intention, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    async def forward(self, context: DotDict) -> VisionBlockOutput:
        """執行地理視覺處理活動
        
        Args:
            context: 代理上下文，包含當前步驟和計劃信息
            
        Returns:
            VisionBlockOutput: 包含影像分析結果、地理位置和視覺記憶信息
        """
        try:
            intention = context.get("current_step", {}).get("intention", "")
            get_logger().info(f"GeoVisionBlock 處理意圖: {intention}")
            
            # 1. 從意圖中提取影像路徑
            image_path = self._extract_image_path_from_intention(intention)
            
            if not image_path:
                # 如果無法從意圖提取路徑，嘗試從代理狀態獲取
                image_path = await self.memory.status.get("current_image_path", "")
            
            if not image_path:
                raise ValueError("未找到要處理的影像路徑")
            
            # 驗證影像路徑
            if not self._validate_image_path(image_path):
                raise ValueError(f"無效的影像路徑或格式: {image_path}")
            
            # 2. 提取地理位置信息
            # 從影像EXIF提取GPS信息
            gps_coords = self._extract_gps_from_exif(image_path)
            image_location = None
            
            if gps_coords:
                lat, lng, alt = gps_coords
                image_location = GeographicLocation(
                    latitude=lat,
                    longitude=lng,
                    altitude=alt,
                    accuracy=5.0,  # GPS精度通常較高
                    source="gps",
                    timestamp=datetime.datetime.now().isoformat()
                )
                get_logger().info(f"從影像EXIF提取GPS坐標: ({lat:.6f}, {lng:.6f})")
            
            # 獲取代理當前位置
            agent_location = await self._get_agent_current_location()
            
            # 如果影像沒有GPS信息，使用代理當前位置作為估計
            if not image_location and agent_location:
                image_location = GeographicLocation(
                    latitude=agent_location.latitude,
                    longitude=agent_location.longitude,
                    altitude=agent_location.altitude,
                    accuracy=agent_location.accuracy + 20.0,  # 降低精度表示估計
                    source="agent_estimated",
                    aoi_id=agent_location.aoi_id,
                    aoi_name=agent_location.aoi_name,
                    timestamp=datetime.datetime.now().isoformat()
                )
            
            # 3. 構建地理上下文
            geographic_context = await self._build_geographic_context(image_location, agent_location)
            
            # 4. 載入和處理影像
            img_base64 = self._load_and_process_image(image_path)
            if not img_base64:
                raise ValueError("影像載入失敗")
            
            # 5. 格式化地理視覺分析提示
            await self.geo_vision_prompt.format(
                context=context,
                geographic_info=geographic_context
            )
            
            # 準備包含影像的訊息
            vision_messages = self.geo_vision_prompt.to_dialog()
            
            # 在最後一個用戶訊息中添加影像
            if vision_messages and vision_messages[-1]["role"] == "user":
                vision_messages[-1]["content"] = [
                    {"type": "text", "text": vision_messages[-1]["content"]},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}",
                            "detail": "high"
                        }
                    }
                ]
            
            # 6. 調用 LLM 進行地理視覺分析
            result = await self.llm.atext_request(
                vision_messages,
                response_format={"type": "json_object"}
            )
            
            # 7. 解析分析結果
            analysis = json_repair.loads(result)
            description = analysis.get("description", "無法分析影像內容")
            objects = analysis.get("objects", [])
            scene_type = analysis.get("scene_type", "未知場景")
            geographic_consistency = analysis.get("geographic_consistency", "無法評估")
            spatial_landmarks = analysis.get("spatial_landmarks", [])
            location_confidence = analysis.get("location_confidence", 0.5)
            spatial_context = analysis.get("spatial_context", "無空間上下文")
            functional_analysis = analysis.get("functional_analysis", "")
            temporal_indicators = analysis.get("temporal_indicators", "")
            relevance = analysis.get("relevance_to_intention", "")
            location_relevance = analysis.get("location_relevance", "")
            
            # 8. 儲存地理視覺記憶
            geo_visual_memory_content = f"""
地理視覺分析結果:
- 檔案路徑: {image_path}
- 場景描述: {description}
- 檢測物體: {', '.join(objects)}
- 場景類型: {scene_type}
- 空間地標: {', '.join(spatial_landmarks)}
- 地理一致性: {geographic_consistency}
- 位置信心度: {location_confidence}
- 空間上下文: {spatial_context}
- 功能分析: {functional_analysis}
- 時間指標: {temporal_indicators}
- 位置相關性: {location_relevance}
"""
            
            if image_location:
                geo_visual_memory_content += f"""
- 拍攝坐標: ({image_location.latitude:.6f}, {image_location.longitude:.6f})
- 位置來源: {image_location.source}
- 位置精度: {image_location.accuracy}m
"""
            
            if geographic_context["distance_from_agent"]:
                geo_visual_memory_content += f"- 距離代理: {geographic_context['distance_from_agent']}\n"
            
            node_id = await self.memory.stream.add(
                topic="geo_vision",
                description=geo_visual_memory_content
            )
            
            # 9. 更新代理的地理視覺狀態
            await self.memory.status.update("last_analyzed_image", image_path)
            await self.memory.status.update("last_scene_type", scene_type)
            await self.memory.status.update("last_image_location", 
                                           image_location.model_dump() if image_location else None)
            
            # 更新地理視覺記憶列表
            geo_visual_memories = await self.memory.status.get("geo_visual_memories", [])
            memory_entry = {
                "path": image_path,
                "description": description,
                "location": image_location.model_dump() if image_location else None,
                "spatial_context": spatial_context,
                "timestamp": self.environment.get_datetime()[1],
                "memory_id": node_id,
                "location_confidence": location_confidence
            }
            geo_visual_memories.append(memory_entry)
            await self.memory.status.update("geo_visual_memories", geo_visual_memories[-15:])  # 保留最近15個
            
            # 10. 如果位置精度較高，觸發認知更新
            if location_confidence > 0.7 and hasattr(self, 'agent'):
                try:
                    location_thought = f"在{geographic_context.get('geographic_context', '某處')}觀察到{scene_type}場景"
                    await self.agent.save_agent_thought(location_thought)
                except Exception as e:
                    get_logger().warning(f"無法保存地理認知: {str(e)}")
            
            get_logger().info(f"GeoVisionBlock 成功分析影像: {os.path.basename(image_path)}")
            
            return VisionBlockOutput(
                success=True,
                evaluation=f"地理視覺分析: {description[:50]}...",
                consumed_time=45,  # 地理視覺分析需要更多時間
                node_id=node_id,
                image_path=image_path,
                image_description=description,
                objects_detected=objects,
                scene_type=scene_type,
                geographic_location=image_location,
                spatial_context=spatial_context,
                visual_memory_id=node_id,
                location_relevance=location_relevance
            )
            
        except Exception as e:
            get_logger().error(f"GeoVisionBlock 執行錯誤: {str(e)}")
            
            # 提供後備方案
            fallback_path = context.get("current_step", {}).get("intention", "unknown_image")
            node_id = await self.memory.stream.add(
                topic="geo_vision",
                description=f"嘗試進行地理視覺分析但遇到錯誤: {str(e)}"
            )
            
            return VisionBlockOutput(
                success=False,
                evaluation=f"地理視覺分析失敗: {str(e)[:30]}",
                consumed_time=10,
                node_id=node_id,
                image_path=fallback_path,
                image_description="無法分析影像內容",
                objects_detected=[],
                scene_type="未知",
                geographic_location=None,
                spatial_context="無地理上下文",
                visual_memory_id=node_id,
                location_relevance="無法評估位置相關性"
            
            # 提供後備方案
            fallback_path = context.get("current_step", {}).get("intention", "unknown_image")
            node_id = await self.memory.stream.add(
                topic="vision",
                description=f"嘗試進行視覺分析但遇到錯誤: {str(e)}"
            )
            
            return VisionBlockOutput(
                success=False,
                evaluation=f"視覺分析失敗: {str(e)[:30]}",
                consumed_time=5,
                node_id=node_id,
                image_path=fallback_path,
                image_description="無法分析影像內容",
                objects_detected=[],
                scene_type="未知",
                visual_memory_id=node_id
            )
    
    async def before_forward(self):
        """前置處理 - 準備視覺處理環境"""
        # 檢查 LLM 是否支援視覺功能
        if not hasattr(self.llm, 'supports_vision') or not self.llm.supports_vision:
            get_logger().warning("當前 LLM 可能不支援視覺分析功能")
        
        # 確保視覺記憶結構存在
        visual_memories = await self.memory.status.get("visual_memories", None)
        if visual_memories is None:
            await self.memory.status.update("visual_memories", [])
    
    async def after_forward(self):
        """後置處理 - 清理臨時資源"""
        # 清理可能的臨時檔案或緩存
        # 這裡可以添加清理邏輯
        pass

# 輔助函數
def create_vision_block_with_custom_settings(
    toolbox: AgentToolbox,
    memory: Memory,
    supported_formats: Optional[set] = None,
    max_image_size: tuple = (1024, 1024)
) -> VisionBlock:
    """創建具有自定義設定的 VisionBlock
    
    Args:
        toolbox: 代理工具箱
        memory: 代理記憶體
        supported_formats: 支援的影像格式集合
        max_image_size: 最大影像尺寸
        
    Returns:
        VisionBlock: 配置好的視覺處理 Block
    """
    block = VisionBlock(toolbox, memory, max_image_size=max_image_size)
    
    if supported_formats:
        block.SUPPORTED_FORMATS = supported_formats
    
    return block