import streamlit as st
import json
import os
import random
import base64

# ==========================================
# 1. 初始設定與樣式
# ==========================================
st.set_page_config(page_title="PTCG 牌組對戰系統", layout="wide", page_icon="🎴")

# --- 樣式設定 (CSS) ---
st.markdown("""
<style>
    /* 卡片容器樣式 */
    .card-box {
        border: 2px solid #ccc;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        background-color: #333;
        color: white;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify_content: space-between;
        align-items: center;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .card-name { font-weight: bold; font-size: 1.1em; color: #FFD700; margin-bottom: 5px; }
    .card-type { font-size: 0.8em; color: #ddd; background-color: #555; padding: 2px 8px; border-radius: 10px; }
    .card-hp { font-size: 0.9em; color: #ff6666; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 資料庫與狀態管理
# ==========================================
DB_FILE = 'cards.json'
DECK_FILE = 'decks.json'

@st.cache_data
def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_saved_decks():
    if not os.path.exists(DECK_FILE):
        return {}
    with open(DECK_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 初始化 Session State
if 'deck' not in st.session_state:
    st.session_state.deck = []
if 'current_deck_name' not in st.session_state:
    st.session_state.current_deck_name = None
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
# 戰鬥狀態
if 'hand' not in st.session_state: st.session_state.hand = []
if 'active_spot' not in st.session_state: st.session_state.active_spot = None
if 'bench' not in st.session_state: st.session_state.bench = []
if 'discard_pile' not in st.session_state: st.session_state.discard_pile = []
if 'prizes' not in st.session_state: st.session_state.prizes = []
if 'coin_result' not in st.session_state: st.session_state.coin_result = None

db = load_db()
saved_decks = load_saved_decks()

# ==========================================
# 3. 核心功能：卡片渲染與牌組載入
# ==========================================
def render_card(card, key_suffix=""):
    image_path = card.get('image', '')
    if image_path and os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        hp_text = f"HP {card.get('hp')}" if 'hp' in card else ""
        type_text = card.get('category', 'Card')
        if 'sub_category' in card: type_text += f" - {card['sub_category']}"
        html = f"""
        <div class="card-box">
            <div class="card-hp">{hp_text}</div>
            <div class="card-name">{card['name']}</div>
            <div class="card-type">{type_text}</div>
            <div style="font-size:0.8em; color:#aaa;">(無圖片)</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

def load_deck_from_name(deck_name):
    """從 decks.json 讀取清單並轉換成完整的卡片物件列表"""
    if deck_name not in saved_decks:
        return False
    
    deck_list = saved_decks[deck_name]
    new_deck = []
    
    for card_name, count in deck_list.items():
        # 從資料庫找卡片完整資料
        card_data = next((c for c in db if c['name'] == card_name), None)
        if card_data:
            for _ in range(count):
                new_deck.append(card_data)
        else:
            st.error(f"資料庫找不到卡片：{card_name}，請檢查 cards.json")
            
    st.session_state.deck = new_deck
    st.session_state.current_deck_name = deck_name
    return True

# ==========================================
# 4. 遊戲邏輯
# ==========================================
def start_game():
    if len(st.session_state.deck) != 60:
        st.error(f"牌組張數錯誤 ({len(st.session_state.deck)}/60)，請檢查牌組設定。")
        return
    
    game_deck = st.session_state.deck.copy()
    random.shuffle(game_deck)
    
    st.session_state.game_deck = game_deck
    st.session_state.hand = []
    st.session_state.active_spot = None
    st.session_state.bench = []
    st.session_state.discard_pile = []
    st.session_state.prizes = []
    st.session_state.coin_result = None
    
    # 抽 7 張手牌, 6 張獎賞
    for _ in range(7):
        if st.session_state.game_deck: st.session_state.hand.append(st.session_state.game_deck.pop(0))
    for _ in range(6):
        if st.session_state.game_deck: st.session_state.prizes.append(st.session_state.game_deck.pop(0))
            
    st.session_state.game_started = True

def draw_card():
    if st.session_state.game_deck:
        st.session_state.hand.append(st.session_state.game_deck.pop(0))
    else:
        st.error("牌庫已空！")

def flip_coin():
    st.session_state.coin_result = random.choice(["正面 (HEADS)", "反面 (TAILS)"])

# ==========================================
# 5. 介面呈現
# ==========================================

# --- 模式 A: 牌組選擇與檢視 ---
if not st.session_state.game_started:
    st.title("🗂️ 牌組選擇中心")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("選擇你的牌組")
        
        # 1. 牌組搜尋/選單
        deck_names = list(saved_decks.keys())
        if not deck_names:
            st.warning("目前沒有儲存的牌組，請檢查 decks.json")
        else:
            selected_deck_name = st.selectbox("請選擇牌組", deck_names)
            
            if st.button("📥 載入此牌組", type="primary"):
                if load_deck_from_name(selected_deck_name):
                    st.success(f"已載入：{selected_deck_name}")
                    st.rerun()

        st.markdown("---")
        st.caption("或是... 手動微調 (進階)")
        # 這裡保留舊的單卡添加功能，以便微調
        if st.checkbox("開啟單卡編輯模式"):
            card_names = [c['name'] for c in db]
            add_choice = st.selectbox("添加單卡", card_names)
            if st.button("加入"):
                card = next((c for c in db if c['name'] == add_choice), None)
                if card: st.session_state.deck.append(card)
                st.rerun()

    with col2:
        if st.session_state.current_deck_name:
            st.subheader(f"目前牌組：{st.session_state.current_deck_name}")
        else:
            st.subheader("目前牌組 (未命名)")
            
        st.write(f"總張數：**{len(st.session_state.deck)}** / 60")
        
        # 顯示牌組內容 (統計)
        if st.session_state.deck:
            counts = {}
            for card in st.session_state.deck:
                name = card['name']
                counts[name] = counts.get(name, 0) + 1
            
            # 漂亮的條列式顯示
            for name, count in counts.items():
                st.text(f"{name} x{count}")
                
            st.markdown("---")
            if len(st.session_state.deck) == 60:
                if st.button("🚀 開始對戰", type="primary", use_container_width=True):
                    start_game()
                    st.rerun()
            else:
                st.warning("牌組必須剛好 60 張才能開始對戰。")
        else:
            st.info("👈 請從左側載入牌組")

# --- 模式 B: 對戰場地 (保持原本功能) ---
else:
    st.title(f"⚔️ 對戰中: {st.session_state.current_deck_name}")
    
    top1, top2 = st.columns([1, 5])
    with top1:
        if st.button("⬅️ 結束對戰"):
            st.session_state.game_started = False
            st.rerun()
            
    left_col, center_col, right_col = st.columns([1, 3, 1])
    
    with left_col:
        st.markdown("### 工具")
        if st.button("🟡 擲硬幣"): flip_coin()
        if st.session_state.coin_result: st.warning(f"結果：{st.session_state.coin_result}")

    with center_col:
        st.markdown("### 🔥 戰鬥場")
        if st.session_state.active_spot:
            render_card(st.session_state.active_spot)
            if st.button("撤退/氣絕"):
                st.session_state.discard_pile.append(st.session_state.active_spot)
                st.session_state.active_spot = None
                st.rerun()
        else:
            st.info("戰鬥場空缺")

        st.markdown("### 🏕️ 備戰區")
        bench_cols = st.columns(5)
        for i in range(5):
            with bench_cols[i]:
                if i < len(st.session_state.bench):
                    card = st.session_state.bench[i]
                    render_card(card)
                    if st.button("上場", key=f"act_{i}"):
                        if not st.session_state.active_spot:
                            st.session_state.active_spot = st.session_state.bench.pop(i)
                            st.rerun()
                    if st.button("丟棄", key=f"disc_{i}"):
                        st.session_state.discard_pile.append(st.session_state.bench.pop(i))
                        st.rerun()

    with right_col:
        st.markdown("### 資訊")
        st.write(f"📚 牌庫: **{len(st.session_state.game_deck)}**")
        if st.button("抽牌"):
            draw_card()
            st.rerun()
        st.write(f"🏆 獎賞: **{len(st.session_state.prizes)}**")
        if st.button("拿獎賞"):
            if st.session_state.prizes:
                st.session_state.hand.append(st.session_state.prizes.pop(0))
                st.rerun()
        st.write(f"🗑️ 棄牌: **{len(st.session_state.discard_pile)}**")

    st.markdown("---")
    st.subheader(f"✋ 手牌 ({len(st.session_state.hand)})")
    if st.session_state.hand:
        cols = st.columns(6)
        for i, card in enumerate(st.session_state.hand):
            with cols[i % 6]:
                render_card(card)
                act = st.selectbox("動作", ["...", "打出", "丟棄"], key=f"h_act_{i}", label_visibility="collapsed")
                if act == "打出":
                    if card['category'] == 'Pokemon':
                        if not st.session_state.active_spot: st.session_state.active_spot = st.session_state.hand.pop(i)
                        elif len(st.session_state.bench) < 5: st.session_state.bench.append(st.session_state.hand.pop(i))
                    else:
                        st.session_state.discard_pile.append(st.session_state.hand.pop(i))
                    st.rerun()
                elif act == "丟棄":
                    st.session_state.discard_pile.append(st.session_state.hand.pop(i))
                    st.rerun()