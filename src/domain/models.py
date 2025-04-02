"""
領域模型 - 定義應用程式所需的核心資料結構
"""
from dataclasses import dataclass
from typing import Any

@dataclass
class SheetData:
    """Google Sheets 資料模型"""
    headers: list[str]
    rows: list[list[Any]]
    
    @property
    def row_count(self) -> int:
        """獲取資料行數"""
        return len(self.rows)
    
    def to_dict_list(self) -> list[dict[str, Any]]:
        """將原始資料轉換為字典列表格式以便於渲染"""
        result = []
        for row in self.rows:
            # 確保行長度與標題相符
            if len(row) != len(self.headers):
                continue
                
            row_dict = {self.headers[i]: row[i] for i in range(len(self.headers))}
            result.append(row_dict)
        return result 