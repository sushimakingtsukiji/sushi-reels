# sushi-reels

Sushi Making Tsukiji のSNS用リール制作パイプラインと、公開用の完成動画置き場（Metricoolがここの raw URL から動画を取り込む）。

- `reel_XXX.mp4` … 完成動画（公開URL: https://raw.githubusercontent.com/sushimakingtsukiji/sushi-reels/main/reel_XXX.mp4）
- `pipeline/build_reel.py` … edit.json から動画を書き出す（素材・テロップ・元音声・BGM・締めクリップ）
- `pipeline/build_cta.py` … 共通の予約導線クリップ（ナレーション入り）を作り直す
- `pipeline/sheets.sh` … 素材のコンタクトシート作成
- `assets/` … 締めクリップ、BGMライブラリ、ナレーション音声、画面録画
- `docs/video_style.md` … 制作・投稿ルールと投稿履歴
- `docs/footage_catalog.md` … 素材一覧（素材本体は非公開リポジトリ sushi-footage）
- `videos/<番号_テーマ>/` … 各動画の edit.json・キャプション・カバー画像

素材動画（ゲストが映った未編集素材）はこのリポジトリには置かない。
