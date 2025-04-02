# 作品集展示平台

這是一個自動化的作品集展示網站，從 Google Sheets 獲取資料並生成靜態網站，然後部署到 Cloudflare Pages。適合用作文學作品、藝術作品、專案作品等集中展示平台。

## 功能特點

- 從 Google Sheets 自動讀取作品集資料
- 生成美觀的響應式靜態網頁
- 支持按類別篩選作品
- 提供搜尋功能以快速找到作品或作者
- 將連結自動轉換為可點擊的按鈕
- 透過 GitHub Actions 每日自動更新
- 完全免費解決方案：使用 GitHub Actions + Cloudflare Pages

## 預期的 Google Sheets 欄位

系統預設處理以下欄位：
- `時間戳記`：作品提交時間
- `作者名`：作者的名稱
- `作品連結`：指向作品的連結
- `類別`：作品類別，用於分類和篩選

您可以根據需要添加其他欄位，系統會自動顯示所有欄位。

## 環境設定

1. 複製 `.env.example` 到 `.env` 並填入您的設定
2. 獲取 Google Sheets API 憑證並下載為 `credentials.json`

### Google Sheets API 憑證設定

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建一個新專案
3. 啟用 Google Sheets API
4. 創建服務帳戶金鑰
5. 下載 JSON 格式的金鑰檔案並重命名為 `credentials.json`
6. 將服務帳戶電郵分享給您的 Google Sheets 檔案

## 本地開發

```bash
# 安裝依賴項
poetry install

# 執行應用程式
poetry run python src/main.py
```

## GitHub 設定

在存儲庫中設定以下 Secrets：

- `SPREADSHEET_ID`：您的 Google Sheets 的 ID
- `SHEET_NAME`：工作表名稱（通常是 Sheet1）
- `GOOGLE_CREDENTIALS`：將 credentials.json 的完整內容貼上
- `CLOUDFLARE_API_TOKEN`：Cloudflare API 權杖
- `CLOUDFLARE_ACCOUNT_ID`：Cloudflare 帳戶 ID

## Cloudflare Pages 設定

1. 登入 Cloudflare 帳戶
2. 前往 Pages
3. 創建名為 `pen-power-recall` 的新專案 (或自訂名稱，但需與 GitHub Actions 工作流程匹配)

## 專案結構

```
pen_power_recall_website_2025/
├── .github/
│   └── workflows/         # GitHub Actions 工作流程
│       └── deploy.yml     # 部署工作流程
├── src/
│   ├── domain/            # 領域模型
│   │   └── models.py      # 定義 SheetData 等數據模型
│   ├── application/       # 應用服務
│   │   ├── sheet_service.py  # Google Sheets 服務
│   │   └── html_generator.py # HTML 生成器
│   ├── infrastructure/    # 基礎設施層
│   └── presentation/      # 表現層
│       ├── templates/     # HTML 模板
│       │   └── index.html # 首頁模板
│       └── static/        # 靜態資源
│           └── css/       # CSS 樣式文件
├── .env.example           # 環境變數範例
├── pyproject.toml         # Poetry 設定
└── README.md              # 專案說明文件
```

## 定制化

您可以通過修改以下文件來自定義網站的外觀和行為：

- `src/presentation/templates/index.html`：修改首頁的 HTML 結構
- `src/presentation/static/css/style.css`：自定義 CSS 樣式
- `src/application/html_generator.py`：調整資料處理和 HTML 生成邏輯

## 授權

MIT 授權

## 安裝與開發

### 安裝依賴

```bash
# 安裝所有依賴（包括開發依賴）
poetry install --with dev
```

### 設置 Git Hooks

本專案使用 pre-commit 來確保程式碼品質。安裝 git hooks：

```bash
# 安裝 pre-commit hooks
poetry run pre-commit install
```

pre-commit 會在每次提交前執行以下檢查：
- 程式碼格式化 (black, isort)
- 靜態代碼分析 (ruff, mypy)
- 常見問題檢查 (檢查尾隨空格、文件末尾換行等)
- 運行單元測試

### 手動運行檢查

```bash
# 對所有文件運行 pre-commit 檢查
poetry run pre-commit run --all-files

# 運行特定的檢查
poetry run pre-commit run black --all-files
poetry run pre-commit run pytest --all-files
```
