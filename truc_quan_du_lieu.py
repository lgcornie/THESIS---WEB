import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

# =========================
# 🎨 MODERN UI STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg, #eef2ff 0%, #f8fafc 100%);
    color: #0f172a;
}
header {visibility: hidden;}
[data-testid="stHeader"] {display: none;}
.block-container {padding-top: 0rem;}

[data-testid="stSidebar"] {background: #0f172a;}
[data-testid="stSidebar"] * {color: white !important;}

.card {
    background: rgba(255,255,255,0.92);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

.hero-title {font-size: 42px;font-weight: 800;text-align: center;}
.hero-sub {text-align: center;color: #334155;}

.stButton button {
    color: white !important;
    background: linear-gradient(90deg,#6366f1,#4f46e5);
    font-weight: 700;
    border-radius: 10px;
}
label, .stSelectbox label, .stTextInput label {
    color: #111 !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

.stSelectbox div, .stTextInput div {
    color: #111 !important;
}
.alert-box {
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    font-weight: 600;
    font-size: 16px;
}

.alert-red {
    background-color: #ffe5e5;
    color: #c62828;
    border-left: 6px solid #ef5350;
}

.alert-yellow {
    background-color: #fff8e1;
    color: #8d6e00;
    border-left: 6px solid #fbc02d;
}
/* text trong select box */
div[data-baseweb="select"] span {
    color: #FFFFFF !important;
    font-weight: 600;
}

/* vùng hiển thị giá trị */
div[data-baseweb="select"] > div {
    color: #FFFFFF !important;
}

/* placeholder text */
div[data-baseweb="select"] input {
    color: #FFFFFF !important;
}

/* icon dropdown */
div[data-baseweb="select"] svg {
    fill: #FFFFFF !important;
}
/* ===== SELECT BOX ===== */

/* nền select */
div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    border-radius: 12px !important;
}

/* chữ giá trị đã chọn (AAV, 2024) */
div[data-baseweb="select"] div {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* chữ trong dropdown menu */
ul[role="listbox"] li {
    color: #111 !important;
}

/* icon dropdown */
div[data-baseweb="select"] svg {
    fill: #ffffff !important;
}

/* placeholder */
div[data-baseweb="select"] input {
    color: #ffffff !important;
}

/* fix opacity mờ */
div[data-baseweb="select"] * {
    opacity: 1 !important;
}


.safe {color:#059669;font-weight:700;}
.warn {color:#d97706;font-weight:700;}
.danger {color:#dc2626;font-weight:700;}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return pd.read_excel(Path("data/financial_distress_data.xlsx"))

df = load_data()
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

# =========================
# SESSION CONTROL
# =========================
if "show_search" not in st.session_state:
    st.session_state.show_search = False

# =========================
# DASHBOARD
# =========================
if not st.session_state.show_search:

    st.markdown("<br><div class='hero-title'>ĐÁNH GIÁ RỦI RO TÀI CHÍNH</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Phân tích nguy cơ kiệt quệ tài chính doanh nghiệp</div><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='card'><b>Số doanh nghiệp</b><h2>{df['ticker'].nunique()}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><b>Số năm dữ liệu</b><h2>{df['year'].nunique()}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><b>Số quan sát</b><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

    st.markdown("### Bản đồ vốn hóa & rủi ro thị trường")

    tree_df = df.dropna(subset=["market_capitalization","risk_score"])
    selected_year = st.slider("Chọn năm",
        int(tree_df.year.min()),
        int(tree_df.year.max()),
        int(tree_df.year.max())
    )

    year_df = tree_df[tree_df.year == selected_year]

    fig_market = px.treemap(
        year_df,
        path=[px.Constant("Thị trường"),"ticker"],
        values="market_capitalization",
        color="risk_score",
        color_continuous_scale="RdYlGn_r"
    )

    st.plotly_chart(fig_market, use_container_width=True)

    st.markdown("### Top 10 Doanh nghiệp rủi ro cao & thấp nhất")

    top_df = year_df.dropna(subset=["risk_score"])
    col1,col2 = st.columns(2)

    col1.plotly_chart(
        px.bar(top_df.sort_values("risk_score",ascending=False).head(10),
        x="risk_score",y="ticker",orientation="h",color="risk_score",
        color_continuous_scale="Reds"),
        use_container_width=True)

    col2.plotly_chart(
        px.bar(top_df.sort_values("risk_score").head(10),
        x="risk_score",y="ticker",orientation="h",color="risk_score",
        color_continuous_scale="Greens"),
        use_container_width=True)

    if st.button("Tra cứu doanh nghiệp"):
        st.session_state.show_search=True
        st.rerun()

# =========================
# SEARCH PAGE
# =========================
else:

    if st.button("⬅ Quay lại"):
        st.session_state.show_search=False
        st.rerun()

    st.markdown("### Tra cứu doanh nghiệp")

    ticker = st.selectbox("Mã cổ phiếu", sorted(df.ticker.unique()))
    year = st.selectbox("Năm", sorted(df.year.unique(), reverse=True))

    if not st.button("🔍 Phân tích"):
        st.stop()

    company = df[(df.ticker==ticker)&(df.year==year)]
    if company.empty:
        st.warning("Không có dữ liệu.")
        st.stop()

    info = company.iloc[0]

    history = df[df.ticker==ticker].sort_values("date")

    zone = info["risk_zone"]
    cls,text = ("safe","AN TOÀN") if "Safe" in zone or "Green" in zone else ("warn","CẢNH BÁO") if "Grey" in zone else ("danger","NGUY CƠ")

    st.markdown(f"""
    <div class='card'>
    <b>Mã CK:</b> {info['ticker']} &nbsp;&nbsp;
    <b>Doanh nghiệp:</b> {info['company_common_name']}<br><br>
    <b>Sàn:</b> {info['exchange']} &nbsp;&nbsp;
    <b>Năm:</b> {year}<br><br>
    <b>Trạng thái:</b> <span class='{cls}'>{text}</span>
    </div>
    """, unsafe_allow_html=True)

    score = round(info["risk_score"],3)
    color = "#059669" if score<0.3 else "#d97706" if score<0.6 else "#dc2626"

    c1,c2 = st.columns(2)
    c1.markdown(f"<div class='card'><b>Risk Score</b><h2 style='color:{color}'>{score}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><b>Risk Zone</b><h2 style='color:{color}'>{info['risk_zone']}</h2></div>", unsafe_allow_html=True)

    # ===== TABLE =====
    st.markdown("### Chỉ số tài chính")
    financial_cols=["total_assets","total_liabilities","net_income_after_tax","roa","roe","current_ratio","quick_ratio","de_ratio"]
    cols=[c for c in financial_cols if c in history.columns]
    st.dataframe(history[["date"]+cols], use_container_width=True)

    # ===== RISK TREND =====
    st.markdown("### Diễn biến Risk Score")
    st.line_chart(history.set_index("date")["risk_score"])

    # ===== RADAR =====
    st.markdown("### Hồ sơ sức khỏe tài chính")

    latest = history.iloc[-1]

    radar_df = pd.DataFrame(dict(
        metric=["ROA", "ROE", "Current Ratio", "Quick Ratio", "Debt Ratio"],
        value=[latest.roa, latest.roe, latest.current_ratio, latest.quick_ratio, latest.de_ratio]
    ))

    fig = px.line_polar(
        radar_df,
        r="value",
        theta="metric",
        line_close=True
    )

    fig.update_traces(
        fill="toself",
        line=dict(width=3),
        opacity=0.9
    )

    fig.update_layout(
        polar=dict(
            bgcolor="#07122b",

            radialaxis=dict(
                tickfont=dict(size=13, color="white"),  # số trên vòng tròn
                gridcolor="rgba(255,255,255,0.25)",
                linecolor="rgba(255,255,255,0.6)"
            ),

            angularaxis=dict(
                tickfont=dict(size=14, color="white"),  # ROA ROE...
                gridcolor="rgba(255,255,255,0.15)",
                linecolor="rgba(255,255,255,0.6)"
            )
        ),

        paper_bgcolor="#07122b",
        plot_bgcolor="#07122b",
    )

    st.plotly_chart(fig, use_container_width=True)


    # ===== STRUCTURE =====
    st.markdown("### Cấu trúc tài chính")
    st.plotly_chart(px.bar(history,x="date",y=["total_assets","total_liabilities"],barmode="group"),use_container_width=True)

    # ===== LIQUIDITY =====
    st.markdown("### Khả năng thanh khoản")
    st.plotly_chart(px.line(history,x="date",y=["current_ratio","quick_ratio"],markers=True),use_container_width=True)

    # ===== PROFITABILITY =====
    st.markdown("### Hiệu quả sinh lời")
    st.plotly_chart(px.line(history,x="date",y=["roa","roe"],markers=True),use_container_width=True)

    # ===== SO SÁNH =====
    st.markdown("### So sánh Risk với thị trường")
    market_avg=df[df.year==year]["risk_score"].mean()
    compare=pd.DataFrame({"Category":["Doanh nghiệp","Trung bình thị trường"],"Risk Score":[score,market_avg]})
    st.plotly_chart(px.bar(compare,x="Category",y="Risk Score",text="Risk Score"),use_container_width=True)

    # ===== CẢNH BÁO =====
    if latest.de_ratio>2: st.markdown('<div class="alert-box alert-red">Đòn bẩy tài chính rất cao</div>', unsafe_allow_html=True)
    if latest.current_ratio<1: st.markdown('<div class="alert-box alert-red">Thanh khoản thấp</div>', unsafe_allow_html=True)
    if latest.roa<0: st.markdown('<div class="alert-box alert-red">Doanh nghiệp đang thua lỗ</div>', unsafe_allow_html=True)

    # ===== RECOMMEND =====
    st.markdown("### 📌 Nhận định đầu tư")
    avg=history.risk_score.mean()
    trend=history.risk_score.diff().mean()

    if score<0.3 and trend<=0:
        rec,cls,msg="NÊN ĐẦU TƯ","safe","Rủi ro thấp và ổn định."
    elif score<0.6:
        rec,cls,msg="CÂN NHẮC","warn","Rủi ro trung bình."
    else:
        rec,cls,msg="KHÔNG NÊN ĐẦU TƯ","danger","Rủi ro cao."

    st.markdown(f"<div class='card'><h3 class='{cls}'>{rec}</h3><p>{msg}</p></div>", unsafe_allow_html=True)
