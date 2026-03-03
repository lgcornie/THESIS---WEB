import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import shap
import streamlit as st

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_curve, roc_auc_score, accuracy_score, ConfusionMatrixDisplay

st.set_page_config(layout="wide")
st.markdown("""
<style>
.stNumberInput input {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 12px !important;
    font-size: 16px !important;
}
/* ===== BACKGROUND ===== */
.stApp {
    background: linear-gradient(120deg, #eef2ff 0%, #f8fafc 100%);
    color: #0f172a;
}

/* remove header */
header {visibility:hidden;}
[data-testid="stHeader"] {display:none;}
.block-container {padding-top: 0rem;}

/* sidebar */
[data-testid="stSidebar"] {
    background:#0f172a;
}
[data-testid="stSidebar"] * {
    color:white !important;
}

/* ===== GLASS CARD ===== */
.card {
    background: rgba(255,255,255,0.92);
    border-radius:16px;
    padding:22px;
    box-shadow:0 8px 25px rgba(0,0,0,0.08);
    margin-bottom:20px;
}

/* titles */
h1, h2, h3 {
    color:#0f172a !important;
    font-weight:700;
}

/* ===== METRIC ===== */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.92);
    padding:16px;
    border-radius:14px;
    box-shadow:0 4px 14px rgba(0,0,0,0.06);
}
[data-testid="stMetricLabel"] {color:#64748b;}
[data-testid="stMetricValue"] {color:#0f172a; font-weight:700;}

/* ===== BUTTON ===== */
.stButton button {
    background: linear-gradient(90deg,#6366f1,#4f46e5);
    color:white !important;
    font-weight:700;
    border-radius:10px;
    padding:10px 18px;
    border:none;
    transition:0.2s;
}
.stButton button:hover {
    transform:translateY(-1px);
    box-shadow:0 4px 14px rgba(0,0,0,0.15);
}

/* ===== INPUT ===== */
label {
    color:#0f172a !important;
    font-weight:600;
}

input {
    color:#0f172a !important;
}

/* ===== DATAFRAME ===== */
div[data-testid="stDataFrame"] {
    border-radius:12px;
    overflow:hidden;
}

/* ===== PLOTS ===== */
.js-plotly-plot .plotly,
.element-container canvas {
    background: transparent !important;
}

/* ===== RESULT BOX ===== */
.result-box {
    padding:18px;
    border-radius:14px;
    font-weight:700;
    text-align:center;
    margin-top:10px;
}

.safe-box {
    background:#ecfdf5;
    color:#059669;
}

.warn-box {
    background:#fff7ed;
    color:#d97706;
}

.danger-box {
    background:#fef2f2;
    color:#dc2626;
}

/* risk colors */
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
    path = Path("data/financial_distress_data.xlsx")
    df = pd.read_excel(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# =========================
# PREPARE DATA
# =========================
df["year"] = df["date"].dt.year
df = df.dropna(subset=["financial_distress_t_plus_1"])

train = df[df["year"] <= 2022]
test  = df[df["year"] > 2022]

target = "financial_distress_t_plus_1"

features = [
    "roa","roe","current_ratio",
    "quick_ratio","de_ratio",
    "total_assets","total_liabilities"
]

X_train = train[features]
y_train = train[target]
X_test  = test[features]
y_test  = test[target]

# =========================
# TRAIN MODELS (CACHE)
# =========================
@st.cache_resource
def train_models(X_train, y_train):
    log_model = LogisticRegression(max_iter=2000)
    rf_model  = RandomForestClassifier(n_estimators=300, random_state=42)
    xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')

    log_model.fit(X_train, y_train)
    rf_model.fit(X_train, y_train)
    xgb_model.fit(X_train, y_train)

    return log_model, rf_model, xgb_model

log_model, rf_model, xgb_model = train_models(X_train, y_train)

# =========================
# PREDICTIONS
# =========================
log_prob = log_model.predict_proba(X_test)[:,1]
rf_prob  = rf_model.predict_proba(X_test)[:,1]
xgb_prob = xgb_model.predict_proba(X_test)[:,1]

log_auc = roc_auc_score(y_test, log_prob)
rf_auc  = roc_auc_score(y_test, rf_prob)
xgb_auc = roc_auc_score(y_test, xgb_prob)

rf_acc = accuracy_score(y_test, rf_model.predict(X_test))
best_auc = max(log_auc, rf_auc, xgb_auc)

# =========================
# HEADER
# =========================
st.title("Financial Distress Prediction Dashboard")
st.write("So sánh & giải thích mô hình dự đoán kiệt quệ tài chính")

# =========================
# KPI
# =========================
c1, c2, c3 = st.columns(3)

c1.markdown(f"<div class='card'><b>Best AUC</b><h2>{best_auc:.3f}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><b>RF Accuracy</b><h2>{rf_acc:.2%}</h2></div>", unsafe_allow_html=True)
c3.markdown("<div class='card'><b>Best Model</b><h2>Random Forest</h2></div>", unsafe_allow_html=True)


# =========================
# MODEL PERFORMANCE
# =========================
st.subheader("Model Performance")

results = pd.DataFrame({
    "Model": ["Logistic Regression", "Random Forest", "XGBoost"],
    "AUC": [log_auc, rf_auc, xgb_auc]
}).sort_values("AUC", ascending=False)

st.dataframe(results, use_container_width=True)

# =========================
# ROC CURVE
# =========================
st.subheader("ROC Curve")

fig, ax = plt.subplots(figsize=(4.2,3.2), dpi=120)

for name, prob in [
    ("Logistic", log_prob),
    ("Random Forest", rf_prob),
    ("XGBoost", xgb_prob)
]:
    fpr, tpr, _ = roc_curve(y_test, prob)
    ax.plot(fpr, tpr, label=name)

ax.plot([0,1],[0,1],'--')
ax.legend()
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")

fig.patch.set_alpha(0)
st.pyplot(fig)
best_model = max(
    [("Logistic Regression", log_auc),
     ("Random Forest", rf_auc),
     ("XGBoost", xgb_auc)],
    key=lambda x: x[1]
)

st.info(
    f"Mô hình **{best_model[0]}** có khả năng phân biệt tốt nhất với AUC = {best_model[1]:.3f}. "
    "AUC càng gần 1 cho thấy mô hình dự đoán càng chính xác."
)


# =========================
# CONFUSION MATRIX
# =========================
st.subheader("Confusion Matrix")

fig2, ax2 = plt.subplots(figsize=(3.2,3.2), dpi=120)
ConfusionMatrixDisplay.from_estimator(rf_model, X_test, y_test, ax=ax2)
fig2.patch.set_alpha(0)
st.pyplot(fig2)
st.info(
    f"Mô hình Random Forest đạt độ chính xác {rf_acc:.2%}. "
    "Ma trận nhầm lẫn cho thấy khả năng phân loại đúng giữa doanh nghiệp "
    "kiệt quệ tài chính và doanh nghiệp khỏe mạnh."
)


st.subheader("Prediction Probability Distribution")

fig_prob, ax_prob = plt.subplots(figsize=(4,2.8), dpi=120)

ax_prob.hist(rf_prob[y_test==0], bins=30, alpha=0.6, label="Không distress")
ax_prob.hist(rf_prob[y_test==1], bins=30, alpha=0.6, label="Distress")

ax_prob.legend()
ax_prob.set_xlabel("Predicted Probability")
fig_prob.patch.set_alpha(0)
st.pyplot(fig_prob)
st.info(
    "Phân bố xác suất dự đoán cho thấy mức độ tách biệt giữa hai nhóm doanh nghiệp. "
    "Khoảng cách càng lớn chứng tỏ mô hình phân loại càng tốt."
)

# =========================
# FEATURE IMPORTANCE
# =========================
st.subheader("Feature Importance")

importance = pd.Series(
    rf_model.feature_importances_,
    index=features
).sort_values()

fig3, ax3 = plt.subplots(figsize=(4,2.6), dpi=120)
ax3.tick_params(labelsize=8)
importance.plot.barh(ax=ax3)
fig3.patch.set_alpha(0)
st.pyplot(fig3)
top_feature = importance.index[-1]

st.info(
    f"Biến quan trọng nhất ảnh hưởng đến dự đoán là **{top_feature}**. "
    "Điều này cho thấy chỉ số này đóng vai trò then chốt trong việc đánh giá "
    "rủi ro kiệt quệ tài chính."
)


# =========================
# SHAP EXPLAINABILITY (FIXED)
# =========================
st.subheader("Model Explainability (SHAP)")

import shap
import matplotlib.pyplot as plt

# cache explainer
@st.cache_resource
def load_explainer(_model):
    return shap.TreeExplainer(_model)

explainer = load_explainer(rf_model)

# lấy mẫu
sample_shap = X_test.sample(min(200, len(X_test)), random_state=42)

# tính shap values
shap_values = explainer.shap_values(sample_shap)

# chọn class distress = 1
shap_class = shap_values[1]

plt.figure(figsize=(6,4), dpi=120)

shap.summary_plot(
    shap_values[:,:,1],
    sample_shap,
    show=False,
    max_display=15
)

plt.tight_layout()
st.pyplot(plt.gcf())
plt.close()


st.info(
    "Biểu đồ SHAP cho thấy mức độ ảnh hưởng của từng biến đến dự đoán. "
    "Biến ở phía trên có tác động mạnh hơn, trong khi màu sắc thể hiện "
    "giá trị cao (đỏ) hoặc thấp (xanh) ảnh hưởng đến xác suất kiệt quệ."
)

# =========================
# DEMO PREDICTION
# =========================
st.subheader("Predict Financial Risk")

col1, col2, col3 = st.columns(3)

roa = col1.number_input("ROA", value=0.05)
roe = col2.number_input("ROE", value=0.01)
de_ratio = col3.number_input("Debt/Equity", value=1.0)

current_ratio = col1.number_input("Current Ratio", value=1.5)
quick_ratio   = col2.number_input("Quick Ratio", value=1.2)
assets        = col3.number_input("Total Assets", value=1000000.0)
liabilities   = col1.number_input("Total Liabilities", value=500000.0)

if st.button("Dự đoán nguy cơ"):

    sample = pd.DataFrame([[roa, roe, current_ratio, quick_ratio,
                            de_ratio, assets, liabilities]],
                          columns=features)

    prob = rf_model.predict_proba(sample)[0][1]

    if prob < 0.3:
        css_class = "safe-box"
        text = "Nguy cơ thấp"
    elif prob < 0.6:
        css_class = "warn-box"
        text = "Cảnh báo"
    else:
        css_class = "danger-box"
        text = "Nguy cơ cao"

    st.markdown(
        f"<div class='result-box {css_class}'>{text} ({prob:.2f})</div>",
        unsafe_allow_html=True
    )

    # ===== SHAP LOCAL EXPLANATION (FIXED) =====
    st.write("### Yếu tố ảnh hưởng dự đoán")

    shap_val = explainer(sample)

    plt.figure(figsize=(3.6, 2.4), dpi=120)

    shap.plots.waterfall(shap_val[0, :, 1], show=False)

    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()


