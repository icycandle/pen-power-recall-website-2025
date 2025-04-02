#!/usr/bin/env python
"""
Google Sheets API 憑證測試腳本
"""
import os
import sys
from typing import Any
import json
from dotenv import load_dotenv

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from colorama import init, Fore, Style

# 初始化 colorama
init()

def print_success(message: str) -> None:
    """打印成功訊息"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message: str) -> None:
    """打印錯誤訊息"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message: str) -> None:
    """打印資訊訊息"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_header(message: str) -> None:
    """打印標題"""
    print(f"\n{Fore.CYAN}=== {message} ==={Style.RESET_ALL}\n")

def test_credentials() -> None:
    """測試 Google Sheets API 憑證"""
    print_header("Google Sheets API 憑證測試")
    
    # 載入環境變數
    load_dotenv()
    
    # 檢查環境變數
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME", "Sheet1")
    
    if not spreadsheet_id:
        print_error("找不到環境變數 SPREADSHEET_ID")
        print_info("請在 .env 檔案中設定 SPREADSHEET_ID")
        sys.exit(1)
    
    # 檢查憑證文件
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    google_credentials_env = os.getenv("GOOGLE_CREDENTIALS")
    
    print_info(f"嘗試連接到試算表 ID: {spreadsheet_id}, 工作表: {sheet_name}")
    
    try:
        # 1. 先嘗試從環境變數加載憑證
        if google_credentials_env:
            print_info("從環境變數 GOOGLE_CREDENTIALS 加載憑證")
            try:
                credentials_dict = json.loads(google_credentials_env)
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    credentials_dict,
                    ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
                )
                print_success("從環境變數成功載入憑證")
            except Exception as e:
                print_error(f"從環境變數載入憑證失敗: {str(e)}")
                sys.exit(1)
        # 2. 如果環境變數不存在，嘗試從檔案加載
        else:
            print_info(f"從檔案 {creds_file} 加載憑證")
            if not os.path.exists(creds_file):
                print_error(f"找不到憑證檔案 {creds_file}")
                print_info("請確保您已下載 credentials.json 檔案並放在正確位置")
                sys.exit(1)
                
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    creds_file,
                    ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
                )
                print_success("從檔案成功載入憑證")
            except Exception as e:
                print_error(f"從檔案載入憑證失敗: {str(e)}")
                sys.exit(1)
        
        # 嘗試授權並連接
        print_info("嘗試使用憑證授權並連接到 Google Sheets API")
        client = gspread.authorize(credentials)
        print_success("成功授權")
        
        # 嘗試開啟試算表
        print_info(f"嘗試開啟試算表 ID: {spreadsheet_id}")
        spreadsheet = client.open_by_key(spreadsheet_id)
        print_success(f"成功開啟試算表: {spreadsheet.title}")
        
        # 嘗試開啟工作表
        print_info(f"嘗試開啟工作表: {sheet_name}")
        worksheet = spreadsheet.worksheet(sheet_name)
        print_success(f"成功開啟工作表: {worksheet.title}")
        
        # 嘗試讀取資料
        print_info("嘗試讀取資料")
        values = worksheet.get_all_values()
        row_count = len(values)
        col_count = len(values[0]) if values else 0
        
        print_success(f"成功讀取資料: {row_count} 列 x {col_count} 欄")
        
        if values:
            print_info("資料預覽 (前 3 列):")
            for i, row in enumerate(values[:3]):
                print(f"  行 {i+1}: {', '.join(row[:5])}" + ("..." if len(row) > 5 else ""))
        
        # 取得服務帳號電子郵件
        service_account_email = credentials.service_account_email
        print_info(f"服務帳號電子郵件: {service_account_email}")
        print_info("請確保您已將此電子郵件加入試算表的共享名單")
        
        print_header("測試完成")
        print_success("您的 Google Sheets API 憑證運作正常!")
        print_success("您可以使用此憑證來部署您的應用程式")
        
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        print_info("請檢查以下可能的問題:")
        print_info("1. 憑證檔案是否有效")
        print_info("2. 試算表 ID 是否正確")
        print_info("3. 工作表名稱是否正確")
        print_info("4. 服務帳號是否有權限存取試算表")
        print_info("5. Google Sheets API 是否已啟用")
        sys.exit(1)

if __name__ == "__main__":
    test_credentials() 