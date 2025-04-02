"""
SheetService 單元測試
"""
import json
import os
import unittest
from unittest.mock import patch, MagicMock

from src.application.sheet_service import SheetService
from src.domain.models import SheetData


class TestSheetService(unittest.TestCase):
    """SheetService 單元測試類"""

    @patch('src.application.sheet_service.gspread')
    @patch('src.application.sheet_service.ServiceAccountCredentials')
    def test_init_with_env_credentials(self, mock_credentials, mock_gspread):
        """測試使用環境變數初始化"""
        # 設置環境變數
        test_creds = {"test": "credentials"}
        mock_creds = MagicMock()
        
        with patch.dict(os.environ, {"GOOGLE_CREDENTIALS": json.dumps(test_creds)}):
            mock_credentials.from_json_keyfile_dict.return_value = mock_creds
            
            service = SheetService()
            
            # 驗證從環境變數加載憑證
            mock_credentials.from_json_keyfile_dict.assert_called_once_with(
                test_creds,
                ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
            )
            
            # 驗證 gspread 使用正確的憑證
            mock_gspread.authorize.assert_called_once_with(mock_creds)

    @patch('src.application.sheet_service.gspread')
    @patch('src.application.sheet_service.ServiceAccountCredentials')
    @patch('os.path.exists', return_value=True)
    def test_init_with_file_credentials(self, mock_exists, mock_credentials, mock_gspread):
        """測試使用檔案憑證初始化"""
        # 模擬憑證
        mock_creds = MagicMock()
        mock_credentials.from_json_keyfile_name.return_value = mock_creds
        
        # 移除環境變數並設定檔案路徑
        with patch.dict(os.environ, {"GOOGLE_CREDENTIALS": ""}):
            with patch.dict(os.environ, {"GOOGLE_CREDENTIALS_FILE": "test_creds.json"}):
                service = SheetService()
                
                # 驗證從檔案加載憑證
                mock_credentials.from_json_keyfile_name.assert_called_once_with(
                    "test_creds.json",
                    ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
                )
                
                # 驗證 gspread 使用正確的憑證
                mock_gspread.authorize.assert_called_once_with(mock_creds)

    @patch('gspread.authorize')
    def test_get_sheet_data(self, mock_authorize):
        """測試從 Google Sheets 獲取資料"""
        # 模擬數據
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ["標題", "作者", "連結"],
            ["測試標題1", "測試作者1", "https://example.com/1"],
            ["測試標題2", "測試作者2", "https://example.com/2"]
        ]
        
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        
        # 設置返回值
        mock_authorize.return_value = mock_client
        
        # 設置環境變數
        with patch.dict(os.environ, {"GOOGLE_CREDENTIALS": json.dumps({"test": "credentials"})}):
            # 執行測試
            with patch('src.application.sheet_service.gspread.authorize', return_value=mock_client):
                service = SheetService()
                result = service.get_sheet_data("test_spreadsheet_id", "test_sheet_name")
                
                # 驗證調用
                mock_client.open_by_key.assert_called_once_with("test_spreadsheet_id")
                mock_spreadsheet.worksheet.assert_called_once_with("test_sheet_name")
                mock_worksheet.get_all_values.assert_called_once()
                
                # 驗證返回值
                self.assertIsInstance(result, SheetData)
                self.assertEqual(result.headers, ["標題", "作者", "連結"])
                self.assertEqual(len(result.rows), 2)
                self.assertEqual(result.rows[0], ["測試標題1", "測試作者1", "https://example.com/1"])
                self.assertEqual(result.rows[1], ["測試標題2", "測試作者2", "https://example.com/2"])

    @patch('gspread.authorize')
    def test_get_sheet_data_empty(self, mock_authorize):
        """測試處理空表格"""
        # 模擬空表格
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = []
        
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        
        # 設置返回值
        mock_authorize.return_value = mock_client
        
        # 設置環境變數
        with patch.dict(os.environ, {"GOOGLE_CREDENTIALS": json.dumps({"test": "credentials"})}):
            # 執行測試
            with patch('src.application.sheet_service.gspread.authorize', return_value=mock_client):
                service = SheetService()
                result = service.get_sheet_data("test_spreadsheet_id", "test_sheet_name")
                
                # 驗證返回空 SheetData
                self.assertIsInstance(result, SheetData)
                self.assertEqual(result.headers, [])
                self.assertEqual(result.rows, []) 