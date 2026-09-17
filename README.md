# 学生生活マップ

水戸市の学生向け便利スポット（安い飯屋・勉強できる場所・ATM・バス停など）を
地図上で共有するDjangoアプリケーション。`design.md` の設計に基づく実装。

## セットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate   # 初期カテゴリはdata migrationで自動投入される
python manage.py createsuperuser   # 管理者アカウント作成
python manage.py runserver
```

## ロールについて

- **学生（student）**: 地図の閲覧・検索・コメント投稿。ATM・バス停・トイレ等、経営者が存在しないカテゴリに限りスポット登録も可能。
- **経営者（business）**: 全カテゴリのスポット登録が可能。
- **管理者（admin）**: Django Admin（`/admin/`）からスポットの承認・却下を行う。新規登録画面からは作成できず、`createsuperuser`または既存管理者が手動で作成する。

## 地図タイル

地図タイルは国土地理院の標準地図（`cyberjapandata.gsi.go.jp`）を利用している。
OpenStreetMap公式タイルサーバーは利用ポリシー（Refererヘッダーの検証など）が
厳しく、環境によっては「403 Access blocked」で表示できないことがあるため、
日本国内向けであることも踏まえてAPIキー不要の国土地理院タイルに切り替えた。
すべて日本語表記で表示される。

## ジオコーディング

- **住所 → 緯度経度**: スポット登録フォームで住所を入力し「住所から検索」を押すと、
  国土地理院 AddressSearch API（APIキー不要・CORS許可済み）で自動変換される。
- **緯度経度 → 住所（逆ジオコーディング）**: 住所が分からない場合は、先に地図をクリックして
  位置を指定すると、国土地理院 逆ジオコーディングAPIで市区町村レベルの住所を自動入力する
  （番地までは取得できないため、登録前に手動で補う必要がある）。
- どちらも失敗した場合は地図をクリックして手動でピンを調整できる。

## 主要URL

| 画面 | URL |
|---|---|
| 地図トップ | `/` |
| スポット詳細 | `/spots/<id>/` |
| スポット登録 | `/spots/new/` |
| マイページ | `/spots/mine/` |
| 会員登録 | `/accounts/signup/` |
| ログイン／ログアウト | `/accounts/login/` / `/accounts/logout/` |
| 管理者承認一覧 | `/admin/spots/spot/` |
