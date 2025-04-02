"""
HTML 生成器 - 負責產生靜態網站檔案
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.domain.models import SheetData


class HtmlGenerator:
    """HTML 生成器類別"""

    def __init__(self) -> None:
        """初始化 Jinja2 模板環境"""
        # 設定模板目錄
        template_dir = Path(__file__).parent.parent / "presentation" / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))

        # 自定義過濾器 - 將連結轉換為 HTML 連結
        self.env.filters["to_link"] = self._to_link
        self.env.filters["format_date"] = self._format_date

        # 靜態資源目錄
        self.static_dir = Path(__file__).parent.parent / "presentation" / "static"

    def generate_site(self, data: SheetData, output_dir: str) -> None:
        """
        生成完整的靜態網站

        Args:
            data: 包含表頭和資料的 SheetData 物件
            output_dir: 輸出目錄路徑
        """
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)

        # 記錄原始欄位索引，用於在過濾後恢復欄位對應關係
        orig_indices = self._map_important_indices(data)

        # 過濾電子郵件地址欄位
        filtered_data = self._filter_sensitive_data(data)

        # 映射過濾後的欄位索引
        new_indices = self._update_indices_after_filter(
            orig_indices, data, filtered_data
        )

        # 產生主頁
        self._generate_index_page(filtered_data, output_dir, new_indices)

        # 複製靜態資源到輸出目錄
        self._copy_static_files(output_dir)

    def _map_important_indices(self, data: SheetData) -> dict:
        """
        映射原始資料中重要欄位的索引

        Args:
            data: 原始資料

        Returns:
            含有重要欄位索引的字典
        """
        indices = {"link": -1, "timestamp": -1, "author": -1, "category": -1}

        for i, header in enumerate(data.headers):
            header_lower = header.lower()
            if header_lower in ["作品連結", "連結", "link", "url"]:
                indices["link"] = i
            elif header_lower in ["時間戳記", "timestamp", "日期", "時間"]:
                indices["timestamp"] = i
            elif header_lower in ["作者名", "作者", "author", "name"]:
                indices["author"] = i
            elif header_lower in ["類別", "分類", "category", "type"]:
                indices["category"] = i

        return indices

    def _update_indices_after_filter(
        self, orig_indices: dict, orig_data: SheetData, filtered_data: SheetData
    ) -> dict:
        """
        在過濾後更新欄位索引

        Args:
            orig_indices: 原始索引字典
            orig_data: 原始資料
            filtered_data: 過濾後的資料

        Returns:
            更新後的索引字典
        """
        # 創建新索引字典
        new_indices = {"link": -1, "timestamp": -1, "author": -1, "category": -1}

        # 建立原始欄位名稱到過濾後索引的映射
        for key, orig_idx in orig_indices.items():
            if orig_idx >= 0:
                header_name = orig_data.headers[orig_idx]
                try:
                    new_idx = filtered_data.headers.index(header_name)
                    new_indices[key] = new_idx
                except ValueError:
                    # 如果欄位已被過濾掉，保持 -1
                    pass

        return new_indices

    def _filter_sensitive_data(self, data: SheetData) -> SheetData:
        """
        過濾敏感資料，如電子郵件地址

        Args:
            data: 原始資料

        Returns:
            過濾後的資料
        """
        # 找出電子郵件地址欄位的索引
        email_indices = []
        for i, header in enumerate(data.headers):
            header_lower = header.lower()
            if (
                "電子郵件" in header_lower
                or "email" in header_lower
                or "mail" in header_lower
            ):
                email_indices.append(i)

        # 如果沒有找到電子郵件欄位，直接返回原始資料
        if not email_indices:
            return data

        # 過濾表頭和資料
        filtered_headers = []
        for i, header in enumerate(data.headers):
            if i not in email_indices:
                filtered_headers.append(header)

        filtered_rows = []
        for row in data.rows:
            filtered_row = []
            for i, cell in enumerate(row):
                if i not in email_indices:
                    filtered_row.append(cell)
            filtered_rows.append(filtered_row)

        # 創建並返回新的 SheetData 物件
        return SheetData(headers=filtered_headers, rows=filtered_rows)

    def _generate_index_page(
        self, data: SheetData, output_dir: str, indices: dict
    ) -> None:
        """
        生成首頁 HTML 檔案

        Args:
            data: 包含表頭和資料的 SheetData 物件
            output_dir: 輸出目錄路徑
            indices: 欄位索引字典
        """
        # 獲取模板
        template = self.env.get_template("index.html")

        # 獲取當前時間
        current_time = datetime.now()
        format_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 渲染模板
        html_content = template.render(
            title="作品集展示",
            subtitle="精選創作分享平台",
            headers=data.headers,
            rows=data.rows,
            items=data.to_dict_list(),
            link_column_index=indices["link"],
            timestamp_column_index=indices["timestamp"],
            author_column_index=indices["author"],
            category_column_index=indices["category"],
            now=format_time,
            year=current_time.year,
        )

        # 寫入檔案
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

    def _copy_static_files(self, output_dir: str) -> None:
        """
        將靜態檔案複製到輸出目錄

        Args:
            output_dir: 輸出目錄路徑
        """
        # 建立靜態資源目錄
        static_output = os.path.join(output_dir, "static")
        os.makedirs(static_output, exist_ok=True)

        # 複製所有靜態檔案
        if self.static_dir.exists():
            for item in self.static_dir.glob("**/*"):
                if item.is_file():
                    # 建立相對路徑
                    rel_path = item.relative_to(self.static_dir)
                    # 建立目標路徑
                    dest_path = Path(static_output) / rel_path
                    # 確保目標目錄存在
                    os.makedirs(dest_path.parent, exist_ok=True)
                    # 複製檔案
                    shutil.copy2(item, dest_path)

    @staticmethod
    def _to_link(value: str) -> str:
        """
        將URL轉換為HTML連結

        Args:
            value: URL字串

        Returns:
            轉換後的HTML連結
        """
        if not value:
            return ""

        # 確保URL有http前綴
        url = value
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">開啟連結</a>'

    @staticmethod
    def _format_date(value: str) -> str:
        """
        格式化時間戳記

        Args:
            value: 時間戳記字串

        Returns:
            格式化後的日期字串
        """
        if not value:
            return ""

        try:
            # 嘗試解析Google Forms的時間戳記格式 (2023/4/30 上午 10:30:45)
            date_obj = datetime.strptime(value, "%Y/%m/%d %p %I:%M:%S")
            return date_obj.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            try:
                # 嘗試ISO格式
                date_obj = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return date_obj.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                # 如果無法解析，返回原始值
                return value
