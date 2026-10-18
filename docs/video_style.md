# 寿司体験リール 型（v2）

## ビジネス前提
- 築地で実際に営業している寿司店のカウンターで、訪日外国人向けに握り体験を提供
- 集客：Instagram / Facebook / TikTok / YouTube の短尺動画 → プロフのリンク → 自社予約サイトで予約
- 見るのは外国人のみ。テロップも投稿キャプションも**すべて英語、日本語なし**
- テロップ文言・投稿キャプションは毎回こちらで考えてOK（サービスにちなんだ内容で）

## 映像の方針
- 主役は**体験しているゲストの笑顔**。握る瞬間、食べた瞬間のリアクション、乾杯、集合写真を優先して使う
- 縦 9:16、1080x1920、25〜30秒、1カット1〜2秒
- 素材の質感（築地の本物のカウンター、職人、日本酒）は残す

## 構成テンプレ
1. **フック（0–2s）**：一番の笑顔 or 握りのアップ＋大きめのテロップ
2. **体験の流れ（2–20s）**：職人の手元 → ゲストが握る → 食べる → 乾杯。テロップで短いストーリーを語る
3. **締め（20–24s）**：集合写真＋「See you in Tsukiji」系の一言
4. **予約導線（最後の4〜5s）**：実際の操作画面で「プロフ → リンク → Book」を見せる。タップ位置に赤丸＋矢印

## テロップ
- 参考：初回投稿（白文字・小さめ・中央）と他社参考（太字・縁取り・キーワードだけ黄色・一文ずつ語る形式）
- v2で採用：**太字の白文字＋黒縁取り、キーワードを黄色ハイライト**、画面の中央〜やや下（下端のUIエリアは避ける）
- 一文ずつ短く区切ってテンポよく切り替える
- 表記の正確さを毎回チェック（Tsukiji, Japanese など）

## 予約導線パート（全SNS共通）
- **Webサイト部分のみ**を使い、全プラットフォームで同じ締めにする（SNSのプロフ画面は映さない）
- 完成済みクリップ：`assets/cta_booking.mp4`（約5.2秒、1080x1920）。毎回これを最後に付けるだけ
  - 「Tap the link in our bio」→ サイトのトップ〜スクロール →「Hit BOOK NOW」（赤丸＋矢印）→「Pick your date / See you in Tsukiji!」で予約画面
  - 背景はサイトと同じクリーム色、文字はサイトの紺＋ロゴの赤
  - **英語ナレーション入り**（AI音声 Kokoro / af_heart・アメリカ英語の女性）：「Tap the link in our bio. / Hit Book Now! / Pick your date, and see you in Tsukiji!」を各ステップの頭に配置。約6秒
  - ナレーションの再生成：`pipeline/tts.py`（発音記号で入力）
- 作り直しスクリプト：`pipeline/build_cta.py assets/source/booking_screen_recording.mp4 assets/cta_booking.mp4`
- サイトのデザインが変わったら画面録画を撮り直して再生成

## 投稿キャプション
- 全SNS共通で同じキャプションを使う（コピペ1回で済むように）
- 英語のみ。参考は競合（sushi_making_japan）の投稿：感謝＋楽しさを伝える短文、絵文字多め
- 構成（4〜6行）
  1. フック：ゲストへの感謝 or 体験の一番の瞬間（絵文字2〜3個）
  2. 体験の中身を1〜2行（その回の映像に合わせる：握り、職人、食べる、乾杯など）
  3. 安心材料を1行（No experience needed / English friendly / real sushi counter in Tsukiji など、毎回1〜2個を入れ替え）
  4. 📍 Tsukiji, Tokyo
  5. 予約導線：👆 Book via the link in our bio
  6. 空行のあとハッシュタグ
- ハッシュタグは**5個**（Instagramが2025年12月から1投稿5個までに制限。TikTok・YouTube Shortsも3〜5個が目安なので全SNSで5個に統一）
  - 枠1：ブランド `#sushimakingtsukiji`（毎回固定）
  - 枠2：場所 `#tsukiji` / `#tsukijimarket` / `#tokyo`
  - 枠3：旅行計画中の人向け `#tokyotravel` / `#japantravel` / `#thingstodointokyo` / `#japantrip`
  - 枠4：体験ジャンル `#sushiclass` / `#sushimaking` / `#cookingclass` / `#tokyoexperience`
  - 枠5：食 `#sushi` / `#nigiri` / `#japanesefood` / `#tokyofood`
  - 動画の内容に合わせて各枠から1個選び、毎回同じ組み合わせにならないよう回す

## 投稿（Metricool経由）
- Metricoolブランド「Sushi Making Tsukiji」（blogId 7484125、タイムゾーン Asia/Tokyo）に4SNS連携済み
- 設定：Instagram=リール（フィードにも表示）／Facebook=リール／TikTok=全員に公開／YouTube=ショート・公開・子ども向けではない
- 投稿時間：**日本時間 2:00**（ロンドン18時・パリ19時・ニューヨーク13時・LA10時。欧州の夕方と米国の昼が重なる時間帯。夏時間終了後もほぼ同じ時間帯に収まる）
- 動画の受け渡し：GitHub公開リポジトリ `sushimakingtsukiji/sushi-reels` に `reel_XXX.mp4` をpush → `https://raw.githubusercontent.com/sushimakingtsukiji/sushi-reels/main/reel_XXX.mp4` をMetricoolの`media`に渡す（Metricoolが自社ストレージにコピーするので確実）
- **カバー（サムネ）を全SNSでそろえる**：`videoCoverMilliseconds: 800`（冒頭のフック画面）をMetricoolに毎回指定。指定しないとFacebookだけ別のコマを自動で選ぶ
- YouTubeは @SushiMakingTsukiji（チャンネルID UCveAgsMJRwvfZNh3LF2AmLw、所有者 lovefootball624@gmail.com のGoogleログインで接続）
- Metricool必須項目：TikTokの`title`、YouTubeの`title`・`madeForKids`、Facebookリールの`title`
- YouTubeタイトル例：「Make Your Own Sushi with a Real Chef in Tsukiji, Tokyo 🍣」／カテゴリ TRAVEL_EVENTS

## 運用ルール
- **BGMはBGMライブラリ（`assets/bgm/`）の実際の無料音源を使う**：あなたが選んでPixabayなどからダウンロードした曲を保存し、動画ごとに`edit.json`の`bgm_file`で指定。尺合わせ・フェード・音量調整は自動
  - 現在のライブラリ：`optimistic-road-trip-loop-no2.mp3`（Pixabay / sonican、72秒）
  - 曲調の基準：競合のような「落ち着いてるけど楽しい、ハッピー」
  - 自動作曲（`pipeline/music.py`）は電子音っぽくなるので使わない（予備のみ）
- **元素材の音も入れる**：体験者の声・店内の音を各カットで音量をそろえて残す（BGMより少し大きめ）
- 最終音量は -14 LUFS（SNS向け標準）
- 完成動画＋英語の投稿キャプション＋ハッシュタグをセットで渡す
- フィードバックのたびにこのファイルを更新して次回に反映

## 制作の仕組み
- 素材一覧：`docs/footage_catalog.md`（素材本体は非公開リポジトリ sushi-footage の footage/）（92本、シーン別・★はおすすめカット）
- 動画ごとのカット表：`videos/<番号_テーマ>/edit.json`（どの素材の何秒からを何秒使うか＋テロップ）
- 書き出し：`python3 pipeline/build_reel.py videos/.../edit.json videos/.../reel_XXX.mp4`
- 素材を使い回す間は、同じカットが続けて使われないよう、動画ごとにテーマ（切り口）とカットの組み合わせを変える

## 投稿履歴
| No. | テーマ | フック | 主なカット |
|---|---|---|---|
| 001 | 初回投稿（体験の流れ） | MAKE YOUR OWN SUSHI IN TOKYO! | 時系列 |
| 002 | POV：自分で握る体験（BGM: optimistic-road-trip／2026-10-18 公開：IG Demmvgfj-Md／TikTok 7697683978794519815／FB reel 2391165585047117／YT shorts lROFlmEeX6U） | POV: You made your own sushi in Tsukiji | 8475_3, 8474, 8466, 8472, 8473, 8476_3, 8482, 8487 |

## 変更履歴
- v4：BGMをユーザー選曲の無料音源ライブラリ方式に変更（2026-10-17）
- v3：BGM自動作曲＋元素材の音を残す、締めに英語ナレーション（2026-10-17）
- v1：初回投稿（igexport-DdwYl23NlLl）の分析
- v2：ビジネス詳細、英語のみ、笑顔重視、操作画面での予約導線、他社参考（igexport-DGYAG2vBC14）のテロップスタイルを反映
