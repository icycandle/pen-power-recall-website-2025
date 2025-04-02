"""
HTML 產生器單元測試
"""
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.application.html_generator import HtmlGenerator
from src.domain.models import SheetData


class TestHtmlGenerator(unittest.TestCase):
    """HtmlGenerator 單元測試類"""
    
    def setUp(self):
        """設置測試環境"""
        # 創建臨時目錄作為輸出目錄
        self.test_output_dir = tempfile.mkdtemp()
        
        # 設置測試數據
        self.headers = ["標題", "作者", "連結", "電子郵件", "時間戳記"]
        self.rows = [
            ["測試標題1", "測試作者1", "https://example.com/1", "test1@example.com", "2023-01-01"],
            ["測試標題2", "測試作者2", "https://example.com/2", "test2@example.com", "2023-01-02"],
        ]
        self.data = SheetData(headers=self.headers, rows=self.rows)
        
        # 初始化 HTML 產生器
        self.generator = HtmlGenerator()
    
    def tearDown(self):
        """清理測試環境"""
        # 刪除臨時目錄
        shutil.rmtree(self.test_output_dir, ignore_errors=True)
    
    @patch('src.application.html_generator.Environment')
    def test_init(self, mock_environment):
        """測試初始化"""
        # 建立模擬環境
        mock_env = MagicMock()
        mock_environment.return_value = mock_env
        
        # 初始化新的產生器以測試初始化過程
        generator = HtmlGenerator()
        
        # 確認過濾器已設置
        self.assertTrue(hasattr(generator, 'env'))
        self.assertTrue(hasattr(generator, 'static_dir'))
    
    def test_filter_sensitive_data(self):
        """測試過濾敏感資料功能"""
        # 調用私有方法過濾敏感資料
        filtered_data = self.generator._filter_sensitive_data(self.data)
        
        # 確認電子郵件已被過濾
        self.assertEqual(filtered_data.headers, ["標題", "作者", "連結", "時間戳記"])
        for row in filtered_data.rows:
            self.assertEqual(len(row), 4)  # 原本有 5 項，現在應該只有 4 項
            self.assertNotIn("test1@example.com", row)
            self.assertNotIn("test2@example.com", row)
    
    def test_map_important_indices(self):
        """測試映射重要欄位索引"""
        indices = self.generator._map_important_indices(self.data)
        
        # 確認索引映射正確
        self.assertEqual(indices['link'], 2)      # 連結
        self.assertEqual(indices['timestamp'], 4)  # 時間戳記
        self.assertEqual(indices['author'], 1)     # 作者
        self.assertEqual(indices['category'], -1)  # 沒有類別欄位
    
    def test_update_indices_after_filter(self):
        """測試過濾後更新索引"""
        # 原始索引
        orig_indices = {
            'link': 2,
            'timestamp': 4,
            'author': 1,
            'category': -1
        }
        
        # 過濾後的資料（無電子郵件欄位）
        filtered_data = SheetData(
            headers=["標題", "作者", "連結", "時間戳記"],
            rows=[
                ["測試標題1", "測試作者1", "https://example.com/1", "2023-01-01"],
                ["測試標題2", "測試作者2", "https://example.com/2", "2023-01-02"]
            ]
        )
        
        # 更新索引
        new_indices = self.generator._update_indices_after_filter(orig_indices, self.data, filtered_data)
        
        # 確認索引更新正確
        self.assertEqual(new_indices['link'], 2)
        self.assertEqual(new_indices['timestamp'], 3)  # 電子郵件被移除後，時間戳記索引應該變為 3
        self.assertEqual(new_indices['author'], 1)
        self.assertEqual(new_indices['category'], -1)
    
    @patch('src.application.html_generator.Environment')
    @patch('src.application.html_generator.Path')
    def test_generate_site(self, mock_path, mock_environment):
        """測試生成網站功能"""
        # 設置模擬
        mock_template = MagicMock()
        mock_env = MagicMock()
        mock_env.get_template.return_value = mock_template
        mock_environment.return_value = mock_env
        
        # 模擬 Path 行為
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.glob.return_value = []
        mock_path.return_value = mock_path_instance
        
        # 設置 generator 的 env 屬性
        self.generator.env = mock_env
        self.generator.static_dir = mock_path_instance
        
        # 調用方法
        self.generator.generate_site(self.data, self.test_output_dir)
        
        # 驗證目錄創建
        self.assertTrue(os.path.exists(self.test_output_dir))
        
        # 驗證模板引擎調用
        mock_env.get_template.assert_called_once_with("index.html")
        mock_template.render.assert_called_once()
    
    def test_to_link(self):
        """測試 URL 轉換為 HTML 連結功能"""
        # 測試一般 URL
        url = "example.com"
        html_link = self.generator._to_link(url)
        self.assertEqual(html_link, '<a href="https://example.com" target="_blank" rel="noopener noreferrer">開啟連結</a>')
        
        # 測試帶有 http 前綴的 URL
        url = "http://example.com"
        html_link = self.generator._to_link(url)
        self.assertEqual(html_link, '<a href="http://example.com" target="_blank" rel="noopener noreferrer">開啟連結</a>')
        
        # 測試空值
        url = ""
        html_link = self.generator._to_link(url)
        self.assertEqual(html_link, "")
    
    def test_format_date(self):
        """測試日期格式化功能"""
        # 這裡應該根據實際的 _format_date 方法實現來測試
        # 假設該方法接收一個日期字串，並返回格式化後的日期字串
        
        # 測試空值
        result = self.generator._format_date("")
        self.assertEqual(result, "") 