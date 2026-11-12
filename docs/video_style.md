# 寿司体験リール 型（v5）

## ビジネス前提
- 築地で実際に営業している寿司店のカウンターで、訪日外国人向けに握り体験を提供
- 集客：Instagram / Facebook / TikTok / YouTube の短尺動画 → プロフのリンク → 自社予約サイトで予約
- 見るのは外国人のみ。テロップも投稿キャプションも**すべて英語、日本語なし**
- テロップ文言・投稿キャプションは毎回こちらで考えてOK（サービスにちなんだ内容で）

## 映像の方針
- 主役は**体験しているゲストの笑顔**。握る瞬間、食べた瞬間のリアクション、乾杯、集合写真を優先して使う
- 縦 9:16、1080x1920、25〜30秒、1カット1〜2秒
- 素材の質感（築地の本物のカウンター、職人、日本酒）は残す
- **色味は撮影したままのオリジナル（色の加工をしない）**（しゅん指定 2026-11-12。オレンジ寄り・濃いめなど加工した004初版は「色合いが悪すぎる」として全SNSから削除→作り直し）。edit.json に `"original_color": true` を入れる
- **iPhoneのHDR（HLG／Dolby Vision）素材は必ずSDRにトーンマップする**（11/10素材から該当。11/4以前はSDR）。変換しないと白っぽく色が抜け、色を足すほど不自然になる。build_reel.py が素材の color_transfer を見て自動で mobius トーンマップを入れる。新しい素材は取り込み時に `ffprobe -show_entries stream=color_transfer` で確認する
- **カットの順番は実際の体験工程どおり**（しゅん指定 2026-11-07）：シャリ切り → 職人に教わる → 握り → 巻物 → 盛り付け → 実食。後の工程のカットを冒頭に持ってこない
- 2人以上映るカットは、全員の表情（笑顔）を確認してから使う

## 構成テンプレ
1. **フック（0–2s）**：一番の笑顔 or 握りのアップ＋大きめのテロップ
2. **体験の流れ（2–20s）**：職人の手元 → ゲストが握る → 食べる → 乾杯。テロップで短いストーリーを語る
3. **締め（20–24s）**：集合写真＋「See you in Tsukiji」系の一言
4. **予約導線（最後の4〜5s）**：実際の操作画面で「プロフ → リンク → Book」を見せる。タップ位置に赤丸＋矢印

## テロップ
- 参考：初回投稿（白文字・小さめ・中央）と他社参考（太字・縁取り・キーワードだけ黄色・一文ずつ語る形式）
- v2で採用：**太字の白文字＋黒縁取り、キーワードを黄色ハイライト**、画面の中央〜やや下（下端のUIエリアは避ける）
- 一文ずつ短く区切ってテンポよく切り替える
- **食べる場面の文言は「自分で作った寿司を食べる」と必ず伝える**（しゅん指定 2026-11-12。例：「Then eat the sushi you made」「Your own nigiri, so good!」）。職人が作ったものを食べるように読める書き方はしない。キャプションも同じ
- **テロップは基本「いつもの」白の太字＋黒縁＋黄色ハイライト**（しゅん指定 2026-11-12 最終。004で下のSNSネイティブ・ステッカー等を試したが、最後は「テロップだけいつものやつに」となった）。下の別スタイルは、しゅんから変えたいと言われたときだけ使う
- **テロップ「SNSネイティブ」**（004で最終採用、しゅん指定 2026-11-12「わかりやすく、外国人が好きで見やすい感じ」）：TikTok/Instagramの標準テロップと同じ、白い角丸の吹き出しに黒の太字。キーワードはオレンジ、行末に絵文字1つ（`"emoji"`）。`"anim": "native"`、size 68〜74、y 1240。ふわっと弾んで出る。上部の飾り（進行バー・バッジ・章ラベル）は使わない
- **テロップ「ステッカー」**（004で採用、しゅん指定 2026-11-12。デザイン案A タイプライター／B ステッカー／C 大きな1語 を出してBに）：`"text_style": "kinetic"` で各beatを `"anim": "sticker"`。1行ずつ少し傾いたシール（普通の行はクリーム地に紺、`**…**` を含む行はロゴの赤地に白）が弾んで出る。傾きは行・beatごとに左右交互。上部の進行バー・場所バッジ・章ラベルは**使わない**（しゅん「上のデザインは無し」）。A（`type`）と C（`big`）も `pipeline/kinetic.py` にあり、回ごとに使い分けて飽きさせない
- **動くテロップ「kinetic」**（004で採用、しゅん指定 2026-11-12「見る人が飽きないテロップの使い方・見せ方に。デザイン追加OK」）：edit.json に `"text_style": "kinetic", "kinetic": {"badge": "TSUKIJI · TOKYO", "progress": true}`。beatごとに `anim`（pop＝単語が弾んで出る／stamp＝大きく押し込む／slide＝左から滑り込む／marker＝キーワードにオレンジのマーカーが引かれる）、`chapter`（左上の「01 SUIT UP」などの章ラベル）、`y`（位置）を変えて、同じ見せ方が続かないようにする。上部にオレンジの進行バー、右上に場所バッジ。白の極太文字＋影、キーワードはオレンジ。仕組みは `pipeline/kinetic.py`
- **別スタイル「ラベル」**（004で採用、しゅん指定 2026-11-12「テロップの入れ方・色を変えて雰囲気を変えて」）：edit.json に `"text_style": "label", "text_y": 1260` を入れると、1行ずつクリーム色の角丸ボックスに紺の文字、`**語**` はロゴの赤。size は 74〜80。回ごとに縁取り白文字と使い分けて雰囲気を変える
- **テロップで体験の工程（Step 1: shape your nigiri／roll a sushi roll など）を説明しない**（しゅん指定 2026-11-12、005）。流れは映像で見せ、テロップはその場の気持ち・雰囲気の一言にする（例：Our best night in Tokyo／Laughing the whole time／Made with our own hands／Look what we made!）。食べる場面の「自分で作った寿司を食べる」文言だけは残す
- **板前が包丁で切る・たたく場面は、しゅんから求められない限り入れない**（005で「別のに差し替えて」。004では逆に伸ばしてと言われたので、迷ったらゲストの場面を優先）
- 表記の正確さを毎回チェック（Tsukiji, Japanese など）

## 予約導線パート（全SNS共通）
- **Webサイト部分のみ**を使い、全プラットフォームで同じ締めにする（SNSのプロフ画面は映さない）
- 完成済みクリップ：`assets/cta_booking.mp4`（ナレーション入りで約6秒、1080x1920）。毎回これを最後に付けるだけ
  - 「Tap the link in our bio」→ サイトのトップ〜スクロール →「Hit BOOK NOW」（赤丸＋矢印）→「Pick your date / See you in Tsukiji!」で予約画面
  - 背景はサイトと同じクリーム色、文字はサイトの紺＋ロゴの赤
  - **英語ナレーション入り**（AI音声 Kokoro / af_heart・アメリカ英語の女性）：「Tap the link in our bio. / Hit Book Now! / Pick your date, and see you in Tsukiji!」を各ステップの頭に配置。約6秒
  - ナレーションの再生成：`pipeline/tts.py`（発音記号で入力）
- 作り直しスクリプト：`pipeline/build_cta.py assets/source/booking_screen_recording.mp4 assets/cta_booking.mp4`
- サイトのデザインが変わったら画面録画を撮り直して再生成

## 投稿キャプション
- **英語対応はうたってよいが、英語を話すのはスタッフで板前ではない**（しゅん指定 2026-11-12）。「English-speaking chef」のように板前が英語を話すと読める表現は使わず、「English-speaking staff」「friendly English support」などにする。ほかの安心材料：No experience needed／beginners welcome／real sushi counter in Tsukiji
- ※スキル（sushi-reel-production）には「英語対応をうたわない」と書いたが、こちらが最新（英語対応＝スタッフならOK）
- **カバーは文字入りのカバー専用画像も作れる**（しゅん指定 2026-11-12、004で採用）：しゅんが選んだ場面を元素材から書き出し（動画のテロップは入れない）、いつものテロップ形式でカバー用の一言（例「Be a sushi chef in Tsukiji」）を入れて、リポジトリ直下に cover_XXX.jpg として push し、Metricool の `videoThumbnailUrl` に raw URL を渡す（videoCoverMilliseconds の代わり）。TikTok・YouTubeはアカウントの種類によって反映されないことがある。**YouTubeは実際に失敗した**（004、2026-11-12：動画は公開されたがMetricoolから「Could not upload its thumbnail」のエラーメール）。YouTubeのカバーは投稿後にしゅんがYouTube Studio／YouTubeアプリで手動設定する前提で、カバー画像をしゅんに渡しておく。**005から、YouTubeはIG・FB・TikTokとは別の予約にしてカバー（videoThumbnailUrl／videoCoverMilliseconds）を付けない**（失敗メールを避けるため）
- **カバーはしゅんに候補（A/B）を見せて選んでもらう**（005：しゅんが「この場面の元クリップから一番いいところ」と指定→同じクリップから2コマ作って選択）
- **カバーは動画ごとに一番いい笑顔の場面を選び、4SNSで統一**（004は20秒地点＝2人の笑顔と締めのテロップ。videoCoverMilliseconds に秒×1000を入れる）。冒頭0.8秒固定ではない
- **キャプションで体験の工程（着替え→職人→握り→食べる…）を順に説明しない**（しゅん指定 2026-11-12）。動画で見せている流れはテロップに任せ、キャプションはゲストへの感謝・その夜の雰囲気・安心材料など別のことを書く
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
- 投稿結果の確認は**投稿翌朝の日本時間9:15**（2:00投稿なら同じ日の9:15）。夜中に通知しないため
- **公開済みの投稿のカバーや動画はMetricoolから変更できない**：直す必要があれば、そのSNSだけ再投稿する（再投稿の前に必ずしゅんのOKをもらう）。古い投稿の削除はしゅんに頼む
- Metricoolの画面の表示タイムゾーンがマドリードのままだと、正しい予約にも「Publish date can't be a past date」と出る。実際の予約は getScheduledPosts で確認する
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

## 素材の受け取り
- 素材は、寿司体験用Googleドライブ「08_写真・動画素材 › <撮影日> › 動画/」から取る（2026/10/21〜）。撮影日の直下に動画と写真が混ざっていたら、こちらで「動画」「写真」フォルダに分けてよい（2026/11/7 しゅん指示。移動だけで、削除・名前変更はしない）。チャットに直接添付されたときは例外扱い（開催日を聞いてから同じ名前の付け方で取り込む）
- Driveコネクタは1ファイル10MBまでしか取り出せない。それを超える動画は、しゅんのMacのChromeでフォルダごとダウンロード（~/Downloads/sushi_<YYYYMMDD>/）→ Macのフォルダから取り込む
- GitHubは1ファイル100MBまで。90MBを超える素材は1080p・HEVC（crf 26）に縮めて保存
- `写真/` など `動画/` 以外のフォルダは使わない
- 素材フォルダは、スケジュール済みタスク「寿司体験 新しい素材で動画を自動作成（毎日）」（日本時間11:17）が毎日確認し、新しい撮影日があれば取り込み→動画作成→しゅんに確認依頼まで進める（2026/11/7 しゅん指示）。投稿はしゅんのOK後だけ。しゅんが「動画作って」と言ったときもその場で行う
- `footage_catalog.md` の「取り込み済みの開催日」に無い日付フォルダを新しい素材とする。新しい日付フォルダが見つからないときは、作業を止めてフォルダ名を確認する
- 新しい素材は非公開リポジトリ sushi-footage の `footage/` に `<開催日YYYYMMDD>_<元の名前>` の形で保存する（公開の sushi-reels には置かない）。デスクトップのファイルは動かさない・消さない
- 新しい開催日の素材を主役にして、足りないカットだけ過去の素材で補う。**なるべくその日の素材だけで構成し、他の日の素材は最後の手段**（しゅん指定 2026-11-12。004では握りの2カットだけ11/4から補った）

## 制作の仕組み
- 素材一覧：`docs/footage_catalog.md`（素材本体は非公開リポジトリ sushi-footage の footage/）（開催日ごと・シーン別、★はおすすめカット。取り込み済みの開催日の一覧もここ）
- 動画ごとのカット表：`videos/<番号_テーマ>/edit.json`（どの素材の何秒からを何秒使うか＋テロップ）
- 書き出し：`python3 pipeline/build_reel.py videos/.../edit.json videos/.../reel_XXX.mp4`
- 素材を使い回す間は、同じカットが続けて使われないよう、動画ごとにテーマ（切り口）とカットの組み合わせを変える

## 投稿履歴
| No. | テーマ | 使った開催日 | フック | 主なカット |
|---|---|---|---|---|
| 001 | 初回投稿（体験の流れ） | — | MAKE YOUR OWN SUSHI IN TOKYO! | 時系列 |
| 002 | POV：自分で握る体験（BGM: optimistic-road-trip／2026-10-18 公開：IG Demmvgfj-Md／TikTok 7697683978794519815／FB reel 2391165585047117／YT shorts lROFlmEeX6U）※FBはカバー修正のため3:08に、YouTubeは2:58に再投稿。古い投稿（FB reel 1429328741989688・YT shorts gvVJgArSHZw）は削除済み | 9:16（以前の素材） | POV: You made your own sushi in Tsukiji | 8475_3, 8474, 8466, 8472, 8473, 8476_3, 8482, 8487 |
| 003 | 初めての寿司づくり（体験工程どおり。BGM: optimistic-road-trip／2026-11-08 2:00 公開：IG DfcrlNcjhtQ／TikTok 7705477187322891541／FB reel 2557540424768225／YT shorts 87vvqzozYLQ）色味は8912基準の自然な色 | 2026-11-04 | His first time making sushi | 8883, 8908, 8911, 8905, 8904, 8912, 8919, 8923, 8914, 7681, 7688 |
| 004 | Tonight, you're the sushi chef（ゲストがその夜の職人に。BGM: optimistic-road-trip／2026-11-12 3:04 公開：IG DfnF3dECUia／TikTok 7706977662203514130／FB reel 1478065584251692／YT shorts dvArBO1JIHI）カバーは文字入りのカバー画像 cover_004_A.jpg（職人が霜降りの身を手に乗せている場面＋「Be a sushi chef in Tsukiji」、videoThumbnailUrlで指定。YouTubeは「Could not upload video thumbnail」の警告でカバー未反映）。色はオリジナル（HDRをトーンマップ）、テロップはいつもの白文字＋黒縁。※11/12 2:00の初版は色が悪く、しゅんが全SNSから削除して3:04に再投稿 | 2026-11-10 | Tonight, you're the sushi chef | 20261110_IMG_7738, 7739, 7740, 7741 |
| 005 | Look what we made（2人の女性ゲストが握り・巻き寿司を作って盛り合わせを自慢。BGM: optimistic-road-trip／2026-11-13 2:00 予約：IG・FB・TikTok はカバー画像 cover_005.jpg（盛り合わせを持つ2人の寄り＋「Look what we made in Tsukiji!」、しゅんがA/Bから選択）を videoThumbnailUrl で、YouTube は別予約でカバー指定なし→投稿後にしゅんが手動で差し替え）。色はオリジナル、テロップはいつもの形・工程説明なし | 2026-11-11 | Our best night in Tokyo | 20261111_IMG_7754, 7756, 7763, 7762, 7764, 7771, 7767, 7775, 7773, 7774, 7779, 7780, 7781 |

## 変更履歴
- v5：素材の受け取り方（デスクトップの開催日フォルダ・声をかけられたときだけ確認）、投稿結果の確認時刻、公開後の修正ルールを追記。投稿履歴に「使った開催日」の欄を追加（2026-10-18）
- v4：BGMをユーザー選曲の無料音源ライブラリ方式に変更（2026-10-17）
- v3：BGM自動作曲＋元素材の音を残す、締めに英語ナレーション（2026-10-17）
- v1：初回投稿（igexport-DdwYl23NlLl）の分析
- v2：ビジネス詳細、英語のみ、笑顔重視、操作画面での予約導線、他社参考（igexport-DGYAG2vBC14）のテロップスタイルを反映
