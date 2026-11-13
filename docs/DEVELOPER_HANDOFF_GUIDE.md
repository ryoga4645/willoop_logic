# Willoop 診断・マッチングシステム 開発者向け完全実装ガイド（Developer Handoff Guide）

本ドキュメントは、Willoop（ウィループ）における「性格・価値観診断（自己理解）」および「学生 ↔ 企業 双方向カルチャーマッチング」を本番環境へ実装するエンジニアのための**総合開発仕様書**です。

---

## 1. システム全体概要 & 処理フロー

Willoopの診断・マッチングエンジンは、**「統計的スコア集計（決定的処理）」**と**「LLMによるパーソナライズ解説生成（生成処理）」**の2段階パイプラインで構成されます。

### 全体アーキテクチャ図

```mermaid
flowchart TD
    subgraph 1. 診断受検フェーズ
        A[ユーザーが診断受検<br/>P28問 + V42問] --> B[回答データを保存<br/>diagnosis_answers]
    end

    subgraph 2. 統計集計・判定フェーズ（決定的処理）
        B --> C[集計バッチ / API]
        C --> C1[P28問: 4特性Tスコア算出<br/>平均・標準偏差・逆転補正]
        C --> C2[4クラスタ中心値との距離計算<br/>推進・巻き込み・安定・慎重・特殊型判定]
        C --> C3[V42問: 42カード順位確定<br/>最上位4枚・高2枚・最下位2枚]
        C1 & C2 & C3 --> D[(集計結果保存<br/>diagnosis_scores)]
    end

    subgraph 3. AI解説文生成フェーズ（LLM処理）
        D --> E[API ①: 学生向け個人診断解説生成<br/>integrated_analysis_prompt.md]
        E --> F[(生成結果保存<br/>user_diagnosis_reports)]
    end

    subgraph 4. 双方向マッチングフェーズ（オンデマンド / キャッシュ）
        F & G[(企業データ<br/>companies)] --> H[API ②: 企業向け候補者推薦<br/>company_match_point_prompt.md]
        F & G --> I[API ③: 学生向け企業マッチ理由<br/>student_company_match_prompt.md]
        H --> J[(企業マイページ表示)]
        I --> K[(学生マイページ表示)]
    end
```

---

## 2. 引き継ぎ資料一覧（リポジトリ内インデックス）

本リポジトリに含まれる以下の資料を参照して実装を進めてください。

### ① プロダクション用プロンプト群（`prompts/`）
| ファイル名 | 推奨用途 | 概要 |
| :--- | :--- | :--- |
| [`prompts/integrated_analysis_prompt.md`](file:///Users/tarou/willoop_logic/prompts/integrated_analysis_prompt.md) | **API ①（本番標準）** | パーソナリティタブ＋バリュータブを**1回のAPI呼び出し**で一括生成する統合プロンプト |
| [`prompts/company_match_point_prompt.md`](file:///Users/tarou/willoop_logic/prompts/company_match_point_prompt.md) | **API ②（企業側）** | 企業マイページ推薦カード生成（**案2: 4特性定位置＋★ハイライト表記準拠**） |
| [`prompts/student_company_match_prompt.md`](file:///Users/tarou/willoop_logic/prompts/student_company_match_prompt.md) | **API ③（学生側）** | 学生マイページおすすめ企業マッチ理由＆カジュアル面談用逆質問生成 |
| [`prompts/personality_analysis_prompt.md`](file:///Users/tarou/willoop_logic/prompts/personality_analysis_prompt.md) | 個別API用 | パーソナリティ単体生成用（ストリーミングや単体再生成用） |
| [`prompts/value_analysis_prompt.md`](file:///Users/tarou/willoop_logic/prompts/value_analysis_prompt.md) | 個別API用 | バリュー単体生成用（ストリーミングや単体再生成用） |
| [`prompts/README.md`](file:///Users/tarou/willoop_logic/prompts/README.md) | 参照仕様 | UIスロット対応表、金太郎飴化防止ロジック、7大志向性一覧 |

### ② 集計アルゴリズム・統計ロジック仕様書
| ファイル名 | 概要 |
| :--- | :--- |
| [`パーソナリティフィット実装計画書.md`](file:///Users/tarou/willoop_logic/パーソナリティフィット実装計画書.md) | P28問の素点集計式、母集団平均値・標準偏差、4クラスタ中心値、ユークリッド距離計算式、特殊型判定の完全仕様 |
| [`バリューフィット実装計画書.md`](file:///Users/tarou/willoop_logic/バリューフィット実装計画書.md) | V42問の7大志向性分類、最上位〜最下位のカード重み付け、企業適合度スコアリング仕様 |

### ③ 設問・選択肢マスターデータ
| ファイル名 | 概要 |
| :--- | :--- |
| [`設問対応表_コードブック_全70問.csv`](file:///Users/tarou/willoop_logic/設問対応表_コードブック_全70問.csv) | P28問＋V42問の全設問文、因子マッピング、選択肢定義、逆転項目（Reverse flag）の完全マスター |

### ④ 学術的根拠・統計エビデンス（意思決定ログ）
| ファイル名 | 概要 |
| :--- | :--- |
| [`高本様_高原教授_メールやり取り一覧.md`](file:///Users/tarou/willoop_logic/高本様_高原教授_メールやり取り一覧.md) | 特殊型閾値（2.40）や中心値決定の学術的背景、統計分析に関する質疑応答ログ |
| [`高原教授_分析結果_result.xlsx`](file:///Users/tarou/willoop_logic/高原教授_分析結果_result.xlsx) | 因子分析・主成分分析・クラスタ分析の生データ（統計アルゴリズムの原典エビデンス） |

---

## 3. マスターデータ & DBテーブル設計ガイド

### 1. 設問マスター（`questions`）
[`設問対応表_コードブック_全70問.csv`](file:///Users/tarou/willoop_logic/設問対応表_コードブック_全70問.csv) をインポートしてテーブルを作成します。
- `id` (例: `P01` 〜 `P28`, `V01` 〜 `V42`)
- `type` (`personality` / `value`)
- `factor` (`社交性`, `好奇心`, `不安耐性`, `着実性`, またはバリュー志向性)
- `question_text` (設問文)
- `is_reversed` (boolean: 逆転項目の場合 `true`)
- `sort_order` (int)

### 2. 回答データ（`diagnosis_answers`）
- `user_id`
- `question_id`
- `score` (1〜5の整数)

### 3. 集計スコア（`diagnosis_scores`）
- `user_id`
- `personality_scores`: JSON
  - `t_sociability`: float（社交性Tスコア）
  - `t_curiosity`: float（好奇心Tスコア）
  - `t_stress_tolerance`: float（不安耐性Tスコア）
  - `t_steadiness`: float（着実性Tスコア）
  - `cluster_type`: string（`推進タイプ` / `巻き込みタイプ` / `安定タイプ` / `慎重タイプ`）
  - `is_special`: boolean（特殊型フラグ）
  - `distances`: JSON（各クラスタ中心値との距離）
- `value_scores`: JSON
  - `top_values`: string[]（最上位4枚）
  - `high_values`: string[]（高2枚）
  - `bottom_values`: string[]（最下位2枚）

---

## 4. スコア集計 & アルゴリズム実装仕様（LLM呼び出し前処理）

バックエンド（バッチまたは受検完了時API）で以下の統計処理を実装します。

### ① パーソナリティ 4特性Tスコア算出式
各特性（7問ずつ、計28問、1〜5点）の合計素点を算出します。
- **逆転項目補正**: `is_reversed == true` の設問は、スコアを `6 - score` に反転して加算。
- **Tスコア（偏差値）算出式**:
  $$T = 50 + 10 \times \frac{\text{素点合計} - \mu}{\sigma}$$

| 特性名 | 対象設問数 | 平均値 $\mu$ | 標準偏差 $\sigma$ |
| :--- | :---: | :---: | :---: |
| **社交性** | 7問 | **23.14** | **4.97** |
| **好奇心** | 7問 | **23.86** | **4.64** |
| **不安耐性** | 7問 | **20.52** | **4.75** |
| **着実性** | 7問 | **24.58** | **4.77** |

### ② 4クラスター中心値とのユークリッド距離計算
算出された4特性のTスコア空間において、以下の4つのクラスタ中心点とのユークリッド距離を計算します。

| クラスター | 社交性 | 好奇心 | 不安耐性 | 着実性 | 特徴 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **推進タイプ** | 56.0 | 58.6 | 55.6 | 59.5 | 目標達成・変革牽引 |
| **巻き込みタイプ** | 57.7 | 56.3 | 45.9 | 42.2 | 共感・ムードメイク・柔軟 |
| **安定タイプ** | 46.1 | 44.0 | 56.1 | 47.5 | 誠実・着実・フォロワーシップ |
| **慎重タイプ** | 39.3 | 40.1 | 40.8 | 49.9 | 計画的・リスク管理・品質重視 |

- **距離計算式**:
  $$D_k = \sqrt{\sum_{i=1}^{4} \left(\frac{T_i - C_{k,i}}{10}\right)^2}$$
  ※ 距離スケールを正規化するため、偏差値差を10で除算して2乗和の平方根を取ります。

### ③ 特殊型（例外タイプ）の判定ロジック
以下のいずれかの条件を満たす場合、基本タイプに加えて `is_special = true`（特殊型）としてフラグを立てます。
1. **中心値からの最短距離**:
   $$\min(D_k) \ge 2.40$$
   （4つの標準クラスタ中心のいずれからも一定以上離れている突出型）
2. **極端な偏差値ギャップ**:
   いずれかの特性Tスコアが $\ge 70$（上位2.3%）または $\le 30$（下位2.3%）であり、かつ特性間の最大差が 20以上 ある場合。

---

## 5. 3大AIエンドポイント実装仕様

### 【API ①】個人診断解説生成（`POST /api/v1/diagnosis/generate-report`）
受検完了時にバックエンドから呼び出します。

* **プロンプト**: [`prompts/integrated_analysis_prompt.md`](file:///Users/tarou/willoop_logic/prompts/integrated_analysis_prompt.md)
* **リクエストPayload（入力JSON）**:
```json
{
  "user_id": "candidate:26",
  "personality": {
    "trait_t_scores": {
      "社交性": 57.8,
      "好奇心": 67.7,
      "不安耐性": 66.3,
      "着実性": 46.2
    },
    "diagnosis_result": {
      "base_type": "推進タイプ",
      "full_name": "周囲を牽引し構想を現実する推進タイプ",
      "is_special": false
    },
    "highlight_questions": [
      {"q_no": 12, "text": "今までにやったことのない仕事をするとき、ワクワクする。", "score": 5},
      {"q_no": 20, "text": "締め切りの間際などプレッシャーのかかる場面でも、冷静さを保てる。", "score": 5}
    ]
  },
  "values": {
    "最上位": [
      {"name": "広い視野", "desc": "広い視野を持つ"},
      {"name": "本質志向", "desc": "本質志向である"},
      {"name": "自己受容", "desc": "自己受容している"},
      {"name": "心身の充足", "desc": "心身ともに健康で満たされている"}
    ],
    "高": [
      {"name": "計画性", "desc": "計画的に進める"},
      {"name": "目標達成", "desc": "目標・目的を達成する"}
    ],
    "最下位": [
      {"name": "上品さ", "desc": "上品に振る舞う"},
      {"name": "一生懸命", "desc": "何事にも一生懸命で全力を尽くす"}
    ]
  }
}
```

* **レスポンスPayload（出力JSON）**:
```json
{
  "personality": {
    "type_name": "周囲を牽引し構想を現実する推進タイプ",
    "type_summary": "高い好奇心と不安耐性を武器に...",
    "individual_unique": "推進タイプの中でも特に好奇心（67.7）が突出しており...",
    "strengths": [
      {"title": "未開拓領域への突破力", "body": "..."},
      {"title": "プレッシャー下での沈着冷静さ", "body": "..."},
      {"title": "大局観に基づいた意思決定", "body": "..."}
    ],
    "future_orient": [
      {"title": "着実な実行パートナーとの連携", "body": "..."},
      {"title": "プロセス共有による合意形成", "body": "..."}
    ],
    "ideal_environments": [
      {"title": "裁量権とミッションが明確な環境", "body": "..."},
      {"title": "前例のない挑戦を歓迎する風土", "body": "..."},
      {"title": "率直な意見交換ができるフラットなチーム", "body": "..."}
    ]
  },
  "values": {
    "top_4_values": [
      {"name": "広い視野", "reason": "..."},
      {"name": "本質志向", "reason": "..."},
      {"name": "自己受容", "reason": "..."},
      {"name": "心身の充足", "reason": "..."}
    ],
    "value_summary": "本質的な価値と持続可能性を追求する...",
    "core_value": "物事の表面にとらわれず、本質を見極めながら...",
    "ideal_environments": [
      {"title": "本質的な価値提供にこだわる事業環境", "body": "..."},
      {"title": "心理的安全性が高く個を尊重するカルチャー", "body": "..."},
      {"title": "持続可能な成長とウェルビーイングを両立する組織", "body": "..."}
    ]
  }
}
```

---

### 【API ②】企業マイページ推薦解説生成（`POST /api/v1/matches/company-view`）
企業担当者がスカウト一覧や候補者詳細を閲覧した際に呼び出します（結果はDBまたはCacheに保存推奨）。

* **プロンプト**: [`prompts/company_match_point_prompt.md`](file:///Users/tarou/willoop_logic/prompts/company_match_point_prompt.md)
* **重要仕様（案2準拠）**:
  - `team_affinity.style` は**「タイプ名（★社交性 xx.x / 好奇心 xx.x / ★不安耐性 xx.x / 着実性 xx.x）」**の形式を厳守すること（4特性固定順、解説の要となる特性に★を付与）。
* **リクエストPayload（入力JSON）**:
```json
{
  "company_profile": {
    "name": "株式会社For Two",
    "business": "保育・育児ITサービスの企画・開発・運営",
    "core_values": ["心身の充足", "人の尊重", "感謝", "丁寧さ", "質の高い対話"],
    "culture_memo": "心理的安全性が高く、お互いを思いやる家族的な温かい風土。一方で、新しい事業領域を切り拓く突破力を持った推進役を求めている。"
  },
  "candidate_profile": {
    "user_id": "candidate:26",
    "personality_type": "周囲を牽引し構想を現実する推進タイプ",
    "trait_t_scores": {
      "社交性": 57.8,
      "好奇心": 67.7,
      "不安耐性": 66.3,
      "着実性": 46.2
    },
    "top_values": ["広い視野", "本質志向", "自己受容", "心身の充足"]
  }
}
```

* **レスポンスPayload（出力JSON）**:
```json
{
  "headline": "温かい理念に深く共鳴しながら、事業を一段上へ押し上げる推進エンジン",
  "value_resonance": {
    "overlap": "『心身の充足』『本質志向』",
    "explanation": "貴社が重んじる「心身の健康や幸福」という根本思想に深く共感しつつ、物事の根本を見つめる『本質志向』を持っています。..."
  },
  "team_affinity": {
    "style": "推進タイプ（★社交性 57.8 / ★好奇心 67.7 / ★不安耐性 66.3 / 着実性 46.2）",
    "explanation": "調和的で穏やかなメンバーが多い貴社において、物怖じせず大局観を持って前へ進める本学生は貴重な「推進役（補完フィット）」となります。..."
  },
  "management_tips": {
    "onboarding": "全体像（ゴール）と裁量を与え、定期的に対話の時間を設けることで最も伸びます。マイクロマネジメントは避けてください。",
    "questions": [
      {
        "q": "「物事に取り組む際、周囲を巻き込んで新しい挑戦や改善を形にした経験はありますか？」",
        "focus": "推進力と周囲への配慮（巻き込み方）のバランスを確認します。"
      },
      {
        "q": "「心身のゆとりや充実感を保ちながら、高いパフォーマンスを出すために意識している工夫は何ですか？」",
        "focus": "『心身の充足』と『推進力』を実生活でどう調和させているかを確かめます。"
      }
    ]
  }
}
```

---

### 【API ③】学生マイページ企業マッチ理由生成（`POST /api/v1/matches/student-view`）
学生が企業詳細やおすすめ求人を閲覧した際に呼び出します。

* **プロンプト**: [`prompts/student_company_match_prompt.md`](file:///Users/tarou/willoop_logic/prompts/student_company_match_prompt.md)
* **リクエストPayload（入力JSON）**: API ②と対称なデータ構造（学生データ ＋ 閲覧中企業データ）。
* **レスポンスPayload（出力JSON）**:
```json
{
  "headline": "あなたの挑戦心を受け止め、本質的な価値提供に熱中できる最高の舞台",
  "culture_fit": {
    "overlap": "『心身の充足』『本質志向』",
    "explanation": "あなたが大切にしている「本質的な価値の追求」と「心身の健康」は、同社の理念そのものです。..."
  },
  "workplace_fit": {
    "role": "新しい風を吹き込む推進リーダー",
    "explanation": "穏やかで支え合う社風だからこそ、あなたの旺盛な好奇心と推進力が頼もしい突破力として歓迎されます。..."
  },
  "growth_environment": {
    "tips": "裁量を持って自律的に動ける環境です。目的を共有した上で自由にアプローチを試行錯誤できます。",
    "reverse_questions": [
      {
        "q": "「現場のメンバーが新しいアイデアや改善提案を出す際、どのようなステップで実現まで進めていますか？」",
        "intent": "自分の提案性や推進力を活かせる風土かどうかを確かめる質問です。"
      },
      {
        "q": "「チーム全体で『心身の充足』や健全な働き方を保つために、日常的に意識されている仕組みはありますか？」",
        "intent": "理念が現場の制度やカルチャーとして実態を伴っているかを確認する質問です。"
      }
    ]
  }
}
```

---

## 6. LLM実行環境・推奨設定

| 項目 | 推奨設定 | 理由・留意事項 |
| :--- | :--- | :--- |
| **推奨LLMモデル** | **GPT-4o** / **Claude 3.5 Sonnet** / **Gemini 1.5 Pro** | 複雑なパーソナリティ凹凸分析と表裏一体の心理的文脈を破綻なく生成するため |
| **Temperature** | **0.3 〜 0.5** | スコアに基づいた論理的整合性を保ちつつ、画一化（金太郎飴化）しない自然な表現力を両立させるため |
| **Output Format** | **`json_object` / Structured Outputs** | JSON形式の崩れを防ぎ、バックエンドのパース成功率を100%に保つため必須 |
| **Timeout 設定** | **30 秒** | 統合プロンプト（API ①）はトークン数が多いため、最低30秒のタイムアウトを設定 |
| **リトライ設計** | **最大2回（指数バックオフ）** | JSONパースエラー時やAPIタイムアウト時は、同一Payloadで自動リトライ |

---

## 7. 学術根拠・エビデンス資料の参照ガイド

開発時や運用中に「なぜこの仕様になっているのか？」という疑問が生じた場合は、以下のエビデンス資料を参照してください。

### ① 特殊型の判定基準（閾値 2.40）の背景
- **参照ファイル**: [`高本様_高原教授_メールやり取り一覧.md`](file:///Users/tarou/willoop_logic/高本様_高原教授_メールやり取り一覧.md)
- **背景要約**: 4クラスター中心値からの最短距離分布を分析した結果、全体の約5〜8%が中心点から外れた領域に位置します。高原教授との協議により、ユークリッド距離 $D \ge 2.40$ を「既存の4枠には収まらない独自性の高い特殊型」と定義することが合意されました。

### ② 4特性の理論的妥当性
- **参照ファイル**: [`高原教授_分析結果_result.xlsx`](file:///Users/tarou/willoop_logic/高原教授_分析結果_result.xlsx)
- **背景要約**: ビッグファイブ理論（外向性・開放性・情緒安定性・誠実性）を日本の新卒・採用現場向けに再構成（社交性・好奇心・不安耐性・着実性）した因子分析データが格納されています。

---

## 8. 保守・改修時の運用ルール

1. **タイムスタンプ付きバックアップの必須作成**:
   - プロンプトや仕様書を改修する際は、必ず事前に `<ファイル名>.YYYYMMDD_HHMMSS.bak` を作成すること。
2. **学生 ↔ 企業 「鏡合わせ（表裏一体）」の同期**:
   - 学生側プロンプトの項目構成や語彙を変更した場合は、必ず企業マイページ側プロンプト（`company_match_point_prompt.md`）との整合性を確認し、同時に改修すること。
3. **案2（4特性固定順＋★ハイライト）の厳守**:
   - 企業マイページ側の行動スタイル表記は、常に `社交性 / 好奇心 / 不安耐性 / 着実性` の順序を崩さず、キー特性に★を付与するルールを維持すること。

---
*初版作成日: 2026年11月13日 / 作成元: Willoop 開発プロジェクト*
