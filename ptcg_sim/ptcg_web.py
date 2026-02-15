import streamlit as st
import random
import uuid
import time
import os

# ==========================================
# 1. CSS 樣式 (用於圖片讀取失敗時的備案)
# ==========================================
st.set_page_config(page_title="PTCG 圖片對戰系統", layout="wide", page_icon="🃏")

st.markdown("""
<style>
    /* 卡片容器 */
    .card-container {
        width: 100%; height: auto;
        border-radius: 10px; padding: 2px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        transition: transform 0.2s; cursor: pointer;
        background-color: transparent;
    }
    .card-container:hover { transform: scale(1.05); z-index: 10; }
    
    /* 這是給沒有圖片時顯示用的 CSS 樣式 */
    .css-card {
        height: 160px; border-radius: 8px; padding: 5px; color: white;
        display: flex; flex-direction: column; justify-content: space-between;
        text-align: center; border: 2px solid #fff;
    }
    .bg-Darkness { background: linear-gradient(135deg, #3c3c3c, #1a1a1a); border-color: #705898; }
    .bg-Water { background: linear-gradient(135deg, #6890F0, #98D8D8); border-color: #6890F0; color: black; }
    .bg-Grass { background: linear-gradient(135deg, #78C850, #A7DB8D); border-color: #78C850; color: black; }
    .bg-Psychic { background: linear-gradient(135deg, #F85888, #F890B0); border-color: #F85888; }
    .bg-Colorless { background: linear-gradient(135deg, #A8A878, #D8D8D0); border-color: #A8A878; color: black; }
    .bg-Dragon { background: linear-gradient(135deg, #7038F8, #B8A038); border-color: #7038F8; }
    .bg-Trainer { background: #e6e6e6; border-color: #999; color: #333; }
    .bg-Energy { background: #ffd700; border-color: #daa520; color: #333; }
    
    /* 按鈕美化 */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 資料庫 (包含圖片檔名對照)
# ==========================================

# 這裡設定：卡片名稱 -> 對應的圖片檔名
CARD_DB = {
    # --- 寶可夢 ---
    "瑪俐的長毛巨魔 ex": {"img": "grimmsnarl_ex.jpg", "type": "Darkness", "hp": 320, "cat": "Pokemon", "moves": [{"n": "暗影子彈", "d": 180}]},
    "瑪俐的詐唬魔": {"img": "morgrem.jpg", "type": "Darkness", "hp": 100, "cat": "Pokemon", "moves": [{"n": "推擊", "d": 60}]},
    "瑪俐的搗蛋小妖": {"img": "impidimp.jpg", "type": "Darkness", "hp": 70, "cat": "Pokemon", "moves": [{"n": "偷盜", "d": 0}, {"n": "推擊", "d": 10}]},
    "願增猿": {"img": "munkidori.jpg", "type": "Psychic", "hp": 110, "cat": "Pokemon", "moves": [{"n": "精神歪曲", "d": 60}]},
    "雪妖女": {"img": "froslass.jpg", "type": "Water", "hp": 90, "cat": "Pokemon", "moves": [{"n": "冰霜粉碎", "d": 60}]},
    "雪童子": {"img": "snorunt.jpg", "type": "Water", "hp": 70, "cat": "Pokemon", "moves": [{"n": "寒意", "d": 10}]},
    "米立龍": {"img": "tatsugiri.jpg", "type": "Dragon", "hp": 70, "cat": "Pokemon", "moves": [{"n": "衝浪", "d": 50}]},
    "含羞苞": {"img": "budew.jpg", "type": "Grass", "hp": 30, "cat": "Pokemon", "moves": [{"n": "癢癢花粉", "d": 10}]},
    "月月熊 赫月 ex": {"img": "bloodmoon_ursaluna.jpg", "type": "Colorless", "hp": 260, "cat": "Pokemon", "moves": [{"n": "血月", "d": 240}]},
    "可達鴨": {"img": "psyduck.jpg", "type": "Water", "hp": 70, "cat": "Pokemon", "moves": [{"n": "衝撞", "d": 20}]},
    
    # --- 訓練家 ---
    "寶可平板": {"img": "poke_tablet.jpg", "type": "Trainer", "cat": "Item"},
    "好友寶芬": {"img": "buddy_poffin.jpg", "type": "Trainer", "cat": "Item"},
    "夜間擔架": {"img": "night_stretcher.jpg", "type": "Trainer", "cat": "Item"},
    "神奇糖果": {"img": "rare_candy.jpg", "type": "Trainer", "cat": "Item"},
    "高級球": {"img": "ultra_ball.jpg", "type": "Trainer", "cat": "Item"},
    "能量轉移": {"img": "energy_switch.jpg", "type": "Trainer", "cat": "Item"},
    "不公印章": {"img": "unfair_stamp.jpg", "type": "Trainer", "cat": "ACE SPEC"},
    "氣球": {"img": "air_balloon.jpg", "type": "Trainer", "cat": "Tool"},
    "莉莉艾的決意": {"img": "lillie_resolve.jpg", "type": "Trainer", "cat": "Supporter"},
    "火箭隊的拉姆達": {"img": "rocket_lambda.jpg", "type": "Trainer", "cat": "Supporter"},
    "老大的指令": {"img": "boss_orders.jpg", "type": "Trainer", "cat": "Supporter"},
    "丹瑜": {"img": "carmine.jpg", "type": "Trainer", "cat": "Supporter"},
    "尖釘鎮道館": {"img": "spikemuth_gym.jpg", "type": "Trainer", "cat": "Stadium"},
    
    # --- 能量 ---
    "基本惡能量": {"img": "dark_energy.jpg", "type": "Energy", "cat": "Energy"}
}

# 牌組清單
DECKS = {
    "瑪俐惡系強攻牌組": {
        "瑪俐的長毛巨魔 ex": 2, "瑪俐的詐唬魔": 2, "瑪俐的搗蛋小妖": 3, "願增猿": 4,
        "含羞苞": 1, "可達鴨": 1, "雪童子": 2, "雪妖女": 2, "月月熊 赫月 ex": 1,
        "米立龍": 1, "寶可平板": 3, "好友寶芬": 3, "夜間擔架": 3, "神奇糖果": 2,
        "能量轉移": 1, "高級球": 1, "不公印章": 1, "氣球": 1, "莉莉艾的決意": 4,
        "老大的指令": 3, "火箭隊的拉姆達": 4, "丹瑜": 3, "尖釘鎮道館": 3, "基本惡能量": 9
    }
}

# ==========================================
# 3. 核心邏輯
# ==========================================

def create_card(name):
    data = CARD_DB.get(name, {"img": "", "type": "Colorless", "cat": "Unknown", "hp": 0})
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        **data,
        "damage": 0,
        "energy": [],
        "is_active": False
    }

def build_deck(deck_name):
    deck_list = []
    if deck_name in DECKS:
        for name, count in DECKS[deck_name].items():
            for _ in range(count):
                deck_list.append(create_card(name))
    random.shuffle(deck_list)
    return deck_list

def init_state():
    if 'page' not in st.session_state: st.session_state.page = 'lobby'
    if 'game' not in st.session_state: st.session_state.game = None

def start_game(p_deck_name, op_deck_name):
    st.session_state.game = {
        "turn_count": 0,
        "current_turn": None, 
        "log": ["遊戲開始！"],
        "player": {"deck": build_deck(p_deck_name), "hand": [], "active": None, "bench": [], "discard": [], "prizes": []},
        "opponent": {"deck": build_deck(op_deck_name), "hand": [], "active": None, "bench": [], "discard": [], "prizes": []}
    }
    # 初始設置
    draw_cards('player', 7)
    draw_cards('opponent', 7)
    for who in ['player', 'opponent']:
        for _ in range(6):
             if st.session_state.game[who]['deck']:
                 st.session_state.game[who]['prizes'].append(st.session_state.game[who]['deck'].pop(0))
    
    st.session_state.page = 'coin_flip'

def draw_cards(who, count=1):
    game = st.session_state.game
    deck = game[who]['deck']
    hand = game[who]['hand']
    drawn_count = 0
    for _ in range(count):
        if deck:
            hand.append(deck.pop(0))
            drawn_count += 1
    if drawn_count > 0:
        game['log'].append(f"{'你' if who=='player' else '對手'} 抽了 {drawn_count} 張牌")

def attack_action(attacker_key, defender_key):
    game = st.session_state.game
    at = game[attacker_key]['active']
    df = game[defender_key]['active']
    
    if not at or not df: return
    
    moves = at.get('moves', [])
    damage = moves[0]['d'] if moves else 20 # 預設傷害
    move_name = moves[0]['n'] if moves else "攻擊"
    
    df['damage'] += damage
    game['log'].append(f"⚔️ {at['name']} 使用「{move_name}」打 {damage}！")
    
    # 氣絕
    if df['hp'] > 0 and df['damage'] >= df['hp']:
        game['log'].append(f"💀 {df['name']} 氣絕！")
        game[defender_key]['discard'].append(df)
        game[defender_key]['active'] = None
        # 拿獎賞
        if game[attacker_key]['prizes']:
            prize = game[attacker_key]['prizes'].pop(0)
            game[attacker_key]['hand'].append(prize)
            game['log'].append(f"🏆 {'你' if attacker_key=='player' else '對手'} 拿了 1 張獎賞卡")

# ==========================================
# 4. 關鍵功能：卡片顯示器 (圖片優先)
# ==========================================

def render_card(card, key_id, is_hidden=False):
    """
    智慧渲染：
    1. 如果 is_hidden=True -> 顯示卡背圖(card_back.png) 或 預設卡背
    2. 如果有圖片且存在 -> 顯示圖片
    3. 如果沒圖片 -> 顯示 CSS 樣式框
    """
    
    # --- 隱藏狀態 (卡背) ---
    if is_hidden:
        if os.path.exists("card_back.png"):
             st.image("card_back.png", use_container_width=True)
        else:
             # CSS 卡背備案
             st.markdown("""
             <div style="height:150px; background:repeating-linear-gradient(45deg,#2b5876,#2b5876 10px,#4e4376 10px,#4e4376 20px);
             border-radius:8px; border:2px solid white; display:flex; align-items:center; justify-content:center; color:white;">
             CARD BACK
             </div>
             """, unsafe_allow_html=True)
        return

    # --- 顯示正面 ---
    img_path = card.get('img', '')
    
    # 判斷圖片檔案是否存在
    if img_path and os.path.exists(img_path):
        # 有圖片，直接顯示
        st.image(img_path, use_container_width=True)
        
        # 如果受傷了，顯示一個小小的傷害標記在圖片下方
        if card['damage'] > 0:
            st.markdown(f"<div style='background:red; color:white; text-align:center; border-radius:5px; margin-top:-20px; position:relative;'>-{card['damage']}</div>", unsafe_allow_html=True)
        
        # 顯示貼上的能量數量
        if card['energy']:
            st.caption(f"⚡ x {len(card['energy'])}")
            
    else:
        # 沒有圖片，使用 CSS 備案
        hp_show = f"HP {card['hp'] - card['damage']}/{card['hp']}" if card['hp'] > 0 else ""
        dmg_style = "background:red; border-radius:4px;" if card['damage'] > 0 else ""
        
        html = f"""
        <div class="card-container">
            <div class="css-card bg-{card['type']}">
                <div style="display:flex; justify-content:space-between; font-size:0.8em;">
                    <span>{card['cat']}</span>
                    <span style="{dmg_style}">{hp_show}</span>
                </div>
                <div style="font-weight:bold; font-size:0.9em;">{card['name']}</div>
                <div style="font-size:0.7em;">{card.get('type')}</div>
                <div style="font-size:0.7em;">(無圖片)</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 5. 主程式流程 (頁面控制)
# ==========================================
init_state()

# --- 側邊欄 ---
with st.sidebar:
    st.title("🎴 控制台")
    if st.button("🏠 回大廳 / 重置"):
        st.session_state.page = 'lobby'
        st.session_state.game = None
        st.rerun()
    
    if st.session_state.game:
        st.divider()
        st.write("📜 戰鬥日誌")
        for line in reversed(st.session_state.game['log'][-15:]):
            st.caption(line)

# --- 頁面 1: 大廳 ---
if st.session_state.page == 'lobby':
    st.title("PTCG 圖片對戰模擬器")
    st.info("系統會自動讀取資料夾內的圖片，如果沒有圖片則顯示文字框。")
    
    c1, c2 = st.columns(2)
    with c1:
        p_choice = st.selectbox("你的牌組", list(DECKS.keys()))
    with c2:
        o_choice = st.selectbox("電腦牌組", list(DECKS.keys()))
        
    if st.button("前往丟硬幣 ➡", type="primary"):
        start_game(p_choice, o_choice)
        st.rerun()

# --- 頁面 2: 硬幣 ---
elif st.session_state.page == 'coin_flip':
    st.title("🪙 決定先攻後攻")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("擲硬幣！", use_container_width=True):
            res = random.choice(["正面", "反面"])
            # 嘗試顯示硬幣圖片
            if res == "正面" and os.path.exists("coin_heads.png"):
                st.image("coin_heads.png", width=150)
            elif res == "反面" and os.path.exists("coin_tails.png"):
                st.image("coin_tails.png", width=150)
            else:
                st.header(f"結果：{res}")
                
            st.session_state.game['log'].append(f"硬幣結果: {res}")
            st.session_state.game['current_turn'] = 'Player' if res == "正面" else 'Opponent'
            
            time.sleep(1.5)
            st.session_state.page = 'battle'
            st.rerun()

# --- 頁面 3: 戰鬥 ---
elif st.session_state.page == 'battle':
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']
    
    st.subheader(f"回合: {game['current_turn']} (第 {game['turn_count']//2 + 1} 回)")
    
    # --- 電腦區 ---
    with st.container():
        st.markdown("#### 🤖 對手區域")
        c1, c2, c3 = st.columns([2, 5, 2])
        with c1:
            st.write(f"🏆 獎賞: {len(op['prizes'])}")
            st.write(f"📚 牌庫: {len(op['deck'])}")
            st.write(f"✋ 手牌: {len(op['hand'])}")
        with c2:
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    if i < len(op['bench']): render_card(op['bench'][i], f"ob_{i}")
        with c3:
            if op['active']: render_card(op['active'], "oa")
            else: st.info("空")
            
    st.divider()
    
    # --- 玩家區 ---
    with st.container():
        st.markdown("#### 👤 你的區域")
        c1, c2, c3 = st.columns([2, 5, 2])
        
        with c1: # 戰鬥場
            if pl['active']:
                render_card(pl['active'], "pa")
                if st.button("⚔️ 攻擊"):
                    attack_action('player', 'opponent')
                    st.rerun()
                if st.button("🏳️ 撤退"):
                    pl['discard'].append(pl['active'])
                    pl['active'] = None
                    st.rerun()
            else:
                st.warning("請推人上場")
                
        with c2: # 備戰
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    if i < len(pl['bench']):
                        render_card(pl['bench'][i], f"pb_{i}")
                        if st.button("⬆", key=f"up_{i}"):
                            if not pl['active']:
                                pl['active'] = pl['bench'].pop(i)
                                st.rerun()
                        if st.button("🗑️", key=f"d_{i}"):
                            pl['discard'].append(pl['bench'].pop(i))
                            st.rerun()
                            
        with c3: # 牌庫與獎賞
            if st.button("抽牌"):
                draw_cards('player', 1)
                st.rerun()
            if st.button("洗牌"):
                random.shuffle(pl['deck'])
                game['log'].append("你洗切了牌庫")
                st.rerun()
            if pl['prizes'] and st.button("拿獎賞"):
                pl['hand'].append(pl['prizes'].pop(0))
                st.rerun()
            st.write(f"🗑️ 棄牌: {len(pl['discard'])}")

    # --- 手牌 ---
    st.markdown("---")
    st.write("✋ 你的手牌")
    if pl['hand']:
        rows = [pl['hand'][i:i+6] for i in range(0, len(pl['hand']), 6)]
        for r_idx, row in enumerate(rows):
            cols = st.columns(6)
            for c_idx, card in enumerate(row):
                with cols[c_idx]:
                    render_card(card, f"h_{card['id']}")
                    act = st.selectbox("...", ["動作", "打出(備戰)", "打出(戰鬥)", "貼能量", "丟棄"], key=f"a_{card['id']}", label_visibility="collapsed")
                    if act == "打出(備戰)":
                        if card['cat'] == 'Pokemon' and len(pl['bench']) < 5:
                            pl['bench'].append(pl['hand'].pop(r_idx*6+c_idx))
                            st.rerun()
                    elif act == "打出(戰鬥)":
                        if card['cat'] == 'Pokemon' and not pl['active']:
                            pl['active'] = pl['hand'].pop(r_idx*6+c_idx)
                            st.rerun()
                    elif act == "貼能量":
                        if card['cat'] == 'Energy' and pl['active']:
                            pl['active']['energy'].append(card)
                            pl['hand'].pop(r_idx*6+c_idx)
                            st.rerun()
                    elif act == "丟棄":
                        pl['discard'].append(pl['hand'].pop(r_idx*6+c_idx))
                        game['log'].append(f"你丟棄了 {card['name']}")
                        st.rerun()

    st.markdown("---")
    if st.button("🛑 結束回合", type="primary"):
        game['current_turn'] = 'Opponent'
        draw_cards('opponent', 1)
        
        # AI 簡易邏輯
        op_poke = [c for c in op['hand'] if c['cat'] == 'Pokemon']
        if not op['active'] and op_poke:
            op['active'] = op_poke[0]
            op['hand'].remove(op_poke[0])
            
        while len(op['bench']) < 5:
            pokes = [c for c in op['hand'] if c['cat'] == 'Pokemon']
            if not pokes: break
            op['bench'].append(pokes[0])
            op['hand'].remove(pokes[0])
            
        if op['active'] and pl['active']:
            attack_action('opponent', 'player')
            
        game['turn_count'] += 1
        game['current_turn'] = 'Player'
        st.rerun()