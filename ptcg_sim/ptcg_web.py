import streamlit as st
import random
import time
import os

# ==========================================
# 1. 遊戲資料 (直接寫在程式裡，免讀檔)
# ==========================================

# --- 卡片資料庫 ---
ALL_CARDS_DB = [
    {
        "name": "瑪俐的長毛巨魔 ex", "image": "grimmsnarl_ex.jpg", "category": "Pokemon", "hp": 320, "type": "Darkness",
        "moves": [{"name": "暗影子彈", "damage": 180}], "retreat": 2
    },
    {
        "name": "瑪俐的詐唬魔", "image": "morgrem.jpg", "category": "Pokemon", "hp": 100, "type": "Darkness",
        "moves": [{"name": "推擊", "damage": 60}], "retreat": 1
    },
    {
        "name": "瑪俐的搗蛋小妖", "image": "impidimp.jpg", "category": "Pokemon", "hp": 70, "type": "Darkness",
        "moves": [{"name": "偷盜", "damage": 0}, {"name": "推擊", "damage": 10}], "retreat": 1
    },
    {
        "name": "雪妖女", "image": "froslass.jpg", "category": "Pokemon", "hp": 90, "type": "Water",
        "moves": [{"name": "冰霜粉碎", "damage": 60}], "retreat": 1
    },
    {
        "name": "雪童子", "image": "snorunt.jpg", "category": "Pokemon", "hp": 70, "type": "Water",
        "moves": [{"name": "寒意", "damage": 10}], "retreat": 1
    },
    {
        "name": "願增猿", "image": "munkidori.jpg", "category": "Pokemon", "hp": 110, "type": "Psychic",
        "moves": [{"name": "精神歪曲", "damage": 60}], "retreat": 1
    },
    {
        "name": "米立龍", "image": "tatsugiri.jpg", "category": "Pokemon", "hp": 70, "type": "Dragon",
        "moves": [{"name": "衝浪", "damage": 50}], "retreat": 1
    },
    {
        "name": "含羞苞", "image": "budew.jpg", "category": "Pokemon", "hp": 30, "type": "Grass",
        "moves": [{"name": "癢癢花粉", "damage": 10}], "retreat": 0
    },
    {
        "name": "月月熊 赫月 ex", "image": "bloodmoon_ursaluna.jpg", "category": "Pokemon", "hp": 260, "type": "Colorless",
        "moves": [{"name": "血月", "damage": 240}], "retreat": 3
    },
    {
        "name": "可達鴨", "image": "psyduck.jpg", "category": "Pokemon", "hp": 70, "type": "Water",
        "moves": [{"name": "衝撞", "damage": 20}], "retreat": 1
    },
    # --- 訓練家與能量 ---
    {"name": "寶可平板", "image": "poke_tablet.jpg", "category": "Trainer", "sub_category": "Item"},
    {"name": "好友寶芬", "image": "buddy_poffin.jpg", "category": "Trainer", "sub_category": "Item"},
    {"name": "夜間擔架", "image": "night_stretcher.jpg", "category": "Trainer", "sub_category": "Item"},
    {"name": "神奇糖果", "image": "rare_candy.jpg", "category": "Trainer", "sub_category": "Item"},
    {"name": "高級球", "image": "ultra_ball.jpg", "category": "Trainer", "sub_category": "Item"},
    {"name": "能量轉移", "image": "energy_switch.jpg", "category": "Trainer", "sub_category": "Item"},
    {"name": "不公印章", "image": "unfair_stamp.jpg", "category": "Trainer", "sub_category": "ACE SPEC"},
    {"name": "氣球", "image": "air_balloon.jpg", "category": "Trainer", "sub_category": "Tool"},
    {"name": "莉莉艾的決意", "image": "lillie_resolve.jpg", "category": "Trainer", "sub_category": "Supporter"},
    {"name": "火箭隊的拉姆達", "image": "rocket_lambda.jpg", "category": "Trainer", "sub_category": "Supporter"},
    {"name": "老大的指令", "image": "boss_orders.jpg", "category": "Trainer", "sub_category": "Supporter"},
    {"name": "丹瑜", "image": "carmine.jpg", "category": "Trainer", "sub_category": "Supporter"},
    {"name": "尖釘鎮道館", "image": "spikemuth_gym.jpg", "category": "Trainer", "sub_category": "Stadium"},
    {"name": "基本惡能量", "image": "dark_energy.jpg", "category": "Energy", "sub_category": "Basic"}
]

# --- 預設牌組 ---
PRESET_DECKS = {
    "瑪俐的長毛巨魔ex-1": {
        "瑪俐的長毛巨魔 ex": 2, "瑪俐的詐唬魔": 2, "瑪俐的搗蛋小妖": 3, "願增猿": 4,
        "含羞苞": 1, "可達鴨": 1, "雪童子": 2, "雪妖女": 2, "月月熊 赫月 ex": 1,
        "米立龍": 1, "寶可平板": 3, "好友寶芬": 3, "夜間擔架": 3, "神奇糖果": 2,
        "能量轉移": 1, "高級球": 1, "不公印章": 1, "氣球": 1, "莉莉艾的決意": 4,
        "老大的指令": 3, "火箭隊的拉姆達": 4, "丹瑜": 3, "尖釘鎮道館": 3,
        "基本惡能量": 9
    }
}

# ==========================================
# 2. 初始設定與樣式
# ==========================================
st.set_page_config(page_title="PTCG 練習場 (整合版)", layout="wide", page_icon="⚔️")

st.markdown("""
<style>
    .card-box {
        border: 2px solid #ccc; border-radius: 8px; padding: 5px;
        text-align: center; background-color: #2e2e2e; color: white;
        height: 180px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        font-size: 0.8em; box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .card-name { font-weight: bold; color: #FFD700; margin-bottom: 5px; font-size: 1.0em;}
    .zone-title { background-color: #444; color: white; padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 10px; font-weight: bold;}
    .stButton>button { width: 100%; border-radius: 5px; margin-top: 2px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 核心邏輯
# ==========================================

def get_card_data(card_name):
    # 從上面的 ALL_CARDS_DB 找資料
    return next((c for c in ALL_CARDS_DB if c['name'] == card_name), None)

def create_card_instance(card_data):
    if not card_data: return None
    new_card = card_data.copy()
    new_card['uuid'] = str(random.randint(100000, 999999))
    new_card['damage_counters'] = 0
    new_card['attached_energy'] = []
    return new_card

def init_game():
    deck_data = PRESET_DECKS["瑪俐的長毛巨魔ex-1"] # 直接鎖定這副牌
    
    # 建立雙方牌組
    def build_deck():
        d_list = []
        for name, count in deck_data.items():
            c_data = get_card_data(name)
            if c_data:
                for _ in range(count): d_list.append(create_card_instance(c_data))
        random.shuffle(d_list)
        return d_list

    st.session_state.game = {
        "turn": 1,
        "log": ["遊戲開始！雙方載入牌組..."],
        "player": {"deck": build_deck(), "hand": [], "active": None, "bench": [], "prizes": [], "discard": []},
        "opponent": {"deck": build_deck(), "hand": [], "active": None, "bench": [], "prizes": [], "discard": []}
    }

    # 初始設置
    draw_cards('player', 7)
    draw_cards('opponent', 7)
    # 設置獎賞卡
    for _ in range(6):
        if st.session_state.game['player']['deck']: st.session_state.game['player']['prizes'].append(st.session_state.game['player']['deck'].pop(0))
        if st.session_state.game['opponent']['deck']: st.session_state.game['opponent']['prizes'].append(st.session_state.game['opponent']['deck'].pop(0))

def draw_cards(who, count):
    deck = st.session_state.game[who]['deck']
    hand = st.session_state.game[who]['hand']
    for _ in range(count):
        if deck: hand.append(deck.pop(0))

def ai_turn_action():
    op = st.session_state.game['opponent']
    pl = st.session_state.game['player']
    log = st.session_state.game['log']
    
    log.append("--- 🤖 電腦回合 ---")
    draw_cards('opponent', 1)
    
    # AI 派怪
    if op['active'] is None:
        pokes = [c for c in op['hand'] if c.get('category') == 'Pokemon']
        if pokes:
            c = pokes[0]
            op['active'] = c
            op['hand'].remove(c)
            log.append(f"電腦派出 {c['name']}")

    # AI 鋪場
    while len(op['bench']) < 5:
        pokes = [c for c in op['hand'] if c.get('category') == 'Pokemon']
        if not pokes: break
        c = pokes[0]
        op['bench'].append(c)
        op['hand'].remove(c)
        log.append(f"電腦將 {c['name']} 放到備戰區")

    # AI 攻擊
    if op['active'] and pl['active']:
        dmg = 30
        if 'moves' in op['active'] and op['active']['moves']:
            dmg = op['active']['moves'][0]['damage']
        pl['active']['damage_counters'] += dmg
        log.append(f"電腦攻擊！造成 {dmg} 點傷害")
        
        if pl['active']['damage_counters'] >= pl['active']['hp']:
            log.append(f"你的 {pl['active']['name']} 氣絕了！")
            pl['discard'].append(pl['active'])
            pl['active'] = None
            if op['prizes']: op['hand'].append(op['prizes'].pop(0))

    log.append("--- 輪到你了 ---")

# ==========================================
# 4. 介面顯示
# ==========================================
def render_card(card, key_id, hidden=False):
    if hidden:
        st.markdown('<div class="card-box" style="background:#444;">🎴<br>卡背</div>', unsafe_allow_html=True)
        return

    # 檢查圖片是否存在，不存在則顯示文字框
    img_path = card.get('image', '')
    if img_path and os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        # 圖片遺失時的備案
        hp_txt = f"HP {card['hp'] - card['damage_counters']}" if 'hp' in card else ""
        st.markdown(f"""
        <div class="card-box">
            <div style="color:red; font-weight:bold;">{hp_txt}</div>
            <div class="card-name">{card['name']}</div>
            <div style="font-size:0.8em; color:#ccc;">{card['category']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 主程式 ---
if 'game' not in st.session_state:
    st.title("⚔️ PTCG 練習場 (整合版)")
    if st.button("開始對戰", type="primary"):
        init_game()
        st.rerun()
    st.stop()

game = st.session_state.game
pl = game['player']
op = game['opponent']

# 顯示戰況
st.sidebar.title("📜 戰鬥紀錄")
for line in reversed(game['log'][-10:]):
    st.sidebar.text(line)

if st.sidebar.button("重置遊戲"):
    del st.session_state.game
    st.rerun()

# 戰場配置
st.markdown("<div class='zone-title'>🤖 電腦對手</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([4, 2, 1])
with c1:
    st.caption("備戰區")
    cols = st.columns(5)
    for i, c in enumerate(op['bench']):
        with cols[i]: render_card(c, f"ob_{i}")
with c2:
    st.caption("戰鬥場")
    if op['active']: render_card(op['active'], "oa")
    else: st.info("空")
with c3:
    st.write(f"手牌: {len(op['hand'])}")
    st.write(f"獎賞: {len(op['prizes'])}")

st.markdown("---")
st.markdown("<div class='zone-title'>👤 你的戰場</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 4])
with c1:
    st.write(f"牌庫: {len(pl['deck'])}")
    st.write(f"獎賞: {len(pl['prizes'])}")
    if st.button("抽牌"):
        draw_cards('player', 1)
        st.rerun()
    if st.button("結束回合", type="primary"):
        ai_turn_action()
        st.rerun()
        
with c2:
    st.caption("戰鬥場")
    if pl['active']:
        render_card(pl['active'], "pa")
        if st.button("撤退"):
            pl['discard'].append(pl['active'])
            pl['active'] = None
            st.rerun()
    else:
        st.warning("請派人上場")

with c3:
    st.caption("備戰區")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            if i < len(pl['bench']):
                render_card(pl['bench'][i], f"pb_{i}")
                if st.button("上", key=f"up_{i}"):
                    if not pl['active']:
                        pl['active'] = pl['bench'].pop(i)
                        st.rerun()

st.markdown("---")
st.write("✋ 你的手牌")
if pl['hand']:
    cols = st.columns(8)
    for i, card in enumerate(pl['hand']):
        with cols[i % 8]:
            render_card(card, f"h_{i}")
            if st.button("打", key=f"play_{i}_{card['uuid']}"):
                # 簡單的出牌邏輯
                if card['category'] == 'Pokemon':
                    if not pl['active']: pl['active'] = pl['hand'].pop(i)
                    elif len(pl['bench']) < 5: pl['bench'].append(pl['hand'].pop(i))
                else:
                    pl['discard'].append(pl['hand'].pop(i)) # 訓練家卡直接丟棄
                st.rerun()