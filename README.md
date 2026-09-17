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

地図タイルはOpenStreetMap公式サーバーではなく、CARTO Voyagerタイル
（`basemaps.cartocdn.com`）を利用している。OSM公式タイルサーバーは
利用ポリシー（Refererヘッダーの検証など）が厳しく、開発環境によっては
「403 Access blocked」でタイルが表示されないことがあるため。
地図データ自体はOpenStreetMapのものであり、帰属表示はOSMとCARTO両方に行っている。

## ジオコーディング

スポット登録時の住所→緯度経度変換には、国土地理院 AddressSearch API
（APIキー不要・CORS許可済み）を利用している。変換に失敗した場合は
地図をクリックして手動でピンを調整できる。

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
