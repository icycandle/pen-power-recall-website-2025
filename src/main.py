#!/usr/bin/env python
"""
主應用入口點 - 從Google Sheets讀取數據並產生靜態網站
"""
import argparse
import os
import sys

from dotenv import load_dotenv

from src.application.html_generator import HtmlGenerator
from src.application.sheet_service import SheetService
from src.domain.models import SheetData


def ensure_import_paths() -> None:
    """確保可以正確導入其他模組"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def create_mock_data() -> SheetData:
    """創建用於測試的模擬數據"""
    headers = ["標題", "作者", "連結", "時間戳記", "類別"]
    rows = [
        [
            "測試項目1",
            "測試作者1",
            "https://example.com/1",
            "2023/04/30 上午 10:30:45",
            "分類A",
        ],
        [
            "測試項目2",
            "測試作者2",
            "https://example.com/2",
            "2023/05/01 下午 02:45:12",
            "分類B",
        ],
        [
            "測試項目3",
            "測試作者3",
            "https://example.com/3",
            "2023/05/02 上午 09:15:30",
            "分類A",
        ],
    ]
    return SheetData(headers=headers, rows=rows)


def dry_run(output_dir: str) -> None:
    """
    使用模擬數據運行程式，不需要真實的 Google Sheets 憑證

    Args:
        output_dir: 輸出目錄
    """
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)

    # 使用模擬數據
    data = create_mock_data()

    # 產生HTML檔案
    html_generator = HtmlGenerator()
    html_generator.generate_site(data, output_dir)

    print(f"[DRY RUN] 網站已成功產生在 {output_dir} 目錄中")

    # 檢查輸出文件是否存在
    index_path = os.path.join(output_dir, "index.html")
    if not os.path.exists(index_path):
        print(f"錯誤: 未能生成索引文件 {index_path}")
        sys.exit(1)

    print("[DRY RUN] 測試通過!")


def main() -> None:
    """主函數：讀取資料並產生靜態網站"""
    # 確保導入路徑正確
    ensure_import_paths()

    parser = argparse.ArgumentParser(
        description="從 Google Sheets 讀取數據並產生靜態網站"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="使用模擬數據運行，不需真實憑證"
    )
    parser.add_argument("--output-dir", default=None, help="指定輸出目錄")
    args = parser.parse_args()

    # 載入環境變數
    load_dotenv()

    # 確定輸出目錄 (命令行參數優先於環境變數)
    output_dir = args.output_dir or os.getenv("OUTPUT_DIR", "dist")

    if args.dry_run:
        dry_run(output_dir)
        return

    # 取得環境變數
    spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
    sheet_name = os.getenv("SHEET_NAME", "Sheet1")

    # 檢查必要的環境變數
    if not spreadsheet_id:
        print("錯誤: 未設置 SPREADSHEET_ID 環境變數")
        sys.exit(1)

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
