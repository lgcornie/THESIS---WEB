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

/* ===== APP BACKGROUND ===== */
.stApp {
    background: linear-gradient(120deg, #eef2ff 0%, #f8fafc 100%);
    color: #0f172a;
}

/* ===== REMOVE HEADER BAR ===== */
header {visibility: hidden;}
[data-testid="stHeader"] {display: none;}

/* remove top padding */
.block-container {
    padding-top: 0rem;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: #0f172a;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* ===== CARDS ===== */
.card {
    background: rgba(255,255,255,0.92);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

/* ===== TITLES ===== */
.hero-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
}
.hero-sub {
    text-align: center;
    color: #334155;
}

/* ===== BUTTON ===== */
.stButton button {
    color: white !important;
    background: linear-gradient(90deg,#6366f1,#4f46e5);
    font-weight: 700;
    border-radius: 10px;
    padding: 10px 18px;
    border: none;
    transition: 0.2s;
}
.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
}

/* ===== LABEL TEXT ===== */
label {
    color: #0f172a !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* ===== SELECTBOX FIX (IMPORTANT) ===== */

/* nền selectbox */
div[data-baseweb="select"] {
    background-color: #1e293b !important;
    border-radius: 10px !important;
}

/* text hiển thị */
div[data-baseweb="select"] span {
    color: white !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

/* text khi search */
div[data-baseweb="select"] input {
    color: white !important;
    -webkit-text-fill-color: white !important;
    font-weight: 600 !important;
}

/* placeholder */
div[data-baseweb="select"] input::placeholder {
    color: #cbd5e1 !important;
}

/* icon dropdown */
div[data-baseweb="select"] svg {
    fill: white !important;
}

/* ===== ALERT / WARNING ===== */
[data-testid="stAlert"] {
    color: #9a3412 !important;
    font-weight: 600;
}
[data-testid="stAlert"] p {
    color: #9a3412 !important;
}

/* ===== METRIC ===== */
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #0f172a !important;
    opacity: 1 !important;
}

/* ===== NORMAL TEXT ===== */
.stMarkdown p {
    color: #0f172a !important;
}

/* ===== RISK COLORS ===== */
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

    st.markdown("<br><div class='hero-title'>HỆ THỐNG ĐÁNH GIÁ RỦI RO TÀI CHÍNH</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Phân tích nguy cơ kiệt quệ tài chính doanh nghiệp</div><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='card'><b>Số doanh nghiệp</b><h2>{df['ticker'].nunique()}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><b>Số năm dữ liệu</b><h2>{df['year'].nunique()}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><b>Số quan sát</b><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

    # =========================
    # TREEMAP MARKET HEATMAP
    # =========================
    st.markdown("### Bản đồ vốn hóa & rủi ro thị trường")

    tree_df = df.dropna(subset=["market_capitalization","risk_score"])

    selected_year = st.slider(
        "Chọn năm",
        min_value=int(tree_df["year"].min()),
        max_value=int(tree_df["year"].max()),
        value=int(tree_df["year"].max())
    )

    year_df = tree_df[tree_df["year"] == selected_year]

    fig_market = px.treemap(
        year_df,
        path=[px.Constant("Thị trường"), "ticker"],
        values="market_capitalization",
        color="risk_score",
        color_continuous_scale="RdYlGn_r",
        hover_data={
            "market_capitalization":":,.0f",
            "risk_score":":.2f"
        }
    )

    fig_market.update_traces(
        textinfo="label+percent parent",
        textfont_size=14,
        marker=dict(line=dict(width=1,color="white"))
    )

    fig_market.update_layout(
        margin=dict(t=20,l=5,r=5,b=5),
        font=dict(size=14,color="#111"),
        coloraxis_colorbar=dict(title="Risk Score")
    )

    st.plotly_chart(fig_market, use_container_width=True)



    # =========================
    # TOP 10 RISK HIGHEST & LOWEST
    # =========================
    st.markdown("### Top 10 Doanh nghiệp rủi ro cao & thấp nhất")

    top_df = year_df.dropna(subset=["risk_score"]).copy()

    col1, col2 = st.columns(2)

    # ===== TOP 10 RISK CAO =====
    top_high = top_df.sort_values("risk_score", ascending=False).head(10)

    fig_high = px.bar(
        top_high,
        x="risk_score",
        y="ticker",
        orientation="h",
        color="risk_score",
        color_continuous_scale="Reds",
        title="Top 10 Risk Cao Nhất"
    )

    fig_high.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(t=40, l=10, r=10, b=10),
        coloraxis_showscale=False
    )

    col1.plotly_chart(fig_high, use_container_width=True)

    # ===== TOP 10 RISK THẤP =====
    top_low = top_df.sort_values("risk_score", ascending=True).head(10)

    fig_low = px.bar(
        top_low,
        x="risk_score",
        y="ticker",
        orientation="h",
        color="risk_score",
        color_continuous_scale="Greens",
        title="Top 10 Risk Thấp Nhất"
    )

    fig_low.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(t=40, l=10, r=10, b=10),
        coloraxis_showscale=False
    )

    col2.plotly_chart(fig_low, use_container_width=True)

    if st.button("Tra cứu doanh nghiệp"):
        st.session_state.show_search = True
        st.rerun()
# =========================
# SEARCH PAGE
# =========================
else:

    if st.button("⬅ Quay lại"):
        st.session_state.show_search = False
        st.rerun()

    st.markdown("### Tra cứu doanh nghiệp")

    ticker = st.selectbox("Mã cổ phiếu", sorted(df["ticker"].unique()))
    year = st.selectbox("Năm", sorted(df["year"].unique(), reverse=True))

    analyze = st.button("🔍 Phân tích")

    if not analyze:
        st.stop()

    company = df[(df["ticker"] == ticker) & (df["year"] == year)]

    if company.empty:
        st.warning("Không có dữ liệu.")
        st.stop()

    info = company.iloc[0]

    zone = info["risk_zone"]
    if "Safe" in zone or "Green" in zone:
        cls,text="safe","AN TOÀN"
    elif "Grey" in zone:
        cls,text="warn","CẢNH BÁO"
    else:
        cls,text="danger","NGUY CƠ"

    st.markdown(f"""
    <div class='card'>
    <b>Mã CK:</b> {info['ticker']} &nbsp;&nbsp;
    <b>Doanh nghiệp:</b> {info['company_common_name']}<br><br>
    <b>Sàn:</b> {info['exchange']} &nbsp;&nbsp;
    <b>Năm:</b> {year}<br><br>
    <b>Trạng thái:</b> <span class='{cls}'>{text}</span>
    </div>
    """, unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    score = round(info["risk_score"],3)
    color = "#059669" if score<0.3 else "#d97706" if score<0.6 else "#dc2626"

    col1.markdown(f"<div class='card'><b>Risk Score</b><h2 style='color:{color}'>{score}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><b>Risk Zone</b><h2 style='color:{color}'>{info['risk_zone']}</h2></div>", unsafe_allow_html=True)
    # ===== FINANCIAL TABLE =====
    st.markdown("### Chỉ số tài chính")

    financial_cols = [
        "total_assets","total_liabilities","net_income_after_tax",
        "roa","roe","current_ratio","quick_ratio","de_ratio",
        "financial_distress_t"
    ]

    cols = [c for c in financial_cols if c in history.columns]
    st.dataframe(history[["date"] + cols], use_container_width=True)
    # ===== RISK TREND =====
    st.markdown("### Diễn biến Risk Score")
    history = df[df["ticker"]==ticker].sort_values("date")
    st.line_chart(history.set_index("date")["risk_score"])

    #=======HỒ SƠ SỨC KHỎE ====

    st.markdown("### Hồ sơ sức khỏe tài chính")

    latest_data = history.iloc[-1]

    radar_df = pd.DataFrame(dict(
        metric=["ROA","ROE","Current Ratio","Quick Ratio","Debt Ratio"],
        value=[
            latest_data["roa"],
            latest_data["roe"],
            latest_data["current_ratio"],
            latest_data["quick_ratio"],
            latest_data["de_ratio"]
        ]
    ))

    fig_radar = px.line_polar(
        radar_df,
        r="value",
        theta="metric",
        line_close=True,
        title="Financial Health Radar"
    )

    fig_radar.update_traces(fill="toself")

    st.plotly_chart(fig_radar, use_container_width=True)
##=====CẤU TRÚC TÀI CHÍNH====
    st.markdown("### Cấu trúc tài chính")

    fig_struct = px.bar(
        history,
        x="date",
        y=["total_assets","total_liabilities"],
        barmode="group",
        title="Tài sản vs Nợ phải trả"
    )

    st.plotly_chart(fig_struct, use_container_width=True)
###=========BIỂU ĐỒ THANH KHOẢN====
    st.markdown("### Khả năng thanh khoản")

    fig_liquid = px.line(
    history,
    x="date",
    y=["current_ratio","quick_ratio"],
    markers=True,
    title="Chỉ số thanh khoản"
)

    st.plotly_chart(fig_liquid, use_container_width=True)

#==========So sánh Risk với trung bình ngành===========
    st.markdown("### So sánh Risk với thị trường")

    market_avg = df[df["year"]==year]["risk_score"].mean()

    compare_df = pd.DataFrame({
        "Category":["Doanh nghiệp","Trung bình thị trường"],
        "Risk Score":[score, market_avg]
    })

    fig_compare = px.bar(
        compare_df,
        x="Category",
        y="Risk Score",
        text="Risk Score",
        title="So sánh Risk Score"
    )

    st.plotly_chart(fig_compare, use_container_width=True)
    # Tạo history trước
history = df[df["company"] == selected_company].sort_values("year")
    ##==== ROE ROA
    st.markdown("### Hiệu quả sinh lời")
    fig_profit = px.line(
    history,
    x="date",
    y=["roa","roe"],
    markers=True,
    title="Xu hướng ROA & ROE"
    )
    st.plotly_chart(fig_profit, use_container_width=True)

# == CẢNH BÁO TỰ ĐỘNG ===
if not history.empty:
    if history["de_ratio"].iloc[-1] > 2:
        st.error("Doanh nghiệp có đòn bẩy tài chính rất cao")

    if history["current_ratio"].iloc[-1] < 1:
        st.warning("Thanh khoản thấp")

    if history["roa"].iloc[-1] < 0:
        st.warning("Doanh nghiệp đang kinh doanh thua lỗ")
    


    # ===== INVESTMENT RECOMMENDATION =====
    st.markdown("### 📌 Nhận định đầu tư")

    avg_score = history["risk_score"].mean()
    latest = history["risk_score"].iloc[-1]
    trend = history["risk_score"].diff().mean()

    if latest < 0.3 and trend <= 0:
            rec="NÊN ĐẦU TƯ"
            rec_class="safe"
            msg="Rủi ro thấp và xu hướng ổn định/giảm."
    elif latest < 0.6:
            rec="CÂN NHẮC"
            rec_class="warn"
            msg="Rủi ro trung bình, cần theo dõi thêm."
    else:
            rec="KHÔNG NÊN ĐẦU TƯ"
            rec_class="danger"
            msg="Rủi ro cao hoặc xu hướng xấu."

    st.markdown(f"""
        <div class='card'>
        <h3 class='{rec_class}'>{rec}</h3>
        <p>{msg}</p>
        <p><b>Risk trung bình:</b> {round(avg_score,3)}</p>
        <p><b>Risk mới nhất:</b> {round(latest,3)}</p>
        </div>
        """, unsafe_allow_html=True)



