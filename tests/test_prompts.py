import csv
import json
import math

# 母集団パラメータ（パーソナリティフィット実装計画書より）
PARAMS = {
    'FAC1_社交性': {'mean': 3.257015, 'sd': 0.7915005},
    'FAC2_好奇心': {'mean': 3.302721, 'sd': 0.8653991},
    'FAC3_不安耐性': {'mean': 2.854592, 'sd': 0.7046661},
    'FAC4_着実性': {'mean': 3.437500, 'sd': 0.4978318}
}

CLUSTERS = {
    '安定タイプ': {
        'name': '自分のペースで着実に進める安定タイプ',
        't': [46.1, 44.0, 56.1, 47.5]
    },
    '慎重タイプ': {
        'name': '計画的に丁寧に積み上げる慎重タイプ',
        't': [39.3, 40.1, 40.8, 49.9]
    },
    '巻き込みタイプ': {
        'name': '自由な発想で変化を楽しむ巻き込みタイプ',
        't': [57.7, 56.3, 45.9, 42.2]
    },
    '推進タイプ': {
        'name': '周囲を牽引し構想を現実する推進タイプ',
        't': [56.0, 58.6, 55.6, 59.5]
    }
}

TRAIT_NAMES = ['社交性', '好奇心', '不安耐性', '着実性']

# コードブックの読み込み
codebook = {}
with open('設問対応表_コードブック_全70問.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        q_no = row.get('\ufeff設問通番') or row.get('設問通番')
        codebook[q_no] = {
            'type': row.get('診断種別'),
            'name': row.get('特性・価値観名'),
            'desc': row.get('設問文・補足説明')
        }

def diagnose(user_tscores, T_dist=2.40, M_dev=20.0):
    dist_list = []
    for c_id, c_info in CLUSTERS.items():
        diffs = [user_tscores[i] - c_info['t'][i] for i in range(4)]
        d = math.sqrt(sum((diff / 10.0) ** 2 for diff in diffs))
        dist_list.append((d, c_id, c_info, diffs))
    
    dist_list.sort(key=lambda x: x[0])
    min_dist, base_id, base_info, diffs = dist_list[0]
    max_dev = max(abs(x) for x in diffs)
    
    is_special = (min_dist >= T_dist) or (max_dev >= M_dev)
    
    features = []
    for i in range(4):
        diff = diffs[i]
        if diff >= 10.0:
            features.append(f"【{TRAIT_NAMES[i]}が突出して高い】")
        elif diff <= -10.0:
            if i == 2:
                features.append("【プレッシャーに対して繊細に向き合う】")
            else:
                features.append(f"【{TRAIT_NAMES[i]}が控えめ】")
                
    return {
        'base_type': base_id,
        'full_name': base_info['name'],
        'min_dist': round(min_dist, 2),
        'max_dev': round(max_dev, 1),
        'is_special': is_special,
        'features': features
    }

def analyze_sample_users():
    users = []
    with open('Willoop_診断回答データ_311名_横持ちワイド形式.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
            
    print(f"Total Users loaded: {len(users)}")
    
    # 代表的なユーザー（各タイプ1名 ＋ 特殊型1名）を探す
    found_types = {}
    special_user = None
    
    for row in users:
        uid = row.get('\ufeffuser_id') or row.get('user_id')
        user_type = row.get('user_type')
        
        # 4因子の素点平均
        # P_Q01〜P_Q08: 社交性
        fac1_raw = sum(float(row[f'P_Q{i:02d}_scored']) for i in range(1, 9)) / 8.0
        # P_Q09〜P_Q14: 好奇心
        fac2_raw = sum(float(row[f'P_Q{i:02d}_scored']) for i in range(9, 15)) / 6.0
        # P_Q15〜P_Q20: 不安耐性
        fac3_raw = sum(float(row[f'P_Q{i:02d}_scored']) for i in range(15, 21)) / 6.0
        # P_Q21〜P_Q28: 着実性
        fac4_raw = sum(float(row[f'P_Q{i:02d}_scored']) for i in range(21, 29)) / 8.0
        
        # 偏差値計算
        t1 = 50.0 + 10.0 * (fac1_raw - PARAMS['FAC1_社交性']['mean']) / PARAMS['FAC1_社交性']['sd']
        t2 = 50.0 + 10.0 * (fac2_raw - PARAMS['FAC2_好奇心']['mean']) / PARAMS['FAC2_好奇心']['sd']
        t3 = 50.0 + 10.0 * (fac3_raw - PARAMS['FAC3_不安耐性']['mean']) / PARAMS['FAC3_不安耐性']['sd']
        t4 = 50.0 + 10.0 * (fac4_raw - PARAMS['FAC4_着実性']['mean']) / PARAMS['FAC4_着実性']['sd']
        tscores = [t1, t2, t3, t4]
        
        res = diagnose(tscores)
        b_type = res['base_type']
        
        if res['is_special'] and special_user is None:
            special_user = (uid, user_type, tscores, res, row)
        elif not res['is_special'] and b_type not in found_types:
            found_types[b_type] = (uid, user_type, tscores, res, row)
            
        if len(found_types) == 4 and special_user is not None:
            break
            
    print("\n=== Representative Test Cases ===")
    test_cases = list(found_types.values())
    if special_user:
        test_cases.append(special_user)
        
    sample_inputs = []
    for uid, utype, tscores, res, row in test_cases:
        # バリューカード抽出 (V_Q29〜V_Q70)
        v_scores = {}
        for q in range(29, 71):
            val = int(row.get(f'V_Q{q}', 3))
            c_info = codebook.get(str(q), {'name': f'Q{q}', 'desc': ''})
            v_scores.setdefault(val, []).append({'name': c_info['name'], 'desc': c_info['desc']})
            
        input_data = {
            'user_id': uid,
            'user_type': utype,
            'personality': {
                'trait_t_scores': {
                    '社交性': round(tscores[0], 1),
                    '好奇心': round(tscores[1], 1),
                    '不安耐性': round(tscores[2], 1),
                    '着実性': round(tscores[3], 1)
                },
                'diagnosis_result': {
                    'is_special': res['is_special'],
                    'base_type': res['base_type'],
                    'full_name': res['full_name'],
                    'features': res['features'],
                    'distance': res['min_dist']
                }
            },
            'values': {
                '最上位': v_scores.get(5, [])[:3],
                '高': v_scores.get(4, [])[:5],
                '低': v_scores.get(2, [])[:3],
                '最下位': v_scores.get(1, [])[:2]
            }
        }
        sample_inputs.append(input_data)
        
        type_label = f"特殊型（{res['base_type']}）" if res['is_special'] else res['base_type']
        print(f"User: {uid} ({utype}) | Result: {type_label} | Dist: {res['min_dist']} | T: {[round(x,1) for x in tscores]}")
        print(f"  Top Values: {[x['name'] for x in input_data['values']['最上位']]}")
        print(f"  Bottom Values: {[x['name'] for x in input_data['values']['最下位']]}")
        print("-" * 50)
        
    with open('tests/sample_prompt_inputs.json', 'w', encoding='utf-8') as fp:
        json.dump(sample_inputs, fp, ensure_ascii=False, indent=2)
    print("Saved sample inputs to tests/sample_prompt_inputs.json")

if __name__ == '__main__':
    analyze_sample_users()
