import streamlit as st
import random
import uuid
import time

st.set_page_config(page_title="PTCG 純文字戰鬥版 v15", layout="wide", page_icon="⚔️")

# ==========================================
# 1. 樣式與顏色設定 (取代圖片)
# ==========================================
def get_type_color(card_type):
    colors = {
        "Darkness": "#2C3E50",  # 深灰/黑
        "Psychic": "#8E44AD",   # 紫色
        "Water": "#2980B9",     # 藍色
        "Grass": "#27AE60",     # 綠色
        "Fire": "#C0392B",      # 紅色
        "Lightning": "#F1C40F", # 黃色
        "Fighting": "#D35400",  # 橘褐
        "Metal": "#95A5A6",     # 銀灰
        "Colorless": "#BDC3C7", # 淺灰
        "Dragon": "#F39C12",    # 金橘
        "Trainer": "#F39C12",   # 訓練家金
        "Energy": "#16A085"     # 能量綠
    }
    return colors.get(card_type, "#7F8C8D")

def get_type_icon(card_type):
    icons = {
        "Darkness": "🌑", "Psychic": "🔮", "Water": "💧", "Grass": "🍃",
        "Fire": "🔥", "Lightning": "⚡", "Fighting": "👊", "Metal": "🔩",
        "Colorless": "⚪", "Dragon": "🐉", "Trainer": "🎒", "Energy": "⚡"
    }
    return icons.get(card_type, "❓")

# ==========================================
# 2. 完整卡片資料庫
# ==========================================
CARD_DB = {
    # --- 寶可夢 ---
    "瑪俐的長毛巨魔 ex": {
        "cat": "Pokemon", "stage": "Stage 2", "hp": 320, "type": "Darkness", "retreat": 2, 
        "weakness": "Grass", "resistance": None,
        "moves": [
            {"n": "不知夜", "cost": 1, "d": 0, "eff": "從牌庫找3張卡"},
            {"n": "暗影子彈", "cost": 3, "d": 180, "eff": "備戰區也受傷"}
        ]
    },
    "瑪俐的詐唬魔": {
        "cat": "Pokemon", "stage": "Stage 1", "hp": 100, "type": "Darkness", "retreat": 1, 
        "weakness": "Grass",
        "moves": [{"n": "推擊", "cost": 1, "d": 40, "eff": ""}]
    },
    "瑪俐的搗蛋小妖": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Darkness", "retreat": 1, 
        "weakness": "Grass",
        "moves": [{"n": "偷盜", "cost": 1, "d": 0, "eff": "丟棄對手手牌"}]
    },
    "願增猿": {
        "cat": "Pokemon", "stage": "Basic", "hp": 110, "type": "Psychic", "retreat": 1, 
        "weakness": "Darkness", "resistance": "Fighting",
        "ability": {"n": "腎上腺素腦", "desc": "移動傷害指示物"},
        "moves": [{"n": "精神歪曲", "cost": 2, "d": 60, "eff": "混亂"}]
    },
    "雪妖女": {
        "cat": "Pokemon", "stage": "Stage 1", "hp": 90, "type": "Water", "retreat": 1, 
        "weakness": "Metal",
        "ability": {"n": "凍結幕簾", "desc": "封鎖物品卡"},
        "moves": [{"n": "冰霜粉碎", "cost": 2, "d": 60, "eff": ""}]
    },
    "雪童子": {
        "cat": "Pokemon", "stage": "Basic", "hp": 60, "type": "Water", "retreat": 1, 
        "weakness": "Metal",
        "moves": [{"n": "寒意", "cost": 1, "d": 10, "eff": "無法撤退"}]
    },
    "月月熊 赫月 ex": {
        "cat": "Pokemon", "stage": "Basic", "hp": 260, "type": "Colorless", "retreat": 3, 
        "weakness": "Fighting",
        "moves": [{"n": "血月", "cost": 5, "d": 240, "eff": "下回合無法攻擊"}]
    },
    "含羞苞": {
        "cat": "Pokemon", "stage": "Basic", "hp": 30, "type": "Grass", "retreat": 0, 
        "weakness": "Fire",
        "moves": [{"n": "發現寶藏", "cost": 0, "d": 0, "eff": "找訓練家卡"}]
    },
    "可達鴨": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Water", "retreat": 1, 
        "weakness": "Lightning",
        "moves": [{"n": "過度思考", "cost": 1, "d": 0, "eff": "封鎖物品"}]
    },
    "米立龍": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Dragon", "retreat": 1, 
        "moves": [{"n": "衝浪", "cost": 2, "d": 50, "eff": ""}]
    },

    # --- 訓練家 ---
    "寶可平板": {"cat": "Trainer", "sub": "Item", "logic": "search_prize", "desc": "拿取一張獎賞卡"},
    "好友寶芬": {"cat": "Trainer", "sub": "Item", "logic": "search_deck", "desc": "找2張HP70以下基礎怪"},
    "夜間擔架": {"cat": "Trainer", "sub": "Item", "logic": "recover", "desc": "回收寶可夢或能量"},
    "神奇糖果": {"cat": "Trainer", "sub": "Item", "logic": "evolve", "desc": "基礎寶可夢直接進化2階"},
    "高級球": {"cat": "Trainer", "sub": "Item", "logic": "search_deck", "desc": "丟2張手牌找任意怪"},
    "能量轉移": {"cat": "Trainer", "sub": "Item", "logic": "move_energy", "desc": "移動場上能量"},
    "不公印章": {"cat": "Trainer", "sub": "Item", "logic": "disrupt", "desc": "雙方重洗手牌(氣絕時用)"},
    "氣球": {"cat": "Trainer", "sub": "Tool", "logic": "tool", "desc": "撤退費用-2"},
    
    "莉莉艾的決意": {"cat": "Trainer", "sub": "Supporter", "logic": "draw_to_6", "desc": "補滿手牌"},
    "火箭隊的拉姆達": {"cat": "Trainer", "sub": "Supporter", "logic": "search_deck", "desc": "找2張火箭隊牌"},
    "老大的指令": {"cat": "Trainer", "sub": "Supporter", "logic": "gust", "desc": "抓對手後台"},
    "丹瑜": {"cat": "Trainer", "sub": "Supporter", "logic": "discard_draw_5", "desc": "丟光手牌抽5張"},
    
    "尖釘鎮道館": {"cat": "Trainer", "sub": "Stadium", "logic": "stadium", "desc": "換位時受傷"},

    # --- 能量 ---
    "基本惡能量": {"cat": "Energy", "sub": "Basic", "desc": "惡屬性寶可夢的動力"}
}

ALL_DECKS = {
    "惡系強攻牌組": {
        "瑪俐的長毛巨魔 ex": 2, "瑪俐的詐唬魔": 2, "瑪俐的搗蛋小妖": 3, "願增猿": 3,
        "含羞苞": 1, "可達鴨": 1, "雪童子": 1, "雪妖女": 1, "月月熊 赫月 ex": 1,
        "米立龍": 1, "寶可平板": 2, "好友寶芬": 2, "夜間擔架": 2, "神奇糖果": 2,
        "能量轉移": 1, "高級球": 2, "氣球": 1, "莉莉艾的決意": 4,
        "老大的指令": 2, "火箭隊的拉姆達": 2, "丹瑜": 4, "基本惡能量": 10
    }
}

# ==========================================
# 3. 遊戲核心邏輯
# ==========================================

if 'game' not in st.session_state:
    st.session_state.game = None
    st.session_state.log = ["遊戲系統啟動 (文字版)。"]

def log_msg(msg):
    st.session_state.log.append(f"[{time.strftime('%H:%M')}] {msg}")

def create_card(name):
    base = CARD_DB.get(name)
    if not base: return None
    c = base.copy()
    c['id'] = str(uuid.uuid4())[:8]
    c['name'] = name
    if c['cat'] == 'Pokemon':
        c['damage'] = 0
        c['attached'] = []
    return c

def init_game():
    deck_list = []
    for name, count in ALL_DECKS["惡系強攻牌組"].items():
        for _ in range(count):
            card = create_card(name)
            if card: deck_list.append(card)
    
    random.shuffle(deck_list)
    p_hand = [deck_list.pop(0) for _ in range(7)]
    p_prizes = [deck_list.pop(0) for _ in range(6)]
    
    op_deck = deck_list.copy()
    random.shuffle(op_deck)
    op_active = create_card("瑪俐的搗蛋小妖")
    op_bench = [create_card("願增猿"), create_card("雪童子")]
    
    st.session_state.game = {
        "turn": 1,
        "supporter_used": False,
        "player": {
            "deck": deck_list, "hand": p_hand, "prizes": p_prizes,
            "active": None, "bench": [], "discard": []
        },
        "opponent": {
            "deck": op_deck, "hand": [1]*5, "prizes": [1]*6,
            "active": op_active, "bench": op_bench, "discard": []
        }
    }
    log_msg("遊戲開始！")

# ==========================================
# 4. 戰鬥邏輯
# ==========================================

def action_play_basic(card_idx):
    pl = st.session_state.game['player']
    card = pl['hand'][card_idx]
    if not pl['active']:
        pl['active'] = card
        pl['hand'].pop(card_idx)
        log_msg(f"前台出戰：{card['name']}")
    elif len(pl['bench']) < 5:
        pl['bench'].append(card)
        pl['hand'].pop(card_idx)
        log_msg(f"備戰區：{card['name']}")

def action_attach_energy(card_idx, target_loc, target_idx=None):
    pl = st.session_state.game['player']
    energy = pl['hand'][card_idx]
    target = pl['active'] if target_loc=='active' else pl['bench'][target_idx]
    target['attached'].append(energy)
    pl['hand'].pop(card_idx)
    log_msg(f"貼能給 {target['name']}")
    st.rerun()

def action_attack(move_idx):
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']
    if not pl['active']: return
    
    move = pl['active']['moves'][move_idx]
    cost = move['cost']
    current_en = len(pl['active']['attached'])
    
    if current_en < cost:
        st.toast(f"❌ 能量不足！需要 {cost}，目前 {current_en}")
        return

    damage = move['d']
    op_wk = op['active'].get('weakness')
    my_type = pl['active'].get('type')
    
    msg = f"{pl['active']['name']} 使用 {move['n']}！"
    if op_wk and my_type == op_wk:
        damage *= 2
        msg += " (弱點x2!)"
        
    op['active']['damage'] += damage
    log_msg(f"{msg} 造成 {damage} 傷害。")
    
    if op['active']['damage'] >= op['active']['hp']:
        log_msg(f"對手 {op['active']['name']} 氣絕！")
        op['discard'].append(op['active'])
        op['active'] = None
        if pl['prizes']:
            prize = pl['prizes'].pop(0)
            pl['hand'].append(prize)
            log_msg(f"拿取獎賞卡：{prize['name']}")

def action_play_trainer(card_idx):
    game = st.session_state.game
    pl = game['player']
    card = pl['hand'][card_idx]
    
    if card['sub'] == 'Supporter':
        if game['supporter_used']:
            st.toast("本回合已用過支援者"); return
        game['supporter_used'] = True
        
    logic = card.get('logic')
    if logic == 'draw_to_6':
        need = 6 - len(pl['hand']) + 1
        for _ in range(max(0, need)):
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg(f"使用 {card['name']} 補牌")
    elif logic == 'discard_draw_5':
        pl['discard'].extend(pl['hand'])
        pl['hand'] = []
        for _ in range(5):
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg(f"使用 {card['name']} 重抽")
    else:
        log_msg(f"使用 {card['name']}")
        
    pl['discard'].append(pl['hand'].pop(card_idx))
    st.rerun()

def end_turn():
    game = st.session_state.game
    game['turn'] += 1
    game['supporter_used'] = False
    pl = game['player']
    if pl['deck']:
        card = pl['deck'].pop(0)
        pl['hand'].append(card)
        log_msg(f"抽牌：{card['name']}")
    st.rerun()

# ==========================================
# 5. 無圖片渲染引擎 (CSS Card)
# ==========================================
def render_css_card(card, is_active=False):
    """用 HTML/CSS 畫出一張卡片"""
    if not card: return
    
    bg_color = get_type_color(card.get('type', card['cat']))
    icon = get_type_icon(card.get('type', card['cat']))
    text_color = "white"
    
    # 卡片內容 HTML
    html_content = f"""
    <div style="
        background-color: {bg_color}; 
        color: {text_color}; 
        border-radius: 10px; 
        padding: 10px; 
        margin: 5px; 
        border: 2px solid #ddd;
        min-height: 180px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    ">
        <div style="font-weight:bold; font-size:14px; border-bottom:1px solid rgba(255,255,255,0.3); padding-bottom:5px;">
            {icon} {card['name']}
        </div>
    """
    
    if card['cat'] == 'Pokemon':
        hp_cur = card['hp'] - card.get('damage', 0)
        html_content += f"""
        <div style="font-size:12px; margin-top:5px;">❤️ HP: {hp_cur}/{card['hp']}</div>
        <div style="font-size:12px;">⚡ 能量: {len(card.get('attached',[]))}</div>
        <div style="font-size:12px;">↩️ 撤退: {card.get('retreat',0)}</div>
        """
        # 顯示招式
        if 'moves' in card:
            html_content += "<div style='margin-top:8px; font-size:11px; background:rgba(0,0,0,0.2); padding:3px; border-radius:4px;'>"
            for m in card['moves']:
                html_content += f"<div>💥 {m['n']} ({m['d']})</div>"
            html_content += "</div>"
            
    elif card['cat'] == 'Trainer':
        html_content += f"""
        <div style="font-size:11px; margin-top:5px; font-style:italic;">{card.get('sub')}</div>
        <div style="font-size:11px; margin-top:5px; background:rgba(0,0,0,0.1); padding:5px; border-radius:5px;">
            {card.get('desc', '無說明')}
        </div>
        """
        
    elif card['cat'] == 'Energy':
        html_content += f"""
        <div style="font-size:30px; text-align:center; margin-top:20px;">⚡</div>
        <div style="text-align:center; font-size:12px;">提供1個能量</div>
        """
        
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)

# ==========================================
# 6. 遊戲介面
# ==========================================

if st.session_state.game is None:
    st.title("PTCG 純文字戰鬥版 v15")
    st.info("此版本無需圖片，卡片樣式由程式碼自動生成！")
    if st.button("🚀 開始遊戲"):
        init_game()
        st.rerun()
else:
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']

    # 側邊欄
    with st.sidebar:
        st.header(f"第 {game['turn']} 回合")
        if st.button("🔚 結束回合"): end_turn()
        st.divider()
        st.write("📜 紀錄")
        for l in reversed(st.session_state.log[-8:]): st.caption(l)
        if st.button("重置"): st.session_state.game=None; st.rerun()

    # 對手區
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 😈 對手前台")
        if op['active']: render_css_card(op['active'], True)
        else: st.warning("空")
    with col2:
        st.markdown("### 對手備戰區")
        cols = st.columns(5)
        for i, c in enumerate(op['bench']):
            with cols[i]: render_css_card(c)

    st.markdown("---")

    # 玩家區
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 🛡️ 你的備戰區")
        cols = st.columns(5)
        for i, c in enumerate(pl['bench']):
            with cols[i]: render_css_card(c)
            
    with col2:
        st.markdown("### ⚔️ 你的前台")
        if pl['active']:
            render_css_card(pl['active'], True)
            # 攻擊選單
            moves = pl['active']['moves']
            move_names = [f"{m['n']} ({m['d']})" for m in moves]
            sel_move = st.selectbox("選擇招式", range(len(moves)), format_func=lambda x: move_names[x])
            if st.button("💥 攻擊"):
                action_attack(sel_move)
                st.rerun()
                
            if st.button("🏳️ 撤退"):
                pl['discard'].append(pl['active'])
                pl['active'] = None; st.rerun()
        else:
            st.warning("請派怪上場")

    st.markdown("---")
    st.subheader(f"✋ 手牌區 ({len(pl['hand'])})")
    
    # 手牌顯示
    if pl['hand']:
        rows = [pl['hand'][i:i+6] for i in range(0, len(pl['hand']), 6)]
        for r_idx, row in enumerate(rows):
            cols = st.columns(6)
            for c_idx, card in enumerate(row):
                idx = r_idx * 6 + c_idx
                with cols[c_idx]:
                    render_css_card(card)
                    
                    # 操作按鈕
                    c1, c2 = st.columns(2)
                    with c1:
                        if card['cat'] == 'Pokemon' and card.get('stage') == 'Basic':
                            if st.button("⬆️", key=f"p_{idx}"): action_play_basic(idx); st.rerun()
                        elif card['cat'] == 'Trainer':
                            if st.button("✨", key=f"t_{idx}"): action_play_trainer(idx)
                        elif card['cat'] == 'Energy':
                            if st.button("⚡", key=f"e_{idx}"): action_attach_energy(idx, 'active')
                    with c2:
                        if st.button("🗑️", key=f"d_{idx}"):
                            pl['discard'].append(pl['hand'].pop(idx)); st.rerun()