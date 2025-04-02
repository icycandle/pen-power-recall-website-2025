"""
Google Sheets 服務 - 負責從 Google Sheets 取得資料
"""

import json
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from ..domain.models import SheetData


class SheetService:
    """Google Sheets 服務類別"""

    def __init__(self) -> None:
        """初始化服務，設定 Google Sheets API 認證"""
        # 在CI環境中使用環境變數中的憑證
        credentials_json = os.getenv("GOOGLE_CREDENTIALS")
        if credentials_json:
            # 將環境變數轉換為臨時檔案
            credentials_dict = json.loads(credentials_json)
            self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_dict,
                [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
        else:
            # 在本地開發環境使用檔案憑證
            creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
            self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                creds_file,
                [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ],
            )

        self.client = gspread.authorize(self.credentials)

    def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> SheetData:
        """
        從 Google Sheets 擷取資料

        Args:
            spreadsheet_id: Google Sheets 的 ID
            sheet_name: 工作表名稱

        Returns:
            SheetData: 包含表頭和資料的物件
        """
        # 打開 Google Sheets
        sheet = self.client.open_by_key(spreadsheet_id).worksheet(sheet_name)

        # 獲取所有資料
        all_values = sheet.get_all_values()

        # 如果表格是空的，返回空資料
        if not all_values:
            return SheetData(headers=[], rows=[])

        # 將第一行作為表頭，其餘為資料
        headers = all_values[0]
        rows = all_values[1:]

        return SheetData(headers=headers, rows=rows)
