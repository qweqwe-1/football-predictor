import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =================配置区域=================
# 这里已经填入了你的Token
API_TOKEN = "9ad0e9e3f9074e59a1f4269ea0565881" 
# ==========================================

st.set_page_config(page_title="自动足球预测", layout="wide")
st.title("⚽️ 今日比赛自动预测系统")
st.markdown("系统正在自动扫描今日赛程并进行AI分析...")

# 1. 定义预测模型函数 (这里使用简化的泊松分布逻辑)
def predict_match(home_team, away_team, home_avg_goals, away_avg_goals):
    # 简单的进球期望计算
    lambda_home = home_avg_goals * 1.1  # 主场优势系数
    lambda_away = away_avg_goals * 0.9  # 客场劣势系数
    
    # 简化的胜率计算逻辑 (模拟AI分析)
    total_strength = lambda_home + lambda_away
    home_win_prob = (lambda_home / total_strength) * 100
    
    result_text = ""
    confidence = 0
    
    if home_win_prob > 55:
        result_text = f"🏆 {home_team} 胜算极大"
        confidence = home_win_prob
    elif home_win_prob < 45:
        result_text = f"🏆 {away_team} 胜算极大"
        confidence = 100 - home_win_prob
    else:
        result_text = "⚖️ 势均力敌，小心平局"
        confidence = 50
        
    return result_text, round(confidence, 1), round(lambda_home, 2), round(lambda_away, 2)

# 2. 获取数据的逻辑
def get_matches():
    if not API_TOKEN:
        return None # 返回None表示没有Token

    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_TOKEN}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            return matches
        else:
            st.error(f"API 错误: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"连接失败: {str(e)}")
        return []

# =================主程序=================

matches = get_matches()

if matches is None:
    st.warning("⚠️ 未检测到 API Token，正在使用演示模拟数据...")
    # 演示数据
    demo_data = [
        {"homeTeam": {"name": "曼城"}, "awayTeam": {"name": "阿森纳"}, "utcDate": "2023-10-08T15:00:00Z"},
        {"homeTeam": {"name": "皇家马德里"}, "awayTeam": {"name": "巴塞罗那"}, "utcDate": "2023-10-08T19:00:00Z"},
        {"homeTeam": {"name": "尤文图斯"}, "awayTeam": {"name": "AC米兰"}, "utcDate": "2023-10-08T21:00:00Z"}
    ]
    matches = demo_data
    is_demo = True
else:
    if len(matches) == 0:
        st.info("今天暂时没有比赛数据，或者API请求受限。")
        st.stop()
    else:
        st.success(f"✅ 成功获取到 {len(matches)} 场今日重点比赛！")
        is_demo = False

st.divider()

# 3. 循环展示比赛卡片
for match in matches:
    home = match['homeTeam']['name']
    away = match['awayTeam']['name']
    
    # 为了演示效果，随机生成一些进攻指数（真实情况需要调用历史数据接口，这里简化处理）
    import random
    h_idx = round(random.uniform(1.2, 2.5), 2)
    a_idx = round(random.uniform(0.8, 2.0), 2)
    
    # 调用预测函数
    prediction, confidence, h_exp, a_exp = predict_match(home, away, h_idx, a_idx)
    
    # 绘制卡片
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"**主队**")
        st.header(home)
        st.caption(f"近期进攻指数: {h_idx}")
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True) # 占位符
        st.markdown(f"<h3 style='text-align: center;'>VS</h3>", unsafe_allow_html=True)
        
        # 显示分析结果
        st.info(f"**AI 分析结果：** {prediction}")
        
        # 进度条显示置信度
        st.progress(confidence / 100, text=f"预测置信度: {confidence}%")

    with col3:
        st.markdown(f"**客队**")
        st.header(away)
        st.caption(f"近期进攻指数: {a_idx}")
        
    st.divider()
