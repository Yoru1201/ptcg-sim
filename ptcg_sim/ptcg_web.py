import streamlit as st
import json
import os
import random
import time

# ==========================================
# 1. 初始設定與樣式
# ==========================================
st.set_page_config(page_title="PTCG 模擬對戰系統 (v2.0)", layout="wide", page_icon="⚔️")

st.markdown("""
<style>
    .card-box {
        border: 2px solid #ccc; border-radius: 8px; padding: 5px;
        text-align: center; background-color: #2e2e2e; color: white;
        height: 200px; display: flex; flex-direction: column;
        justify-content: space-between; align-items: center;
        font-size: 0.8em; box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .card-name { font-weight: bold; color: #FFD700; margin-bottom: 2px; font-size: 1.1em;}
    .card-hp { color: #ff6666; font-weight: bold; }
    .zone-title { background-color: #444; color: white; padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 10px; font-weight: bold;}
    .stButton>button { width: 100%; border-radius: 5px; margin-top: 2px;}
    
    /* 對手區域背景微調 */
    .opponent-zone { background-color: #f0f0f5; padding: 10px; border-radius: 10px; margin-bottom: 20px; border: 2px dashed #aaa; }
    /* 玩家區域背景微調 */
    .player-zone { background-color: #e6f7ff; padding: 10px; border-radius: 10px; border: 2px solid #007bff; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 資料庫讀取函式
# ==========================================
DB_FILE = 'cards.json'
DECK_FILE = 'decks.json'

@st.cache_data
def load_db():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def load_decks():
    if not os.path.exists(DECK_FILE): return {}
    with open(DECK_FILE, 'r', encoding='utf-8') as f: return json.load(f)

db = load_db()
saved_decks = load_decks()

# 輔助：從名稱找卡片資料
def get_card_data(card_name):
    return next((c for c in db if c['name'] == card_name), None)

# 輔助：建立實體卡片 (產生唯一 ID 防止重複)
def create_card_instance(card_data):
    if not card_data: return None
    new_card = card_data.copy()
    new_card['uuid'] = str(random.randint(100000, 999999)) # 唯一編號
    new_card['damage_counters'] = 0
    new_card['attached_energy'] = []
    return new_card

# ==========================================
# 3. 遊戲核心邏輯 (初始化與 AI)
# ==========================================

def init_game(player_deck_name, opponent_deck_name):
    # 載入玩家牌組
    p_deck_list = []
    for name, count in saved_decks[player_deck_name].items():
        c_data = get_card_data(name)
        if c_data:
            for _ in range(count): p_deck_list.append(create_card_instance(c_data))
    
    # 載入電腦牌組
    o_deck_list = []
    for name, count in saved_decks[opponent_deck_name].items():
        c_data = get_card_data(name)
        if c_data:
            for _ in range(count): o_deck_list.append(create_card_instance(c_data))
            
    random.shuffle(p_deck_list)
    random.shuffle(o_deck_list)

    # 建立狀態
    st.session_state.game = {
        "turn": 1,
        "phase": "setup", # setup, player_turn, opponent_turn, game_over
        "log": ["遊戲開始！"],
        "player": {
            "deck": p_deck_list,
            "hand": [],
            "active": None,
            "bench": [],
            "prizes": [],
            "discard": []
        },
        "opponent": {
            "deck": o_deck_list,
            "hand": [],
            "active": None,
            "bench": [],
            "prizes": [],
            "discard": []
        }
    }

    # 初始抽牌 (雙方各7張)
    draw_cards('player', 7)
    draw_cards('opponent', 7)
    
    # 設置獎賞卡 (6張)
    for _ in range(6):
        if st.session_state.game['player']['deck']:
            st.session_state.game['player']['prizes'].append(st.session_state.game['player']['deck'].pop(0))
        if st.session_state.game['opponent']['deck']:
            st.session_state.game['opponent']['prizes'].append(st.session_state.game['opponent']['deck'].pop(0))

def draw_cards(who, count):
    deck = st.session_state.game[who]['deck']
    hand = st.session_state.game[who]['hand']
    drawn = []
    for _ in range(count):
        if deck:
            card = deck.pop(0)
            hand.append(card)
            drawn.append(card['name'])
    return drawn

# --- 簡單的 AI 邏輯 ---
def ai_turn_action():
    op = st.session_state.game['opponent']
    pl = st.session_state.game['player']
    log = st.session_state.game['log']
    
    log.append("--- 🤖 電腦回合 ---")
    
    # 1. 抽牌
    drawn = draw_cards('opponent', 1)
    # log.append(f"電腦抽了 1 張牌") # 隱藏電腦抽的牌

    # 2. 如果戰鬥場沒人，隨機從手牌推一隻基礎寶可夢
    if op['active'] is None:
        basics = [c for c in op['hand'] if c.get('category') == 'Pokemon' and c.get('stage', 'Basic') == 'Basic'] # 簡化判斷
        # 這裡簡單判定，只要是 Pokemon 且 HP < 200 假設是基礎 (因為資料庫沒有 stage 欄位，這是一個權宜之計)
        # 修正：直接抓所有 Pokemon 嘗試上場 (簡化版 AI)
        pokemons = [c for c in op['hand'] if c.get('category') == 'Pokemon']
        
        if pokemons:
            card = pokemons[0]
            op['active'] = card
            op['hand'].remove(card)
            log.append(f"電腦派出 {card['name']} 到戰鬥場")
        else:
            log.append("電腦沒有寶可夢可以出場！(AI 認輸邏輯未實作)")

    # 3. 填能 (簡易版：手上有能量就貼給戰鬥寶可夢)
    energies = [c for c in op['hand'] if c.get('category') == 'Energy']
    if energies and op['active']:
        card = energies[0]
        op['active']['attached_energy'].append(card)
        op['hand'].remove(card)
        log.append(f"電腦對 {op['active']['name']} 貼了能量")

    # 4. 鋪場 (備戰區未滿則鋪)
    while len(op['bench']) < 5:
        pokemons = [c for c in op['hand'] if c.get('category') == 'Pokemon']
        if not pokemons: break
        card = pokemons[0]
        op['bench'].append(card)
        op['hand'].remove(card)
        log.append(f"電腦將 {card['name']} 放置於備戰區")

    # 5. 攻擊 (簡易版：只要活著就攻擊)
    if op['active'] and pl['active']:
        # 這裡 AI 沒有判斷能量夠不夠，直接攻擊 (為了練習方便)
        damage = 30 # 預設 AI 攻擊力
        moves = op['active'].get('moves', [])
        if moves:
            damage = moves[0].get('damage', 30)
            move_name = moves[0].get('name', '攻擊')
        else:
            move_name = "衝撞"
            
        pl['active']['damage_counters'] += damage
        log.append(f"電腦使用 {move_name} 造成 {damage} 點傷害！")
        
        # 檢查玩家是否氣絕
        if pl['active']['damage_counters'] >= pl['active']['hp']:
            log.append(f"玩家的 {pl['active']['name']} 氣絕了！")
            pl['discard'].append(pl['active'])
            pl['active'] = None
            # 拿獎賞
            if op['prizes']:
                prize = op['prizes'].pop(0)
                op['hand'].append(prize)
                log.append("電腦拿取 1 張獎賞卡")

    st.session_state.game['phase'] = 'player_turn'
    log.append("--- 輪到你了 ---")


# ==========================================
# 4. 介面渲染函式
# ==========================================
def render_card_mini(card, key_id, is_hidden=False, location=""):
    """渲染單張小卡片"""
    if is_hidden:
        st.markdown(f"""
        <div style="background:#555; color:#aaa; height:100px; border-radius:5px; display:flex; align-items:center; justify-content:center;">
            卡背
        </div>
        """, unsafe_allow_html=True)
        return

    img_path = card.get('image', '')
    if img_path and os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        # 無圖片時的備案
        hp_show = f"HP {card['hp'] - card['damage_counters']}/{card['hp']}" if 'hp' in card else ""
        dmg_color = "red" if card['damage_counters'] > 0 else "#666"
        
        html = f"""
        <div class="card-box">
            <div style="color:{dmg_color}">{hp_show}</div>
            <div class="card-name">{card['name']}</div>
            <div style="font-size:0.8em;">{card.get('category')}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 5. 主程式頁面
# ==========================================

# --- 側邊欄：遊戲設定 ---
st.sidebar.title("⚙️ 對戰設定")

# 讀取牌組列表
deck_names = list(saved_decks.keys())

if not deck_names:
    st.sidebar.error("⚠️ 找不到牌組！請確認 decks.json 是否存在且有內容。")
else:
    # 選擇玩家牌組
    p_deck_choice = st.sidebar.selectbox("你的牌組", deck_names, index=0)
    # 選擇電腦牌組
    o_deck_choice = st.sidebar.selectbox("電腦 (AI) 牌組", deck_names, index=0)

    if st.sidebar.button("⚔️ 開始新對戰 / 重置", type="primary"):
        init_game(p_deck_choice, o_deck_choice)
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("說明：這是一個練習模式。\nAI 雖然不聰明，但會自動鋪場與攻擊，適合用來測試手牌順暢度。")

# --- 主畫面檢查 ---
if 'game' not in st.session_state:
    st.title("👋 歡迎來到 PTCG 練習場")
    st.write("請從左側選擇雙方牌組，並點擊「開始新對戰」。")
    st.stop()

game = st.session_state.game
pl = game['player']
op = game['opponent']

# --- 戰鬥日誌 (顯示在最上方或側邊) ---
with st.expander("📜 戰鬥紀錄 (Log)", expanded=False):
    for line in reversed(game['log'][-10:]):
        st.text(line)

# ==========================================
# 上半部：電腦 (Opponent) 區域
# ==========================================
st.markdown("<div class='zone-title'>🤖 電腦對手 (Opponent)</div>", unsafe_allow_html=True)

# 電腦手牌 (蓋牌顯示)
col_info, col_hand = st.columns([1, 4])
with col_info:
    st.write(f"🏆 獎賞: {len(op['prizes'])}")
    st.write(f"📚 牌庫: {len(op['deck'])}")
    st.write(f"✋ 手牌: {len(op['hand'])}")
with col_hand:
    # 只顯示手牌背面數量
    st.write("🎴 " * len(op['hand']))

col_bench, col_active, col_discard = st.columns([4, 2, 1])

with col_bench:
    st.caption("備戰區")
    if op['bench']:
        cols = st.columns(5)
        for i, card in enumerate(op['bench']):
            with cols[i]:
                render_card_mini(card, f"op_bench_{i}")

with col_active:
    st.caption("戰鬥場")
    if op['active']:
        render_card_mini(op['active'], "op_active")
        st.write(f"❤️ 傷害: {op['active']['damage_counters']}")
        st.write(f"⚡ 能量: {len(op['active']['attached_energy'])}")
    else:
        st.info("空缺")

with col_discard:
    st.caption("棄牌區")
    st.write(f"{len(op['discard'])} 張")

st.markdown("---")

# ==========================================
# 下半部：玩家 (Player) 區域
# ==========================================
st.markdown("<div class='zone-title'>👤 你的戰場 (Player)</div>", unsafe_allow_html=True)

col_discard_p, col_active_p, col_bench_p = st.columns([1, 2, 4])

with col_discard_p:
    st.caption("棄牌區")
    st.write(f"{len(pl['discard'])} 張")

with col_active_p:
    st.caption("戰鬥場")
    if pl['active']:
        render_card_mini(pl['active'], "pl_active")
        st.write(f"❤️ 傷害: {pl['active']['damage_counters']}")
        if st.button("撤退 (丟棄)", key="retreat_btn"):
            pl['discard'].append(pl['active'])
            pl['active'] = None
            st.rerun()
    else:
        st.warning("請從備戰區推人上場")

with col_bench_p:
    st.caption("備戰區")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            if i < len(pl['bench']):
                card = pl['bench'][i]
                render_card_mini(card, f"pl_bench_{i}")
                if st.button("上場", key=f"promo_{i}"):
                    if not pl['active']:
                        pl['active'] = pl['bench'].pop(i)
                        st.rerun()
                if st.button("丟棄", key=f"disc_b_{i}"): # 增加丟棄功能以便清場
                     pl['discard'].append(pl['bench'].pop(i))
                     st.rerun()

# 玩家資訊與手牌
col_info_p, col_hand_p = st.columns([1, 4])

with col_info_p:
    st.write(f"🏆 獎賞: {len(pl['prizes'])}")
    st.write(f"📚 牌庫: {len(pl['deck'])}")
    if st.button("抽一張牌"):
        draw_cards('player', 1)
        st.rerun()
    
    if st.button("結束回合 (換電腦)", type="primary"):
        ai_turn_action()
        st.rerun()

with col_hand_p:
    st.write("✋ 你的手牌")
    if pl['hand']:
        h_cols = st.columns(6)
        for i, card in enumerate(pl['hand']):
            with h_cols[i % 6]:
                render_card_mini(card, f"hand_{i}")
                # 手牌動作選單
                action = st.selectbox("動作", ["...", "打出/上場", "貼能(戰鬥)", "丟棄"], key=f"act_{i}_{card['uuid']}", label_visibility="collapsed")
                
                if action == "打出/上場":
                    if card['category'] == 'Pokemon':
                        if not pl['active']: pl['active'] = pl['hand'].pop(i)
                        elif len(pl['bench']) < 5: pl['bench'].append(pl['hand'].pop(i))
                    else: # 訓練家卡直接進棄牌 (簡化)
                         pl['discard'].append(pl['hand'].pop(i))
                    st.rerun()
                elif action == "貼能(戰鬥)":
                    if pl['active']:
                        pl['active']['attached_energy'].append(pl['hand'].pop(i))
                        st.rerun()
                elif action == "丟棄":
                    pl['discard'].append(pl['hand'].pop(i))
                    st.rerun()