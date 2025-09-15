import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# ---------------------------
# Backend API configuration
# ---------------------------
API_BASE = "http://localhost:5001"  # Flask backend URL

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #f8f6fb;
        font-family: 'Segoe UI', sans-serif;
    }
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #6f42c1;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 18px;
        text-align: center;
        color: #8e44ad;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Header
# ---------------------------
st.markdown("<div class='main-title'>📊 Sales Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Streamlit + Flask API</div>", unsafe_allow_html=True)

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.header("🔍 Filters")

source = st.sidebar.selectbox("Data Source", ["xlsx", "sql"])
product = st.sidebar.text_input("Product Line")
city = st.sidebar.text_input("City")
gender = st.sidebar.selectbox("Gender", ["", "Male", "Female"])
payment = st.sidebar.text_input("Payment")
limit = st.sidebar.number_input("Limit", min_value=0, value=0)
offset = st.sidebar.number_input("Offset", min_value=0, value=0)

if st.sidebar.button("Fetch Data"):
    params = {"source": source}
    if product:
        params["product"] = product
    if city:
        params["city"] = city
    if gender:
        params["gender"] = gender
    if payment:
        params["payment"] = payment
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset

    try:
        resp = requests.get(f"{API_BASE}/api/sales", params=params, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            if not data:
                st.warning("⚠️ No records found with these filters.")
            else:
                df = pd.DataFrame(data)
                st.success(f"✅ Fetched {len(df)} records from API")

                # ---------------------------
                # KPI Metrics
                # ---------------------------
                total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
                avg_rating = df["Rating"].mean() if "Rating" in df.columns else 0
                total_orders = len(df)
                avg_cogs = df["cogs"].mean() if "cogs" in df.columns else 0

                kpi1, kpi2, kpi3, kpi4 = st.columns(4)

                with kpi1:
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(135deg, #8e44ad, #d2b4de);
                                    padding: 20px; border-radius: 12px; text-align: center;
                                    color: white; font-weight: bold;'>
                            💰 Total Sales <br><span style='font-size:24px;'>${total_sales:,.2f}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with kpi2:
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(135deg, #6f42c1, #bb8fce);
                                    padding: 20px; border-radius: 12px; text-align: center;
                                    color: white; font-weight: bold;'>
                            ⭐ Avg Rating <br><span style='font-size:24px;'>{avg_rating:.2f}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with kpi3:
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(135deg, #512da8, #9575cd);
                                    padding: 20px; border-radius: 12px; text-align: center;
                                    color: white; font-weight: bold;'>
                            🛒 Orders <br><span style='font-size:24px;'>{total_orders}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with kpi4:
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(135deg, #7b1fa2, #ce93d8);
                                    padding: 20px; border-radius: 12px; text-align: center;
                                    color: white; font-weight: bold;'>
                            🏭 Avg COGS <br><span style='font-size:24px;'>${avg_cogs:,.2f}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # ---------------------------
                # Visualizations
                # ---------------------------
                st.subheader("📊 Visualizations")
                tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
                    "📊 By Product Line", "💳 By Payment", "⏳ Over Time", "🏙️ By City", "🔀 Scatter/Box", "🌞 Sunburst", "🟩 Treemap", "📦 Box Plot", "🔥 Heatmap"
                ])

                # 1. Sales by Product Line
                with tab1:
                    if "Product line" in df.columns and "Sales" in df.columns:
                        sales_by_product = df.groupby("Product line", as_index=False)["Sales"].sum()
                        fig1 = px.bar(
                            sales_by_product, x="Product line", y="Sales",
                            color="Sales", text_auto=True,
                            title="✨ Total Sales by Product Line",
                            color_continuous_scale=px.colors.sequential.Purples
                        )
                        fig1.update_traces(
                            hovertemplate="<b>%{x}</b><br>Sales: %{y:,.2f}",
                            marker=dict(line=dict(color="white", width=2)),
                            selected=dict(marker=dict(opacity=1.0)),
                            unselected=dict(marker=dict(opacity=0.4))
                        )
                        st.plotly_chart(fig1, use_container_width=True)

                # 2. Sales Distribution by Payment (Pie)
                with tab2:
                    if "Payment" in df.columns and "Sales" in df.columns:
                        custom_colors = ["#6f42c1", "#8e44ad", "#a569bd", "#bb8fce", "#d2b4de"]

                        fig2 = px.pie(
                            df, names="Payment", values="Sales",
                            title="💳 Sales Distribution by Payment Method",
                            hole=0.45,
                            color_discrete_sequence=custom_colors
                        )
                        fig2.update_traces(
                            textinfo="percent+label",
                            hovertemplate="<b>%{label}</b><br>Sales: %{value:,.2f}<br>Share: %{percent}",
                            pull=[0.05] * df["Payment"].nunique(),
                            marker=dict(line=dict(color="white", width=2)),
                            hoverlabel=dict(bgcolor="white", font_size=14, font_color="#6f42c1")
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                # 3. Sales Over Time
                with tab3:
                    for col in ["Date", "Invoice Date", "date"]:
                        if col in df.columns and "Sales" in df.columns:
                            df[col] = pd.to_datetime(df[col], errors="coerce")
                            sales_over_time = df.groupby(col, as_index=False)["Sales"].sum()
                            fig3 = px.line(
                                sales_over_time, x=col, y="Sales",
                                title=f"📅 Sales Over Time ({col})",
                                markers=True, color_discrete_sequence=["#6f42c1"]
                            )
                            fig3.update_traces(
                                hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Sales: %{y:,.2f}",
                                line=dict(width=3)
                            )
                            st.plotly_chart(fig3, use_container_width=True)
                            break

                # 4. Sales by City
                with tab4:
                    if "City" in df.columns and "Sales" in df.columns:
                        sales_by_city = df.groupby("City", as_index=False)["Sales"].sum()
                        fig4 = px.bar(
                            sales_by_city, x="City", y="Sales",
                            color="Sales", text_auto=True,
                            title="🏙️ Total Sales by City",
                            color_continuous_scale=px.colors.sequential.Blues
                        )
                        fig4.update_traces(
                            hovertemplate="<b>%{x}</b><br>Sales: %{y:,.2f}",
                            marker=dict(line=dict(color="white", width=2)),
                            selected=dict(marker=dict(opacity=1.0)),
                            unselected=dict(marker=dict(opacity=0.4))
                        )
                        st.plotly_chart(fig4, use_container_width=True)

                # 5. Scatter + Box Plot
                with tab5:
                    if "Quantity" in df.columns and "Sales" in df.columns:
                        fig5 = px.scatter(
                            df, x="Quantity", y="Sales",
                            size="Sales", color="Product line",
                            hover_data=["City", "Payment"],
                            title="📦 Quantity vs Sales by Product Line",
                            color_discrete_sequence=px.colors.sequential.Purples
                        )
                        fig5.update_traces(
                            hovertemplate="<b>Qty %{x}</b><br>Sales: %{y:,.2f}",
                            marker=dict(line=dict(width=1, color="white"))
                        )
                        st.plotly_chart(fig5, use_container_width=True)

                    if "Product line" in df.columns and "Rating" in df.columns:
                        fig_box = px.box(
                            df, x="Product line", y="Rating", color="Product line",
                            title="📦 Rating Distribution by Product Line"
                        )
                        fig_box.update_traces(
                            hovertemplate="<b>%{x}</b><br>Rating: %{y:.2f}",
                            marker=dict(outliercolor="red", line=dict(width=1))
                        )
                        st.plotly_chart(fig_box, use_container_width=True)

                # 6. Sunburst Chart
                with tab6:
                    if {"City", "Product line", "Sales"}.issubset(df.columns):
                        fig_sunburst = px.sunburst(
                            df, path=["City", "Product line"], values="Sales",
                            color="Sales", color_continuous_scale=px.colors.sequential.Purples,
                            title="🌞 Sales Hierarchy (City → Product Line)"
                        )
                        fig_sunburst.update_traces(
                            hovertemplate="<b>%{label}</b><br>Sales: %{value:,.2f}"
                        )
                        st.plotly_chart(fig_sunburst, use_container_width=True)

                # 7. Treemap
                with tab7:
                    if {"City", "Product line", "Sales"}.issubset(df.columns):
                        fig_treemap = px.treemap(
                            df, path=["City", "Product line"], values="Sales",
                            color="Sales", color_continuous_scale=px.colors.sequential.Blues,
                            title="🟩 Sales Treemap (City → Product Line)"
                        )
                        st.plotly_chart(fig_treemap, use_container_width=True)

                # 8. Box Plot (Sales by Gender)
                with tab8:
                    if {"Gender", "Sales"}.issubset(df.columns):
                        fig_box_gender = px.box(
                            df, x="Gender", y="Sales", color="Gender",
                            title="📦 Sales Distribution by Gender",
                            color_discrete_sequence=["#6f42c1", "#a569bd"]
                        )
                        st.plotly_chart(fig_box_gender, use_container_width=True)

                # 9. Heatmap (City vs Product Line)
                with tab9:
                    if {"City", "Product line", "Sales"}.issubset(df.columns):
                        pivot = df.pivot_table(index="City", columns="Product line", values="Sales", aggfunc="sum", fill_value=0)
                        fig_heatmap = ff.create_annotated_heatmap(
                            z=pivot.values,
                            x=pivot.columns.tolist(),
                            y=pivot.index.tolist(),
                            colorscale="Purples",
                            showscale=True
                        )
                        fig_heatmap.update_layout(title="🔥 Sales Heatmap (City vs Product Line)")
                        st.plotly_chart(fig_heatmap, use_container_width=True)

        else:
            st.error(f"❌ API request failed ({resp.status_code}): {resp.text}")

    except Exception as e:
        st.error(f"🚨 Could not connect to API: {e}")
