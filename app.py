import math
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# ========== 演示数据（你可以自己改这里的比赛） ==========
MATCHES = [
    {"id": "周一001", "league": "法甲", "home": "布雷斯特", "away": "斯特拉斯堡",
     "kickoff": "03:00", "oh": 3.10, "od": 3.40, "oa": 2.30},
    {"id": "周一002", "league": "西甲", "home": "皇家社会", "away": "塞尔塔",
     "kickoff": "04:00", "oh": 1.85, "od": 3.60, "oa": 4.20},
    {"id": "周一003", "league": "英超", "home": "切尔西", "away": "利物浦",
     "kickoff": "23:30", "oh": 2.50, "od": 3.30, "oa": 2.80},
]

# ========== 泊松模型 ==========
def poisson_pmf(k, lam):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def implied_prob(oh, od, oa):
    ih, id_, ia = 1/oh, 1/od, 1/oa
    total = ih + id_ + ia
    return ih/total, id_/total, ia/total

def predict(m):
    oh, od, oa = implied_prob(m["oh"], m["od"], m["oa"])
    total_xg = 2.5
    s = oh + oa
    lh = total_xg * (oh / s) * 1.15
    la = total_xg * (oa / s)
    # 比分概率矩阵
    mat = {}
    for h in range(5):
        ph = poisson_pmf(h, lh)
        for a in range(5):
            pa = poisson_pmf(a, la)
            mat[(h, a)] = ph * pa
    norm = sum(mat.values())
    mat = {k: v/norm for k, v in mat.items()}
    # 胜平负
    hw = dw = aw = 0
    for (h, a), p in mat.items():
        if h > a: hw += p
        elif h == a: dw += p
        else: aw += p
    # 排序
    probs = [("主胜", hw), ("平局", dw), ("客胜", aw)]
    probs.sort(key=lambda x: x[1], reverse=True)
    direction = " / ".join([p[0] for p in probs])
    primary, secondary = probs[0][0], probs[1][0]
    rec_map = {
        ("平局", "客胜"): "平局防客胜", ("平局", "主胜"): "平局防主胜",
        ("主胜", "平局"): "主胜防平", ("客胜", "平局"): "客胜防平",
        ("主胜", "客胜"): "主胜", ("客胜", "主胜"): "客胜防主胜",
    }
    recommend = rec_map.get((primary, secondary), primary)
    # 比分
    scores = sorted(mat.items(), key=lambda x: x[1], reverse=True)
    main = f"{scores[0][0][0]}-{scores[0][0][1]}"
    backup = " / ".join([f"{h}-{a}" for (h,a),_ in scores[1:3]])
    # 进球
    exp = sum((h+a)*p for (h,a),p in mat.items())
    goals = "1-2 球" if exp < 2 else ("2-3 球" if exp < 3 else "3-4 球")
    # 半全场
    half_full = "平/平（主推）/ 平/客（备选）" if primary == "平局" else \
                "平/主（主推）/ 主/主（备选）" if primary == "主胜" else \
                "平/客（主推）/ 客/客（备选）"
    return {
        "match_id": m["id"], "league": m["league"], "home": m["home"], "away": m["away"],
        "direction": direction, "recommend": recommend,
        "score": f"{main}（主推）/ {backup}", "goals": goals, "half_full": half_full,
        "probs": {"home_win": round(hw,4), "draw": round(dw,4), "away_win": round(aw,4)},
        "xg": f"{lh:.2f} : {la:.2f}"
    }

RECOMMENDS = {m["id"]: predict(m) for m in MATCHES}

# ========== 网页 ==========
HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>足球竞彩预测系统</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:#fff;min-height:100vh;padding:20px}
.container{max-width:800px;margin:0 auto}
h1{text-align:center;margin-bottom:20px}
.match{cursor:pointer;background:rgba(255,255,255,.08);border-radius:10px;padding:15px;margin-bottom:10px;transition:.2s}
.match:hover{background:rgba(255,255,255,.15)}
.id{background:#e94560;padding:3px 8px;border-radius:4px;font-size:.85rem;margin-right:8px}
.teams{font-size:1.1rem;font-weight:bold}
.vs{opacity:.5;margin:0 5px}
.kickoff{float:right;opacity:.6}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.85);justify-content:center;align-items:center}
.modal.show{display:flex}
.box{background:#1a1a2e;border-radius:16px;padding:30px;max-width:450px;width:90%}
.close{float:right;font-size:1.5rem;cursor:pointer;opacity:.7}
.field{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.1)}
.hl{color:#e94560;font-size:1.3rem;font-weight:bold}
</style>
</head>
<body>
<div class="container">
<h1>足球竞彩预测系统</h1>
<div id="list"></div>
</div>
<div class="modal" id="modal"><div class="box">
<span class="close" onclick="document.getElementById('modal').classList.remove('show')">&times;</span>
<div id="content"></div>
</div></div>
<script>
async function load(){
  const res = await fetch('/api/matches');
  const data = await res.json();
  const list = document.getElementById('list');
  data.forEach(m=>{
    const d = document.createElement('div');
    d.className='match';
    d.innerHTML = `<span class="id">${m.id}</span><span class="teams">${m.home}<span class="vs">VS</span>${m.away}</span><span class="kickoff">${m.kickoff}</span>`;
    d.onclick = ()=>showRec(m.id);
    list.appendChild(d);
  });
}
async function showRec(id){
  const res = await fetch('/api/recommend/'+id);
  const d = await res.json();
  document.getElementById('content').innerHTML = `
    <h2>${d.match_id} ${d.league}</h2>
    <h3 style="margin:10px 0">${d.home} vs ${d.away}</h3>
    <p style="opacity:.7;margin-bottom:15px">预期进球 ${d.xg}</p>
    <div class="field"><span>方向</span><span>${d.direction}</span></div>
    <div class="field"><span>推荐</span><span class="hl">${d.recommend}</span></div>
    <div class="field"><span>比分</span><span>${d.score}</span></div>
    <div class="field"><span>进球</span><span>${d.goals}</span></div>
    <div class="field"><span>半全场</span><span>${d.half_full}</span></div>
    <div class="field"><span>概率</span><span>主胜${(d.probs.home_win*100).toFixed(1)}% 平局${(d.probs.draw*100).toFixed(1)}% 客胜${(d.probs.away_win*100).toFixed(1)}%</span></div>
    <p style="margin-top:15px;font-size:.8rem;opacity:.5;text-align:center">⚠️ 数据分析参考，请理性看待</p>
  `;
  document.getElementById('modal').classList.add('show');
}
load();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/matches")
def api_matches():
    return jsonify([{"id": m["id"], "league": m["league"], "home": m["home"], "away": m["away"], "kickoff": m["kickoff"]} for m in MATCHES])

@app.route("/api/recommend/<match_id>")
def api_recommend(match_id):
    if match_id in RECOMMENDS:
        return jsonify(RECOMMENDS[match_id])
    return jsonify({"error": "not found"}), 404

if __name__ == "__main__":
    print("✅ 足球预测系统启动")
    print("🌐 浏览器打开: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
