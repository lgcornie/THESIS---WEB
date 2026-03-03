import streamlit as st
import pandas as pd
from pathlib import Path
import Trực quan dữ liệu 
import Ứng dụng mô hình
st.set_page_config(page_title="KHÓA LUẬN TỐT NGHIỆP", layout="wide")

# =========================================================
# 🎨 CSS – MODERN GLASS UI
# =========================================================
st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(120deg, #eef2ff 0%, #f8fafc 100%);
    color: #0f172a;
}

/* Header hidden line */
[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Glass cards */
.card {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* Hero title */
.hero-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    color: #1e293b;
}

.hero-sub {
    text-align: center;
    font-size: 18px;
    color: #475569;
    margin-top: -10px;
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg,#6366f1,#4f46e5);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 10px 18px;
    transition: 0.25s;
}
.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

/* Tables */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Titles */
h2, h3 {
    color: #1e293b;
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: #e2e8f0;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 🏆 HERO HEADER
# =========================================================
st.markdown("<div class='hero-title'>PHÂN TÍCH KIỆT QUỆ TÀI CHÍNH</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>Ứng dụng Machine Learning trong dự báo rủi ro doanh nghiệp</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# 👨‍🎓 THÀNH VIÊN (CARD)
# =========================================================

st.subheader("- Sinh viên thực hiện")

members = [("Ngô Lam Giang", "K224141656")]
df_members = pd.DataFrame(members, columns=["Họ và tên", "MSSV"])
df_members.index = df_members.index + 1
df_members.index.name = "STT"

st.dataframe(df_members, use_container_width=True)


# =========================================================
# 📊 GIỚI THIỆU HỆ THỐNG
# =========================================================

st.subheader("- Giới thiệu hệ thống")

st.markdown("""
Trang web được xây dựng nhằm trình bày dữ liệu tài chính sử dụng trong quá trình
huấn luyện mô hình **Machine Learning** để dự đoán nguy cơ kiệt quệ tài chính.

### - Chức năng chính

**Trực quan dữ liệu**
- Hiển thị dữ liệu tài chính doanh nghiệp  
- Giúp hiểu rõ đặc trưng đầu vào  

**Ứng dụng mô hình**
- Dự đoán khả năng gặp khó khăn tài chính  
- Hỗ trợ đánh giá rủi ro doanh nghiệp  

### - Mục tiêu
Cung cấp công cụ trực quan giúp người dùng hiểu dữ liệu và
minh họa khả năng dự báo của mô hình.
""")

st.markdown("</div>", unsafe_allow_html=True)

