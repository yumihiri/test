# Claude Codeへの依頼文（コピペ用）

このプロジェクトフォルダには以下が入っています。

- `design.md` … 詳細設計書（技術スタック・DB設計・機能仕様・URL設計）
- `student-map-prototype.html` … 見た目とロール別の動きを確認するためのプロトタイプ（DB・API・実認証なし、ブラウザで直接開けるモック）

以下の指示をそのままClaude Codeに貼り付けてください。

---

`design.md`を読んで、このDjangoプロジェクトの**本実装**を進めてください。プロトタイプではなく、実際にDBに保存され、Djangoの認証機構でログインが機能する状態を目指します。

`student-map-prototype.html`は見た目とロール別の画面切り替えの参考用です。データの持ち方（インメモリのJS配列）はダミーなので、これはそのまま使わず、`design.md`のDB設計（Userモデルのroleカラム、Category/Spot/Commentモデル）に沿って実装し直してください。

進める順番の目安：

1. Djangoプロジェクトの雛形作成（`design.md` 3章のディレクトリ構成に沿う）
2. `accounts`アプリ：カスタムUserモデル（role: student/business/admin）、会員登録・ログイン・ログアウト
3. `spots`アプリ：Category・Spotモデル、Django Adminでの承認フロー
4. 地図表示・スポット登録画面（`student-map-prototype.html`の見た目・操作感を踏襲）
5. `reviews`アプリ：コメント・評価機能

まだ確定していない点（`design.md`内に「要検討」「要判断」と記載）：

- ジオコーディングAPIをNominatimのままにするか、国土地理院AddressSearch APIに変更するか
- 経営者が存在しないカテゴリ（ATM・バス停・トイレ等）を誰が登録するか
- 同一ユーザーが同じスポットに複数回評価できないよう制限するか（`unique_together`を入れるか）

判断に迷う場合は、実装を進める前に確認してください。
