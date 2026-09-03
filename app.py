import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =================配置区域=================
# 如果你有 API Token，请填在这里；如果没有，留空即可使用演示模式
API_TOKEN = "" 
# ==========================================

st.set_page_config(page_title="自动足球预测", layout="wide")
st.title("⚽️ 今日比赛自动预测系统")
st.markdown("系统正在自动扫描今日赛程并进行AI分析...")

# 1. 定义预测模型函数 (这里使用简化的泊松分布逻辑)
def predict_match(home_team, away_team, home_avg_goals, away_avg_goals):
    # 简单的进球期望计算
    lambda_home = home_avg_goals * 1.2  # 假设主场优势系数 1.2
    lambda_away = away_avg_goals * 0.8
    
    # 简化版胜率计算 (基于进球期望差值)
    diff = lambda_home - lambda_away
    
    if diff > 0.5:
        result = f"🏆 **{home_team}** 胜算极大"
        prob = min(90, 50 + diff * 20)
    elif diff < -0.5:
        result = f"🏆 **{away_team}** 胜算极大"
        prob = min(90, 50 + abs(diff) * 20)
    else:
        result = "🤝 **势均力敌 / 平局概率高**"
        prob = 40
        
    return result, round(prob, 1)

# 2. 获取数据的函数
def get_today_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {'X-Auth-Token': API_TOKEN}
    
    # 如果没有填 Token，生成模拟数据供测试
    if not API_TOKEN:
        st.warning("⚠️ 未检测到 API Token，正在使用**演示模拟数据**...")
        return [
            {"homeTeam": {"name": "曼城"}, "awayTeam": {"name": "阿森纳"}, "utcDate": "2023-10-27T20:00:00Z"},
            {"homeTeam": {"name": "皇家马德里"}, "awayTeam": {"name": "巴塞罗那"}, "utcDate": "2023-10-27T21:00:00Z"},
            {"homeTeam": {"name": "尤文图斯"}, "awayTeam": {"name": "AC米兰"}, "utcDate": "2023-10-27T22:00:00Z"},
        ]

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('matches', [])
        else:
            st.error(f"API 请求失败: {response.status_code}。请检查 Token。")
            return []
    except Exception as e:
        st.error(f"发生错误: {e}")
        return []

# 3. 主程序逻辑
matches = get_today_matches()

if matches:
    st.success(f"✅ 成功获取到 {len(matches)} 场今日重点比赛！")
    
    # 创建展示卡片
    for match in matches:
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        time = match['utcDate'].split('T')[0] # 只取日期部分
        
        # 模拟随机数据 (因为免费API通常不直接给近期平均进球数，需要复杂计算，这里为了演示自动化，我们随机生成实力值)
        # 在实际生产中，这里应该去查数据库获取两队历史数据
        import random
        h_strength = random.uniform(1.0, 2.5) 
        a_strength = random.uniform(0.8, 2.2)
        
        prediction, confidence = predict_match(home, away, h_strength, a_strength)
        
        # 绘制界面卡片
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.metric(label="主队", value=home)
                st.caption(f"近期进攻指数: {h_strength:.2f}")
                
            with col2:
                st.markdown(f"### VS")
                st.info(f"**AI 分析结果**: {prediction}")
                st.progress(confidence / 100, text=f"预测置信度: {confidence}%")
                
            with col3:
                st.metric(label="客队", value=away)
                st.caption(f"近期进攻指数: {a_strength:.2f}")
else:
    st.info("今天暂无顶级联赛比赛，或 API 未配置。")

st.divider()
st.caption("数据来源: Football-Data.org | 预测仅供娱乐参考")
