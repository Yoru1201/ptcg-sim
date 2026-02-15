import streamlit as st
import json
import os
import random

# ==========================================
# 1. 頁面設定
# ==========================================
st.set_page_config(page_title="PTCG 系統診斷模式", layout="wide", page_icon="🛠️")

st.title("🛠️ 系統診斷模式")
st.info("這個模式會幫你檢查檔案到底在哪裡。")

# ==========================================
# 2. 強力診斷功能 (顯示檔案列表)
# ==========================================
current_dir = os.getcwd()
all_files = os.listdir(current_dir)

st.subheader("1. 檔案環境檢查")
col1, col2 = st.columns(2)

with col1:
    st.write(f"📂 **程式目前執行的資料夾:**")
    st.code(current_dir)

with col2:
    st.write(f"📄 **這個資料夾裡實際有的檔案:**")
    st.write(all_files)

# ==========================================
# 3. 檢查 decks.json
# ==========================================
st.subheader("2. 檢查 decks.json (牌組檔)")

target_file = 'decks.json'
possible_error_file = 'decks.json.txt'

# 狀態 A: 成功找到
if target_file in all_files:
    st.success(f"✅ 成功！找到 `{target_file}` 了。")
    
    # 嘗試讀取內容
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        st.write("內容讀取成功，你的牌組名稱是：")
        st.json(list(data.keys()))
        deck_loaded = True
    except Exception as e:
        st.error(f"❌ 檔案雖然存在，但內容格式錯誤：{e}")
        st.warning("請確認內容是否為正確的 JSON 格式 (括號有沒有對齊)。")
        deck_loaded = False

# 狀態 B: 檔名變成了 .txt (最常見錯誤)
elif possible_error_file in all_files:
    st.error(f"❌ 找不到 `{target_file}`")
    st.warning(f"⚠️ 但是我發現了 `{possible_error_file}`！")
    st.markdown("### 🛠️ 解決方法：")
    st.markdown("Windows 把你的副檔名隱藏了。請重新命名該檔案，**把後面的 `.txt` 刪掉**。")
    deck_loaded = False

# 狀態 C: 完全找不到
else:
    st.error(f"❌ 找不到 `{target_file}`")
    st.warning("請確認你是否有建立這個檔案，並且放在跟 `app.py` 同一個資料夾。")
    deck_loaded = False

# ==========================================
# 4. 檢查 cards.json
# ==========================================
st.subheader("3. 檢查 cards.json (卡片資料庫)")
if 'cards.json' in all_files:
    st.success("✅ 找到 `cards.json`")
else:
    st.error("❌ 找不到 `cards.json`")

st.markdown("---")

# ==========================================
# 5. 自動修復工具 (如果是檔案沒建立)
# ==========================================
st.subheader("4. 自動修復 (如果真的搞不定)")

if not deck_loaded:
    st.write("如果你一直無法解決檔案問題，請點擊下方按鈕，我直接幫你產生一個正確的 `decks.json`。")
    if st.button("🪄 幫我建立 decks.json", type="primary"):
        # 預設牌組資料
        default_deck_data = {
            "瑪俐的長毛巨魔ex-1": {
                "瑪俐的長毛巨魔 ex": 2, "瑪俐的詐唬魔": 2, "瑪俐的搗蛋小妖": 3, "願增猿": 4,
                "含羞苞": 1, "可達鴨": 1, "雪童子": 2, "雪妖女": 2, "月月熊 赫月 ex": 1,
                "米立龍": 1, "寶可平板": 3, "好友寶芬": 3, "夜間擔架": 3, "神奇糖果": 2,
                "能量轉移": 1, "高級球": 1, "不公印章": 1, "氣球": 1, "莉莉艾的決意": 4,
                "老大的指令": 3, "火箭隊的拉姆達": 4, "丹瑜": 3, "尖釘鎮道館": 3,
                "基本惡能量": 9
            }
        }
        try:
            with open('decks.json', 'w', encoding='utf-8') as f:
                json.dump(default_deck_data, f, ensure_ascii=False, indent=4)
            st.success("✨ 檔案已建立！請重新整理網頁。")
            st.rerun() # 重新整理
        except Exception as e:
            st.error(f"建立失敗，權限不足或路徑錯誤：{e}")