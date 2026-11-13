import json

with open("tests/10_sample_reports_data.json", "r", encoding="utf-8") as f:
    sample_reports = json.load(f)

with open("tests/10_complete_pairs_simulation_data.json", "r", encoding="utf-8") as f:
    pairs_data = json.load(f)

company_data = pairs_data["company"]
pairs_list = pairs_data["pairs"]

# マージして10名分の統合データを作成
merged_users = []
for p in pairs_list:
    no = p["no"]
    sr = next((item for item in sample_reports if item["no"] == no), None)
    
    user_obj = {
        "no": no,
        "id": p["id"],
        "user_type": p["user_type"],
        # 性格データ
        "personality": {
            "type_name": p["personality"]["full_name"],
            "base_type": p["personality"]["base_type"],
            "t_scores": p["personality"]["t_scores"],
            "style": p["personality"]["style"],
            "type_summary": sr["personality"]["type_summary"] if sr else "",
            "individual_uniqueness": sr["personality"]["individual_uniqueness"] if sr else "",
            "strengths": sr["personality"]["strengths"] if sr else [],
            "future_orientation": sr["personality"]["future_orientation"] if sr else [],
            "ideal_environments": sr["personality"]["ideal_environments"] if sr else []
        },
        # バリューデータ
        "values": {
            "top": p["values"]["top"],
            "high": p["values"]["high"],
            "culture_coords": p["values"]["culture_coords"],
            "culture_type": p["values"]["culture_type"],
            "quadrant": p["values"]["quadrant"],
            "value_summary": sr["values"]["value_summary"] if sr else "",
            "core_value": sr["values"].get("core_value_narrative", sr["values"].get("core_value", "")) if sr else "",
            "ideal_environments": sr["values"]["ideal_environments"] if sr else []
        },
        # マッチングデータ
        "match_analysis": p["match_analysis"],
        "company_view": p["company_view"],
        "student_view": p["student_view"]
    }
    merged_users.append(user_obj)

portal_data = {
    "company": company_data,
    "users": merged_users
}

json_str = json.dumps(portal_data, ensure_ascii=False)

html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Willoop 診断・マッチング 総合Webポータル</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Inter', 'Noto Sans JP', sans-serif;
    }}
    @keyframes pulse-ring {{
      0% {{ transform: scale(0.95); opacity: 0.8; }}
      50% {{ transform: scale(1.4); opacity: 0.2; }}
      100% {{ transform: scale(0.95); opacity: 0.8; }}
    }}
    .pulse-pin {{
      animation: pulse-ring 2.5s infinite ease-in-out;
    }}
    .pin-transition {{
      transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }}
    .custom-scroll::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scroll::-webkit-scrollbar-thumb {{
      background: #cbd5e1;
      border-radius: 9999px;
    }}
  </style>
</head>
<body class="bg-slate-50 text-slate-900 antialiased min-h-screen">

  <!-- グローバルナビゲーションバー -->
  <header class="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20 text-white font-black text-lg">
          W
        </div>
        <div>
          <span class="font-extrabold text-lg tracking-tight bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Willoop</span>
          <span class="text-xs text-slate-400 font-medium ml-1.5 hidden sm:inline">Culture & Personality Intelligence</span>
        </div>
      </div>

      <!-- 受検者切り替えセレクター -->
      <div class="flex items-center gap-2">
        <span class="text-xs font-semibold text-slate-500 hidden md:inline">受検者:</span>
        <select id="user-select" onchange="onSelectUserChange(this.value)" class="bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold py-2 px-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer">
        </select>
      </div>
    </div>

    <!-- メインビュー切り替えタブバー -->
    <div class="bg-white border-t border-slate-100 shadow-inner">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex overflow-x-auto custom-scroll gap-2 py-2">
        <button onclick="switchView('culture-map')" id="tab-btn-culture-map" class="view-tab-btn px-4 py-2 text-xs font-bold rounded-xl whitespace-nowrap transition-all flex items-center gap-2 bg-blue-600 text-white shadow-sm shadow-blue-500/20">
          <span>🗺️</span> 1. カルチャー重心マップ (新マトリクス)
        </button>
        <button onclick="switchView('student-diagnosis')" id="tab-btn-student-diagnosis" class="view-tab-btn px-4 py-2 text-xs font-bold rounded-xl whitespace-nowrap transition-all flex items-center gap-2 bg-slate-100 text-slate-600 hover:bg-slate-200">
          <span>🎓</span> 2. 学生マイページ 診断結果
        </button>
        <button onclick="switchView('company-match')" id="tab-btn-company-match" class="view-tab-btn px-4 py-2 text-xs font-bold rounded-xl whitespace-nowrap transition-all flex items-center gap-2 bg-slate-100 text-slate-600 hover:bg-slate-200">
          <span>🏢</span> 3. 企業マイページ 候補者推薦
        </button>
        <button onclick="switchView('student-match')" id="tab-btn-student-match" class="view-tab-btn px-4 py-2 text-xs font-bold rounded-xl whitespace-nowrap transition-all flex items-center gap-2 bg-slate-100 text-slate-600 hover:bg-slate-200">
          <span>🤝</span> 4. 学生マイページ 企業マッチ理由
        </button>
      </div>
    </div>
  </header>

  <!-- メインコンテンツ領域 -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

    <!-- 受検者プロファイルヘッダーカード -->
    <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-start sm:items-center gap-4">
        <div class="w-12 h-12 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center text-xl shrink-0">
          👤
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <span id="profile-user-id" class="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">candidate:26</span>
            <span id="profile-user-attr" class="text-xs font-semibold px-2 py-0.5 rounded-md bg-blue-50 text-blue-600 border border-blue-200">学生・求職者</span>
            <span id="profile-cluster-badge" class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-200">推進タイプ</span>
          </div>
          <h2 id="profile-full-type" class="text-lg font-extrabold text-slate-900 mt-1">周囲を牽引し構想を現実する推進タイプ</h2>
        </div>
      </div>

      <!-- 4特性偏差値バッジ -->
      <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
        <div class="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl text-center">
          <span class="text-[10px] text-slate-400 font-semibold block">社交性</span>
          <span id="badge-t-soc" class="text-sm font-extrabold text-slate-800">57.8</span>
        </div>
        <div class="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl text-center">
          <span class="text-[10px] text-slate-400 font-semibold block">好奇心</span>
          <span id="badge-t-cur" class="text-sm font-extrabold text-slate-800">67.7</span>
        </div>
        <div class="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl text-center">
          <span class="text-[10px] text-slate-400 font-semibold block">不安耐性</span>
          <span id="badge-t-str" class="text-sm font-extrabold text-slate-800">66.3</span>
        </div>
        <div class="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl text-center">
          <span class="text-[10px] text-slate-400 font-semibold block">着実性</span>
          <span id="badge-t-std" class="text-sm font-extrabold text-slate-800">46.2</span>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- ビュー1: カルチャー・ポジショニングマップ -->
    <!-- ========================================== -->
    <div id="view-culture-map" class="view-section grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- 2軸SVGマップ（左2カラム） -->
      <div class="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
        <div class="flex items-center justify-between text-xs">
          <div>
            <h3 class="font-extrabold text-sm text-slate-900">🧭 カルチャー重心ポジショニングマップ</h3>
            <span class="text-slate-400 text-xs">重視バリューから算出した「あなたのカルチャー現在地」</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="flex items-center gap-1.5 font-bold text-blue-600">
              <span class="w-3 h-3 rounded-full bg-blue-500 inline-block shadow-sm"></span> あなた (YOU)
            </span>
            <span class="flex items-center gap-1.5 font-bold text-emerald-600">
              <span class="w-3 h-3 rounded-full bg-emerald-500 inline-block shadow-sm"></span> 企業 (For Two)
            </span>
          </div>
        </div>

        <!-- 2軸SVGキャンバス -->
        <div class="relative w-full aspect-square max-h-[520px] bg-slate-50/70 rounded-2xl border border-slate-200 overflow-hidden">
          <svg viewBox="-105 -105 210 210" class="w-full h-full select-none">
            
            <!-- 4象限ゾーンカラー -->
            <rect x="-105" y="-105" width="105" height="105" fill="#ea580c" fill-opacity="0.05" />
            <rect x="0" y="-105" width="105" height="105" fill="#8b5cf6" fill-opacity="0.05" />
            <rect x="0" y="0" width="105" height="105" fill="#10b981" fill-opacity="0.05" />
            <rect x="-105" y="0" width="105" height="105" fill="#64748b" fill-opacity="0.04" />

            <!-- 十字ガイド軸 -->
            <line x1="-100" y1="0" x2="100" y2="0" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="3,3"/>
            <line x1="0" y1="-100" x2="0" y2="100" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="3,3"/>

            <!-- 象限背景ラベル -->
            <g opacity="0.65">
              <text x="-52" y="-55" text-anchor="middle" font-size="7" font-weight="bold" fill="#ea580c">🚀 革新・成果</text>
              <text x="-52" y="-46" text-anchor="middle" font-size="4.5" fill="#64748b">変革・スピード・突破</text>
              
              <text x="52" y="-55" text-anchor="middle" font-size="7" font-weight="bold" fill="#8b5cf6">🦅 自律・柔軟</text>
              <text x="52" y="-46" text-anchor="middle" font-size="4.5" fill="#64748b">自由・本質・心理的安全</text>

              <text x="52" y="48" text-anchor="middle" font-size="7" font-weight="bold" fill="#10b981">🤝 協調・共感</text>
              <text x="52" y="57" text-anchor="middle" font-size="4.5" fill="#64748b">感謝・丁寧・人の尊重</text>

              <text x="-52" y="48" text-anchor="middle" font-size="7" font-weight="bold" fill="#475569">🛡️ 安定・品質</text>
              <text x="-52" y="57" text-anchor="middle" font-size="4.5" fill="#64748b">計画性・秩序・確実性</text>
            </g>

            <!-- 軸先端ラベル -->
            <text x="0" y="-93" text-anchor="middle" font-size="5" font-weight="bold" fill="#1e293b">▲ 挑戦・変革・柔軟</text>
            <text x="0" y="97" text-anchor="middle" font-size="5" font-weight="bold" fill="#1e293b">▼ 着実・安定・規律</text>
            <text x="-95" y="2" text-anchor="start" font-size="5" font-weight="bold" fill="#1e293b">◀ 成果・タスク</text>
            <text x="95" y="2" text-anchor="end" font-size="5" font-weight="bold" fill="#1e293b">人・チーム ▶</text>

            <!-- 企業とユーザーの距離コネクター線 -->
            <line id="map-match-line" x1="0" y1="0" x2="0" y2="0" stroke="#3b82f6" stroke-width="1.8" stroke-dasharray="3,3" opacity="0.6"/>

            <!-- 企業ピン（For Two: X=+55, Y=+10） -->
            <g id="map-company-pin" transform="translate(55, -10)" class="pin-transition cursor-pointer">
              <circle r="12" fill="#10b981" fill-opacity="0.15" />
              <circle r="5" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
              <rect x="-24" y="-22" width="48" height="12" rx="4" fill="#ffffff" stroke="#10b981" stroke-width="1"/>
              <text y="-14" text-anchor="middle" font-size="5" font-weight="bold" fill="#0f172a">🏢 For Two</text>
            </g>

            <!-- ユーザーピン（動的アニメーション） -->
            <g id="map-user-pin" transform="translate(28, -48)" class="pin-transition cursor-pointer">
              <circle r="16" fill="#3b82f6" class="pulse-pin" />
              <circle r="6" fill="#3b82f6" stroke="#ffffff" stroke-width="2" />
              <rect x="-24" y="-24" width="48" height="13" rx="4" fill="#2563eb" />
              <text y="-15" text-anchor="middle" font-size="5.5" font-weight="bold" fill="#ffffff">YOU (あなた)</text>
            </g>

          </svg>
        </div>
      </div>

      <!-- 右側: カルチャータイプ判定 & マッチング解説 -->
      <div class="space-y-4">
        
        <!-- カルチャータイプカード -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">カルチャー判定</span>
            <span id="map-coords-badge" class="px-2 py-0.5 rounded text-xs font-mono font-bold bg-slate-100 text-slate-700">
              (X: 28, Y: 48)
            </span>
          </div>

          <div>
            <h3 id="map-type-title" class="text-lg font-black text-slate-900">🦅 自律・柔軟タイプ</h3>
            <p id="map-quadrant-desc" class="text-xs text-slate-500 mt-0.5">右上象限（挑戦・柔軟 × 人・チーム寄り）</p>
          </div>

          <div class="pt-2 border-t border-slate-100 space-y-1.5">
            <span class="text-[11px] font-bold text-slate-400">重視バリュー上位:</span>
            <div id="map-top-values" class="flex flex-wrap gap-1.5"></div>
          </div>
        </div>

        <!-- 企業との親和性カード -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">For Two との相性</span>
            <span id="map-fit-badge" class="px-2.5 py-0.5 rounded text-xs font-extrabold bg-blue-50 text-blue-600 border border-blue-200">
              補完フィット
            </span>
          </div>

          <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-700">カルチャー距離</span>
              <span id="map-distance-val" class="text-xs font-mono font-bold text-blue-600">43.8</span>
            </div>
            <p id="map-synergy-text" class="text-xs text-slate-600 leading-relaxed pt-1 border-t border-slate-200/60">
              人を大切にする根底の想い（心身の充足）を共有しながら、穏やかなチームに自律的な突破力をもたらす理想的な補完関係
            </p>
          </div>

          <div class="text-[11px] text-slate-500 leading-relaxed">
            🏢 **株式会社For Twoのカルチャー**: 協調・関係 × ウェルビーイング重視（X: 55, Y: 10）。温かい社風にあなたの個性がどう機能するかを分析しています。
          </div>
        </div>

      </div>

    </div>

    <!-- ========================================== -->
    <!-- ビュー2: 学生マイページ 診断結果 -->
    <!-- ========================================== -->
    <div id="view-student-diagnosis" class="view-section hidden space-y-6">
      
      <!-- サブタブ（パーソナリティ / バリュー） -->
      <div class="flex border-b border-slate-200 gap-4">
        <button onclick="switchDiagSubTab('p')" id="subtab-btn-p" class="pb-3 text-sm font-extrabold border-b-2 border-blue-600 text-blue-600 transition-all flex items-center gap-2">
          <span>🧠</span> あなたのパーソナリティ（行動様式）
        </button>
        <button onclick="switchDiagSubTab('v')" id="subtab-btn-v" class="pb-3 text-sm font-bold border-b-2 border-transparent text-slate-400 hover:text-slate-600 transition-all flex items-center gap-2">
          <span>💎</span> あなたのバリュー（大切にする価値観）
        </button>
      </div>

      <!-- パーソナリティタブ内容 -->
      <div id="diag-sub-p" class="space-y-6">
        
        <!-- 概要カード -->
        <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div>
            <span class="text-xs font-bold text-blue-600 uppercase tracking-wider">タイプ概要</span>
            <h3 id="diag-p-type-name" class="text-xl font-extrabold text-slate-900 mt-1">周囲を牽引し構想を現実する推進タイプ</h3>
            <p id="diag-p-summary" class="text-sm text-slate-600 mt-2 leading-relaxed"></p>
          </div>

          <div class="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <h4 class="text-xs font-bold text-slate-700 uppercase mb-1">このタイプの中での個性・立ち位置</h4>
            <p id="diag-p-unique" class="text-xs text-slate-600 leading-relaxed"></p>
          </div>
        </div>

        <!-- 強み ＆ これからの向き合い方 2カラム -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- 強み3点 -->
          <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-3">
            <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
              <span class="text-amber-500">★</span> あなたの強み（3点）
            </h4>
            <div id="diag-p-strengths" class="space-y-3"></div>
          </div>

          <!-- これからの向き合い方2点 -->
          <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-3">
            <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
              <span class="text-blue-500">💡</span> これからの向き合い方（2点）
            </h4>
            <div id="diag-p-future" class="space-y-3"></div>
          </div>

        </div>

        <!-- あなたが活きる環境3点 -->
        <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-3">
          <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
            <span class="text-emerald-500">🚩</span> あなたが活きる環境（任され方・チーム構成）
          </h4>
          <div id="diag-p-env" class="grid grid-cols-1 md:grid-cols-3 gap-3"></div>
        </div>

      </div>

      <!-- バリュータブ内容 -->
      <div id="diag-sub-v" class="hidden space-y-6">
        
        <!-- 最上位バリュー4枚カード -->
        <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div>
            <span class="text-xs font-bold text-indigo-600 uppercase tracking-wider">コアバリュー</span>
            <h3 class="text-lg font-extrabold text-slate-900 mt-1">あなたが最も大切にする価値観（TOP 4）</h3>
            <p id="diag-v-summary" class="text-sm text-slate-600 mt-1.5 leading-relaxed"></p>
          </div>

          <div id="diag-v-top4-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2"></div>
        </div>

        <!-- 大切にしていること要約文 -->
        <div class="bg-indigo-50/60 border border-indigo-200/80 rounded-2xl p-5 shadow-sm space-y-1.5">
          <span class="text-xs font-bold text-indigo-700 flex items-center gap-1.5">
            <span>✨</span> あなたが大切にしていること（要約）
          </span>
          <p id="diag-v-core-value" class="text-xs text-slate-700 leading-relaxed font-medium"></p>
        </div>

        <!-- あなたが活きる企業・カルチャー3点 -->
        <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-3">
          <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
            <span class="text-emerald-500">🚩</span> あなたが活きる企業（理念・評価風土）
          </h4>
          <div id="diag-v-env" class="grid grid-cols-1 md:grid-cols-3 gap-3"></div>
        </div>

      </div>

    </div>

    <!-- ========================================== -->
    <!-- ビュー3: 企業マイページ 候補者推薦カード -->
    <!-- ========================================== -->
    <div id="view-company-match" class="view-section hidden space-y-6">
      
      <!-- 推薦ハイライトバナー -->
      <div class="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-6 shadow-md space-y-2">
        <span class="text-xs font-bold uppercase tracking-wider text-blue-300">💡 推薦ハイライト（企業マイページ推薦枠）</span>
        <h3 id="comp-headline" class="text-xl sm:text-2xl font-black tracking-tight leading-snug"></h3>
        <p class="text-xs text-blue-200/90 pt-1">対象企業: 株式会社For Two（保育・育児IT）への推薦理由</p>
      </div>

      <!-- 3大評価項目グリッド -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- 1. バリュー共鳴 -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div class="space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <span class="font-extrabold text-sm text-slate-900">1. 価値観の共鳴ポイント</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-600">バリュー適合</span>
            </div>
            <div class="text-xs font-bold text-slate-500">
              共通バリュー: <span id="comp-overlap-val" class="text-blue-600"></span>
            </div>
            <p id="comp-overlap-exp" class="text-xs text-slate-600 leading-relaxed"></p>
          </div>
          <div class="text-[10px] text-slate-400 border-t border-slate-100 pt-2">理念やパーパスへの共感度合い</div>
        </div>

        <!-- 2. 現場・チーム親和性（案2形式） -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div class="space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <span class="font-extrabold text-sm text-slate-900">2. 現場・チームとの親和性</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-600">パーソナリティ適合</span>
            </div>
            <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800" id="comp-style-text">
            </div>
            <p id="comp-team-exp" class="text-xs text-slate-600 leading-relaxed"></p>
          </div>
          <div class="text-[10px] text-slate-400 border-t border-slate-100 pt-2">★はマッチングの要となる注目特性</div>
        </div>

        <!-- 3. マネジメント処方箋 -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div class="space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <span class="font-extrabold text-sm text-slate-900">3. 活躍を引き出す関わり方</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-600">育成処方箋</span>
            </div>
            <p id="comp-onboarding" class="text-xs text-slate-600 leading-relaxed"></p>
            <div class="space-y-2 pt-2 border-t border-slate-100">
              <span class="text-[11px] font-bold text-slate-700 block">おすすめ面接質問2選:</span>
              <div id="comp-questions-list" class="space-y-2"></div>
            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- ========================================== -->
    <!-- ビュー4: 学生マイページ 企業マッチ理由 -->
    <!-- ========================================== -->
    <div id="view-student-match" class="view-section hidden space-y-6">
      
      <!-- おすすめハイライトバナー -->
      <div class="bg-gradient-to-r from-indigo-800 to-purple-800 text-white rounded-2xl p-6 shadow-md space-y-2">
        <span class="text-xs font-bold uppercase tracking-wider text-purple-200">💡 おすすめハイライト（学生向け求人詳細枠）</span>
        <h3 id="stud-headline" class="text-xl sm:text-2xl font-black tracking-tight leading-snug"></h3>
        <p class="text-xs text-purple-200/90 pt-1">対象企業: 株式会社For Two（保育・育児IT）があなたに合う理由</p>
      </div>

      <!-- 3大解説グリッド -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- 1. カルチャーフィット -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div class="space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <span class="font-extrabold text-sm text-slate-900">1. 価値観の共鳴ポイント</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-50 text-purple-600">カルチャーフィット</span>
            </div>
            <div class="text-xs font-bold text-slate-500">
              共通バリュー: <span id="stud-overlap-val" class="text-purple-600"></span>
            </div>
            <p id="stud-culture-exp" class="text-xs text-slate-600 leading-relaxed"></p>
          </div>
          <div class="text-[10px] text-slate-400 border-t border-slate-100 pt-2">なぜこの会社で居心地良く働けるか</div>
        </div>

        <!-- 2. 強みが活きる現場 -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div class="space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <span class="font-extrabold text-sm text-slate-900">2. あなたの強みが活きる現場</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-600">パーソナリティフィット</span>
            </div>
            <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800" id="stud-role-title"></div>
            <p id="stud-workplace-exp" class="text-xs text-slate-600 leading-relaxed"></p>
          </div>
          <div class="text-[10px] text-slate-400 border-t border-slate-100 pt-2">チーム内での立ち位置と活躍イメージ</div>
        </div>

        <!-- 3. 働きやすさ & 逆質問 -->
        <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div class="space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <span class="font-extrabold text-sm text-slate-900">3. 伸び伸び働ける環境</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-600">逆質問サポート</span>
            </div>
            <p id="stud-growth-tips" class="text-xs text-slate-600 leading-relaxed"></p>
            <div class="space-y-2 pt-2 border-t border-slate-100">
              <span class="text-[11px] font-bold text-slate-700 block">面談・面接でのおすすめ逆質問:</span>
              <div id="stud-reverse-questions" class="space-y-2"></div>
            </div>
          </div>
        </div>

      </div>

    </div>

  </main>

  <!-- フッター -->
  <footer class="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-400">
    Willoop Diagnosis & Matching Engine • Generated from Production Prompts & Specifications
  </footer>

  <!-- スクリプト -->
  <script>
    const portalData = {json_str};
    const company = portalData.company;
    const users = portalData.users;

    let currentUserId = 1;
    let currentDiagSubTab = 'p';

    // 初期化
    window.addEventListener('DOMContentLoaded', () => {{
      // セレクターの選択肢を構築
      const select = document.getElementById('user-select');
      users.forEach(u => {{
        const opt = document.createElement('option');
        opt.value = u.no;
        opt.textContent = `No.${{u.no}} ${{u.id}}（${{u.personality.base_type}} / ${{u.values.culture_type.split('（')[0]}}）`;
        select.appendChild(opt);
      }});

      renderUser(1);
    }});

    function onSelectUserChange(val) {{
      renderUser(parseInt(val));
    }}

    function renderUser(no) {{
      currentUserId = no;
      const u = users.find(x => x.no === no);
      if (!u) return;

      // ヘッダープロファイル
      document.getElementById('profile-user-id').textContent = u.id;
      document.getElementById('profile-user-attr').textContent = u.user_type;
      document.getElementById('profile-cluster-badge').textContent = u.personality.base_type;
      document.getElementById('profile-full-type').textContent = u.personality.type_name;
      document.getElementById('badge-t-soc').textContent = u.personality.t_scores.社交性;
      document.getElementById('badge-t-cur').textContent = u.personality.t_scores.好奇心;
      document.getElementById('badge-t-str').textContent = u.personality.t_scores.不安耐性;
      document.getElementById('badge-t-std').textContent = u.personality.t_scores.着実性;

      // 1. カルチャーマップ
      const mapUserPin = document.getElementById('map-user-pin');
      mapUserPin.setAttribute('transform', `translate(${{u.values.culture_coords.x}}, ${{-u.values.culture_coords.y}})`);

      const mapLine = document.getElementById('map-match-line');
      mapLine.setAttribute('x1', u.values.culture_coords.x);
      mapLine.setAttribute('y1', -u.values.culture_coords.y);
      mapLine.setAttribute('x2', company.culture_coords.x);
      mapLine.setAttribute('y2', -company.culture_coords.y);

      document.getElementById('map-coords-badge').textContent = `(X: ${{u.values.culture_coords.x}}, Y: ${{u.values.culture_coords.y}})`;
      document.getElementById('map-type-title').textContent = u.values.culture_type;
      document.getElementById('map-quadrant-desc').textContent = u.values.quadrant;
      document.getElementById('map-fit-badge').textContent = u.match_analysis.fit_type;
      document.getElementById('map-distance-val').textContent = u.match_analysis.distance;
      document.getElementById('map-synergy-text').textContent = u.match_analysis.culture_synergy;

      const topValContainer = document.getElementById('map-top-values');
      topValContainer.innerHTML = u.values.top.map(v => `
        <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
          ${{v}}
        </span>
      `).join('');

      // 2. 個人診断結果
      document.getElementById('diag-p-type-name').textContent = u.personality.type_name;
      document.getElementById('diag-p-summary').textContent = u.personality.type_summary;
      document.getElementById('diag-p-unique').textContent = u.personality.individual_uniqueness;

      // 強み
      const pStrengths = document.getElementById('diag-p-strengths');
      pStrengths.innerHTML = u.personality.strengths.map(s => `
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <div class="text-xs font-bold text-slate-800">${{s.label}}</div>
          <p class="text-xs text-slate-600 mt-1 leading-relaxed">${{s.text}}</p>
        </div>
      `).join('');

      // 向き合い方
      const pFuture = document.getElementById('diag-p-future');
      pFuture.innerHTML = u.personality.future_orientation.map(f => `
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <div class="text-xs font-bold text-slate-800">${{f.label}}</div>
          <p class="text-xs text-slate-600 mt-1 leading-relaxed">${{f.text}}</p>
        </div>
      `).join('');

      // 環境
      const pEnv = document.getElementById('diag-p-env');
      pEnv.innerHTML = u.personality.ideal_environments.map(e => `
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <div class="text-xs font-bold text-slate-800">${{e.label}}</div>
          <p class="text-xs text-slate-600 mt-1 leading-relaxed">${{e.text}}</p>
        </div>
      `).join('');

      // バリュー
      document.getElementById('diag-v-summary').textContent = u.values.value_summary;
      document.getElementById('diag-v-core-value').textContent = u.values.core_value;

      const vTop4 = document.getElementById('diag-v-top4-grid');
      vTop4.innerHTML = u.values.top.map((v, i) => `
        <div class="p-3 rounded-xl border border-indigo-200 bg-indigo-50/40 text-center">
          <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-wider block">Rank ${{i+1}}</span>
          <span class="font-extrabold text-sm text-slate-800 mt-0.5 block">${{v}}</span>
        </div>
      `).join('');

      const vEnv = document.getElementById('diag-v-env');
      vEnv.innerHTML = u.values.ideal_environments.map(e => `
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-200">
          <div class="text-xs font-bold text-slate-800">${{e.label}}</div>
          <p class="text-xs text-slate-600 mt-1 leading-relaxed">${{e.text}}</p>
        </div>
      `).join('');

      // 3. 企業マイページ推薦
      document.getElementById('comp-headline').textContent = u.company_view.headline;
      document.getElementById('comp-overlap-val').textContent = u.company_view.value_resonance.overlap;
      document.getElementById('comp-overlap-exp').textContent = u.company_view.value_resonance.explanation;
      document.getElementById('comp-style-text').textContent = u.company_view.team_affinity.style;
      document.getElementById('comp-team-exp').textContent = u.company_view.team_affinity.explanation;
      document.getElementById('comp-onboarding').textContent = u.company_view.management_tips.onboarding;

      const compQuestions = document.getElementById('comp-questions-list');
      compQuestions.innerHTML = u.company_view.management_tips.questions.map((q, idx) => `
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1">
          <div class="text-xs font-bold text-slate-800 font-mono">${{idx+1}}. ${{q.q}}</div>
          <div class="text-[10px] text-slate-500">意図: ${{q.focus}}</div>
        </div>
      `).join('');

      // 4. 学生マイページ企業マッチ
      document.getElementById('stud-headline').textContent = u.student_view.headline;
      document.getElementById('stud-overlap-val').textContent = u.student_view.culture_fit.overlap;
      document.getElementById('stud-culture-exp').textContent = u.student_view.culture_fit.explanation;
      document.getElementById('stud-role-title').textContent = u.student_view.workplace_fit.role;
      document.getElementById('stud-workplace-exp').textContent = u.student_view.workplace_fit.explanation;
      document.getElementById('stud-growth-tips').textContent = u.student_view.growth_environment.tips;

      const studQuestions = document.getElementById('stud-reverse-questions');
      studQuestions.innerHTML = u.student_view.growth_environment.reverse_questions.map((q, idx) => `
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1">
          <div class="text-xs font-bold text-slate-800 font-mono">${{idx+1}}. ${{q.q}}</div>
          <div class="text-[10px] text-slate-500">狙い: ${{q.intent}}</div>
        </div>
      `).join('');
    }}

    function switchView(viewName) {{
      document.querySelectorAll('.view-section').forEach(sec => sec.classList.add('hidden'));
      document.querySelectorAll('.view-tab-btn').forEach(btn => {{
        btn.classList.remove('bg-blue-600', 'text-white', 'shadow-sm', 'shadow-blue-500/20');
        btn.classList.add('bg-slate-100', 'text-slate-600');
      }});

      const targetSec = document.getElementById(`view-${{viewName}}`);
      const targetBtn = document.getElementById(`tab-btn-${{viewName}}`);

      if (targetSec && targetBtn) {{
        targetSec.classList.remove('hidden');
        targetBtn.classList.remove('bg-slate-100', 'text-slate-600');
        targetBtn.classList.add('bg-blue-600', 'text-white', 'shadow-sm', 'shadow-blue-500/20');
      }}
    }}

    function switchDiagSubTab(tab) {{
      const pSec = document.getElementById('diag-sub-p');
      const vSec = document.getElementById('diag-sub-v');
      const pBtn = document.getElementById('subtab-btn-p');
      const vBtn = document.getElementById('subtab-btn-v');

      if (tab === 'p') {{
        pSec.classList.remove('hidden');
        vSec.classList.add('hidden');
        pBtn.classList.add('border-blue-600', 'text-blue-600');
        pBtn.classList.remove('border-transparent', 'text-slate-400');
        vBtn.classList.remove('border-blue-600', 'text-blue-600');
        vBtn.classList.add('border-transparent', 'text-slate-400');
      }} else {{
        vSec.classList.remove('hidden');
        pSec.classList.add('hidden');
        vBtn.classList.add('border-blue-600', 'text-blue-600');
        vBtn.classList.remove('border-transparent', 'text-slate-400');
        pBtn.classList.remove('border-blue-600', 'text-blue-600');
        pBtn.classList.add('border-transparent', 'text-slate-400');
      }}
    }}
  </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Successfully generated index.html!")
