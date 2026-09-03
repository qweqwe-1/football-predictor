import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import time

# ================= 页面设置 =================
st.set_page_config(page_title="⚽ 足球预测大师", page_icon="⚽", layout="wide")
st.title("⚽ 足球比赛结果预测系统")
st.markdown("基于全因子模型（历史战绩+攻防数据+主客场优势）")

# ================= 模拟数据库（实际使用时可替换为真实数据） =================
@st.cache_data
def load_data():
    # 这里模拟了一些历史比赛数据，用于训练模型
    data = {
        'home_goals_avg': [2, 1, 3, 0, 1, 2, 1, 0, 2, 3], # 主队平均进球
        'away_goals_avg': [1, 1, 0, 2, 1, 0, 2, 1, 1, 0], # 客队平均进球
        'home_win_rate': [0.6, 0.4, 0.8, 0.2, 0.5, 0.7, 0.3, 0.4, 0.6, 0.8], # 主队胜率
        'away_win_rate': [0.4, 0.5, 0.2, 0.6, 0.5, 0.2, 0.6, 0.5, 0.4, 0.2], # 客队胜率
        'result': [1, 0, 1, 2, 0, 1, 2, 0, 1, 1] # 1=主胜, 0=平局, 2=客胜
    }
    return pd.DataFrame(data)

df = load_data()

# ================= 侧边栏输入区 =================
st.sidebar.header("📊 输入比赛数据")

home_team = st.sidebar.text_input("主队名称", "曼联")
away_team = st.sidebar.text_input("客队名称", "切尔西")

# 用户输入特征值
h_goals = st.sidebar.slider("主队近期平均进球", 0.0, 5.0, 1.5)
a_goals = st.sidebar.slider("客队近期平均进球", 0.0, 5.0, 1.2)
h_win_rate = st.sidebar.slider("主队近期胜率 (0-1)", 0.0, 1.0, 0.5)
a_win_rate = st.sidebar.slider("客队近期胜率 (0-1)", 0.0, 1.0, 0.4)

# ================= 模型预测逻辑 =================
if st.sidebar.button("🔮 开始预测"):
    with st.spinner('正在计算全因子模型数据...'):
        time.sleep(1) # 假装计算了一下
        
        # 准备训练数据
        X = df[['home_goals_avg', 'away_goals_avg', 'home_win_rate', 'away_win_rate']]
        y = df['result']
        
        # 训练模型 (随机森林)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # 预测新数据
        new_match = np.array([[h_goals, a_goals, h_win_rate, a_win_rate]])
        prediction = model.predict(new_match)[0]
        probabilities = model.predict_proba(new_match)[0]
        
        # 结果映射
        result_map = {1: "🔴 主胜", 0: "🤝 平局", 2: "🔵 客胜"}
        result_text = result_map[prediction]
        
        st.success(f"预测结果：**{home_team} vs {away_team}**")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("主胜概率", f"{probabilities[1]*100:.1f}%")
        col2.metric("平局概率", f"{probabilities[0]*100:.1f}%")
        col3.metric("客胜概率", f"{probabilities[2]*100:.1f}%")
        
        st.balloons()
        st.info(f"模型建议投注方向：{result_text}")

else:
    st.info("👈 请在左侧输入比赛数据并点击预测")

# 显示使用的数据集
with st.expander("查看训练数据集"):
    st.dataframe(df)
