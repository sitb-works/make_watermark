# Watermark CLI

画像に透かし（ウォーターマーク）を自動で合成するPythonスクリプトです。
クロスハッチパターンを重ねて、自然な透かし効果を生成します。

## 🔍 処理前 → 処理後の比較

| 元画像 | 透かし合成後 |
|--------|----------------|
| ![](sample_img/sample.png) | ![](sample_img/sample_wm.jpg) |


## 📦 構成

```
make_watermark/
├ apply_watermark.py       # 実行スクリプト
├ watermark_config.txt     # 設定ファイル（フォントやテキスト）
├ images/                  # 入力画像フォルダ
└ watermarked_output/      # 出力フォルダ（自動作成）
```

## ⚙️ 設定ファイル（`watermark_config.txt`）

```txt
# 使用するフォントのパス（省略時はOSデフォルト）
font_path = /path/to/fonts/Font.ttf

# フォントサイズ（ピクセル単位）
font_size = 32

# 入力する透かしテキスト（複数行OK）
text:
This is a sample image.
Please do not repost.
endtext
```

- `font_path`：使用するTrueTypeフォントのパス（例：arial.ttf）
- `font_size`：文字サイズ（px）
- `text`：中央下に入れるテキスト（複数行OK）

> 設定ファイルがない場合はOSごとのデフォルトフォントが設定されます。
> `apply_watermark.py`

## 🚀 使い方

### 🔹 単一画像を処理
```bash
python apply_watermark.py path/to/image.jpg
```

### 🔹 フォルダ内の画像を一括処理
```bash
python apply_watermark.py images/
```

- `.jpg`, `.jpeg`, `.png` に対応
- 出力先は `watermarked_output/` に自動生成
- ファイル名の末尾に `_wm` が付きます（例：`sample_wm.jpg`）

## ✨ 特徴

- ✅ 透かし文字は中央下に整列（テキストサイズはconfigで設定）
- ✅ 透かしはクロスハッチパターン（画像サイズに応じてスケーリング）
- ✅ PILベースで処理軽め
- ✅ 設定ファイルでカスタマイズ簡単

## 🛠 カスタマイズ案（note有料記事にて公開予定）

- [ ] クロスハッチパターン色を自動で取得 or config指定
- [ ] コマンドライン引数実装（`--no-text` でテキスト消したり `--gray-stripes` で色強制したり）
- [ ] GUI版（Tkinter/Gradioなど）
- [ ] WordPress自動入稿機能

## 📦 仮想環境セットアップ

以下の内容で `requirements.txt` を作成してください：

```txt
Pillow>=10.0.0
```

セットアップ手順：
```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
```

---

何か不明点があれば、お気軽にお知らせください！
