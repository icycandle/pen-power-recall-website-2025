"""
領域模型單元測試
"""
import unittest
from src.domain.models import SheetData


class TestSheetData(unittest.TestCase):
    """SheetData 模型單元測試"""
    
    def test_init(self):
        """測試初始化"""
        headers = ["標題", "作者", "連結"]
        rows = [
            ["測試標題1", "測試作者1", "https://example.com/1"],
            ["測試標題2", "測試作者2", "https://example.com/2"]
        ]
        
        data = SheetData(headers=headers, rows=rows)
        
        self.assertEqual(data.headers, headers)
        self.assertEqual(data.rows, rows)
    
    def test_row_count(self):
        """測試 row_count 屬性"""
        data = SheetData(
            headers=["標題", "作者", "連結"],
            rows=[
                ["測試標題1", "測試作者1", "https://example.com/1"],
                ["測試標題2", "測試作者2", "https://example.com/2"],
                ["測試標題3", "測試作者3", "https://example.com/3"]
            ]
        )
        
        self.assertEqual(data.row_count, 3)
        
        # 測試空資料
        empty_data = SheetData(headers=[], rows=[])
        self.assertEqual(empty_data.row_count, 0)
    
    def test_to_dict_list(self):
        """測試 to_dict_list 方法"""
        data = SheetData(
            headers=["標題", "作者", "連結"],
            rows=[
                ["測試標題1", "測試作者1", "https://example.com/1"],
                ["測試標題2", "測試作者2", "https://example.com/2"]
            ]
        )
        
        result = data.to_dict_list()
        expected = [
            {"標題": "測試標題1", "作者": "測試作者1", "連結": "https://example.com/1"},
            {"標題": "測試標題2", "作者": "測試作者2", "連結": "https://example.com/2"}
        ]
        
        self.assertEqual(result, expected)
    
    def test_to_dict_list_with_uneven_rows(self):
        """測試 to_dict_list 處理長度不一致的資料行"""
        data = SheetData(
            headers=["標題", "作者", "連結"],
            rows=[
                ["測試標題1", "測試作者1"],  # 缺少連結
                ["測試標題2", "測試作者2", "https://example.com/2", "多餘資料"],  # 多出一項
                ["測試標題3", "測試作者3", "https://example.com/3"]  # 正常
            ]
        )
        
        result = data.to_dict_list()
        
        # 檢查結果的結構而不是具體內容
        self.assertEqual(len(result), 1)  # 只有長度匹配的行
        self.assertIn("標題", result[0])
        self.assertIn("作者", result[0])
        self.assertIn("連結", result[0])
        self.assertTrue(any(row["標題"] == "測試標題3" for row in result))
    
    def test_to_dict_list_empty(self):
        """測試 to_dict_list 處理空資料"""
        # 空標頭
        data1 = SheetData(headers=[], rows=[["資料"]])
        self.assertEqual(data1.to_dict_list(), [])
        
        # 空資料
        data2 = SheetData(headers=["標題"], rows=[])
        self.assertEqual(data2.to_dict_list(), [])
                         
        # 完全空
        data3 = SheetData(headers=[], rows=[])
        self.assertEqual(data3.to_dict_list(), []) 