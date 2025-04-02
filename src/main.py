#!/usr/bin/env python
"""
主應用入口點 - 從Google Sheets讀取數據並產生靜態網站
"""
import os
from dotenv import load_dotenv
from application.sheet_service import SheetService
from application.html_generator import HtmlGenerator

def main() -> None:
    """主函數：讀取資料並產生靜態網站"""
    # 載入環境變數
    load_dotenv()
    
    # 取得環境變數
    spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
    sheet_name = os.getenv("SHEET_NAME", "Sheet1")
    output_dir = os.getenv("OUTPUT_DIR", "dist")
    
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 從Google Sheets獲取資料
    sheet_service = SheetService()
    data = sheet_service.get_sheet_data(spreadsheet_id, sheet_name)
    
    # 產生HTML檔案
    html_generator = HtmlGenerator()
    html_generator.generate_site(data, output_dir)
    
    print(f"網站已成功產生在 {output_dir} 目錄中")

if __name__ == "__main__":
    main() 