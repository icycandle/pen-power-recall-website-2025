#!/usr/bin/env python
"""
HTML 產生測試腳本 - 測試從 Google Sheets 生成靜態網頁
"""
import http.server
import os
import shutil
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

from colorama import Fore, Style, init
from dotenv import load_dotenv

from src.application.html_generator import HtmlGenerator

# 導入應用程式相關功能
from src.application.sheet_service import SheetService

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


def start_http_server(directory: str, port: int = 8080) -> threading.Thread:
    """
    啟動一個 HTTP 伺服器來預覽生成的 HTML

    Args:
        directory: 要提供的目錄
        port: 伺服器端口

    Returns:
        伺服器執行緒
    """
    original_dir = os.getcwd()
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler

    class NoLoggingTCPServer(socketserver.TCPServer):
        def __init__(self, *args, **kwargs):
            # 允許端口重用，解決 "Address already in use" 問題
            socketserver.TCPServer.allow_reuse_address = True
            super().__init__(*args, **kwargs)

        def handle_error(self, request, client_address):
            pass

    try:
        httpd = NoLoggingTCPServer(("", port), handler)

        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        return server_thread
    except Exception as e:
        # 如果 8080 端口也被佔用，嘗試其他端口
        if isinstance(e, OSError) and e.errno == 48:  # Address already in use
            print_info(f"端口 {port} 已被佔用，嘗試端口 8090...")
            os.chdir(original_dir)
            return start_http_server(directory, 8090)
        else:
            # 如果是其他錯誤，重新拋出
            os.chdir(original_dir)
            raise


def test_html_generation() -> None:
    """測試 HTML 生成功能"""
    print_header("HTML 生成測試")

    # 載入環境變數
    load_dotenv()

    # 檢查環境變數
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME", "Sheet1")

    if not spreadsheet_id:
        print_error("找不到環境變數 SPREADSHEET_ID")
        print_info("請在 .env 檔案中設定 SPREADSHEET_ID")
        sys.exit(1)

    # 設定輸出目錄
    output_dir = os.getenv("OUTPUT_DIR", "dist")
    test_output_dir = "test_output"
    original_dir = os.getcwd()

    # 確保測試輸出目錄存在並清空
    if os.path.exists(test_output_dir):
        shutil.rmtree(test_output_dir)
    os.makedirs(test_output_dir, exist_ok=True)

    try:
        # 獲取資料
        print_info("從 Google Sheets 獲取資料...")
        sheet_service = SheetService()
        data = sheet_service.get_sheet_data(spreadsheet_id, sheet_name)

        # 顯示獲取的資料概覽
        print_success(f"成功獲取資料: {data.row_count} 行")
        print_info("表頭欄位:")
        for i, header in enumerate(data.headers):
            print(f"  {i+1}. {header}")

        # 產生 HTML
        print_info(f"生成 HTML 到 {test_output_dir} 目錄...")
        html_generator = HtmlGenerator()
        html_generator.generate_site(data, test_output_dir)

        index_file = os.path.join(test_output_dir, "index.html")
        if os.path.exists(index_file):
            print_success(f"成功生成 HTML 檔案: {index_file}")

            # 獲取檔案大小
            file_size = Path(index_file).stat().st_size
            print_info(f"HTML 檔案大小: {file_size / 1024:.2f} KB")

            # 檢查生成的其他檔案
            css_file = os.path.join(test_output_dir, "static", "css", "style.css")
            if os.path.exists(css_file):
                print_success("CSS 檔案已生成")

            # 啟動預覽伺服器
            port = 8080
            print_info(f"啟動預覽伺服器在 http://localhost:{port}...")
            try:
                server_thread = start_http_server(test_output_dir, port)

                # 開啟瀏覽器
                print_info("在瀏覽器中開啟預覽...")
                webbrowser.open(f"http://localhost:{port}")

                print_header("測試完成")
                print_success("HTML 生成功能運作正常!")
                print_info(f"您可以在瀏覽器中查看生成的網頁: http://localhost:{port}")
                print_info("按 Ctrl+C 關閉伺服器並退出測試")

                # 保持伺服器運行
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print_info("\n伺服器已停止，測試結束")
                    os.chdir(original_dir)
            except Exception as e:
                os.chdir(original_dir)
                print_error(f"啟動伺服器時發生錯誤: {str(e)}")
                print_info(
                    "請嘗試手動開啟生成的 HTML 文件: " + os.path.abspath(index_file)
                )
                sys.exit(1)
        else:
            print_error(f"未找到生成的 HTML 檔案: {index_file}")
            sys.exit(1)

    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    test_html_generation()
