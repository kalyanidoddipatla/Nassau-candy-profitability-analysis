import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Candy Profitability", page_icon="🍬", layout="wide")

# ---- Custom color theme (consistent across all charts) ----
DIVISION_COLORS = {"Chocolate": "#7B3F00", "Sugar": "#E63946", "Other": "#457B9D"}

# ---- Load Data ----
df = pd.read_csv("data/nassau_candy_cleaned.csv")
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Gross Margin %'] = (df['Gross Profit'] / df['Sales']) * 100

# ---- Product -> Factory mapping (from project reference table) ----
FACTORY_MAP = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar - Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Kazookles": "The Other Factory",
}
df['Factory'] = df['Product Name'].map(FACTORY_MAP).fillna("Unmapped")

st.title("🍬 Nassau Candy Distributor")
st.caption("Product Line Profitability & Margin Performance Analysis")
st.divider()

# ---- Sidebar Filters ----
st.sidebar.header("🔎 Filters")

date_range = st.sidebar.date_input(
    "Order Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

division_filter = st.sidebar.multiselect(
    "Division",
    options=df['Division'].unique(),
    default=df['Division'].unique()
)

margin_threshold = st.sidebar.slider(
    "Minimum Margin % Filter",
    min_value=0, max_value=100, value=0
)

search_product = st.sidebar.text_input("Search Product Name")

# ---- Apply Filters ----
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1])) &
    (df['Division'].isin(division_filter)) &
    (df['Gross Margin %'] >= margin_threshold)
]

if search_product:
    filtered_df = filtered_df[filtered_df['Product Name'].str.contains(search_product, case=False)]

# ---- KPI Metric Cards ----
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Gross Profit'].sum()
avg_margin = filtered_df['Gross Margin %'].mean() if len(filtered_df) else 0
total_orders = filtered_df['Order ID'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📈 Total Profit", f"${total_profit:,.0f}")
col3.metric("📊 Avg Margin", f"{avg_margin:.1f}%")
col4.metric("🧾 Total Orders", f"{total_orders:,}")

st.divider()

# ---- Tabs for 4 Modules ----
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Product Profitability", "🏭 Division Performance", "⚠️ Cost vs Margin", "📉 Pareto Analysis", "🏗️ Factory Performance"
])

with tab1:
    st.subheader("Product-Level Profitability")
    product_summary = filtered_df.groupby('Product Name').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Avg_Margin=('Gross Margin %', 'mean')
    ).reset_index().sort_values('Total_Profit', ascending=False)

    # Margin volatility: std deviation of monthly margin per product
    monthly = filtered_df.groupby(['Product Name', filtered_df['Order Date'].dt.to_period('M')]).agg(
        S=('Sales', 'sum'), P=('Gross Profit', 'sum')
    ).reset_index()
    monthly['Monthly_Margin'] = monthly['P'] / monthly['S'] * 100
    volatility = monthly.groupby('Product Name')['Monthly_Margin'].std().reset_index()
    volatility.columns = ['Product Name', 'Margin_Volatility']
    volatility['Margin_Volatility'] = volatility['Margin_Volatility'].fillna(0).round(4)
    product_summary = product_summary.merge(volatility, on='Product Name', how='left')

    fig1 = px.bar(
        product_summary, x='Product Name', y='Total_Profit',
        title="Profit Leaderboard by Product",
        labels={"Total_Profit": "Total Profit ($)", "Product Name": ""},
        color='Total_Profit', color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.dataframe(
        product_summary.rename(columns={
            "Total_Sales": "Total Sales ($)", "Total_Profit": "Total Profit ($)",
            "Avg_Margin": "Avg Margin (%)", "Margin_Volatility": "Margin Volatility (std)"
        }),
        use_container_width=True, hide_index=True
    )

    if len(product_summary) > 0:
        top_product = product_summary.iloc[0]
        low_margin_flag = product_summary[product_summary['Avg_Margin'] < product_summary['Avg_Margin'].mean()]
        st.success(f"🏆 **{top_product['Product Name']}** is the top performer, contributing **${top_product['Total_Profit']:,.0f}** in profit.")
        if len(low_margin_flag) > 0:
            st.info(f"📉 **{len(low_margin_flag)} of {len(product_summary)} products** are below average margin — review pricing for these.")
        if product_summary['Margin_Volatility'].max() < 0.01:
            st.success("📐 Margin volatility is near zero across all products — margins are stable month-to-month, with no seasonal drift.")

with tab2:
    st.subheader("Division Performance")
    division_summary = filtered_df.groupby('Division').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Avg_Margin=('Gross Margin %', 'mean')
    ).reset_index()

    fig2 = px.bar(
        division_summary, x='Division', y=['Total_Sales', 'Total_Profit'],
        barmode='group', title="Revenue vs Profit by Division",
        labels={"value": "Amount ($)", "variable": "Metric"},
        color_discrete_map={"Total_Sales": "#A8DADC", "Total_Profit": "#1D3557"}
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(
        division_summary.rename(columns={
            "Total_Sales": "Total Sales ($)", "Total_Profit": "Total Profit ($)", "Avg_Margin": "Avg Margin (%)"
        }),
        use_container_width=True, hide_index=True
    )

    if len(division_summary) > 0:
        division_summary['Revenue_Share'] = (division_summary['Total_Sales'] / division_summary['Total_Sales'].sum()) * 100
        division_summary['Profit_Share'] = (division_summary['Total_Profit'] / division_summary['Total_Profit'].sum()) * 100
        top_div = division_summary.sort_values('Total_Profit', ascending=False).iloc[0]
        imbalanced = division_summary[division_summary['Profit_Share'] < division_summary['Revenue_Share'] - 5]

        st.success(f"🏭 **{top_div['Division']}** leads with **${top_div['Total_Profit']:,.0f}** profit ({top_div['Avg_Margin']:.1f}% avg margin).")
        if len(imbalanced) > 0:
            names = ", ".join(imbalanced['Division'].tolist())
            st.warning(f"⚖️ **{names}** — revenue share exceeds profit share by 5%+, indicating margin inefficiency.")

with tab3:
    st.subheader("Cost vs Margin Diagnostics")
    fig3 = px.scatter(
        filtered_df, x='Cost', y='Gross Margin %', color='Division',
        hover_data=['Product Name'], title="Cost vs Margin — Risk Flags",
        color_discrete_map=DIVISION_COLORS,
        labels={"Cost": "Cost ($)", "Gross Margin %": "Gross Margin (%)"}
    )
    fig3.add_hline(y=filtered_df['Gross Margin %'].mean(), line_dash="dash", line_color="gray",
                    annotation_text="Avg Margin")
    st.plotly_chart(fig3, use_container_width=True)
    st.info("Points **below** the dashed line are margin-poor relative to average — candidates for repricing or cost review.")

with tab4:
    st.subheader("Profit & Revenue Concentration (Pareto)")

    pareto_profit = product_summary.sort_values('Total_Profit', ascending=False).reset_index(drop=True)
    pareto_profit['Cumulative_%'] = (pareto_profit['Total_Profit'].cumsum() / pareto_profit['Total_Profit'].sum()) * 100
    pareto_profit['Metric'] = 'Profit'

    pareto_rev = product_summary.sort_values('Total_Sales', ascending=False).reset_index(drop=True)
    pareto_rev['Cumulative_%'] = (pareto_rev['Total_Sales'].cumsum() / pareto_rev['Total_Sales'].sum()) * 100
    pareto_rev['Metric'] = 'Revenue'

    import pandas as pd
    pareto_combined = pd.concat([
        pareto_profit[['Product Name', 'Cumulative_%', 'Metric']].reset_index().rename(columns={'index': 'Rank'}),
        pareto_rev[['Product Name', 'Cumulative_%', 'Metric']].reset_index().rename(columns={'index': 'Rank'})
    ])
    pareto_combined['Rank'] += 1

    fig4 = px.line(
        pareto_combined, x='Rank', y='Cumulative_%', color='Metric', markers=True,
        title="Cumulative Contribution: Profit vs Revenue",
        labels={"Cumulative_%": "Cumulative %", "Rank": "Number of Products (ranked)"},
        color_discrete_map={"Profit": "#7B3F00", "Revenue": "#A8DADC"}
    )
    fig4.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% Threshold")
    st.plotly_chart(fig4, use_container_width=True)

    top_n_profit = (pareto_profit['Cumulative_%'] <= 80).sum() + 1
    top_n_rev = (pareto_rev['Cumulative_%'] <= 80).sum() + 1
    st.warning(f"⚠️ Just **{top_n_profit} of {len(pareto_profit)} products** generate 80%+ of total profit, and **{top_n_rev} products** generate 80%+ of total revenue — the same core group drives both.")

with tab5:
    st.subheader("Factory-Level Profitability")
    factory_summary = filtered_df.groupby('Factory').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Products=('Product Name', 'nunique')
    ).reset_index()

    if len(factory_summary) > 0:
        factory_summary['Margin_%'] = (factory_summary['Total_Profit'] / factory_summary['Total_Sales']) * 100
        factory_summary = factory_summary.sort_values('Margin_%', ascending=False)

        fig5 = px.bar(
            factory_summary, x='Factory', y='Margin_%',
            title="Gross Margin by Factory",
            labels={"Margin_%": "Gross Margin (%)", "Factory": ""},
            color='Margin_%', color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.dataframe(
            factory_summary.rename(columns={
                "Total_Sales": "Total Sales ($)", "Total_Profit": "Total Profit ($)",
                "Margin_%": "Margin (%)", "Products": "No. of Products"
            }),
            use_container_width=True, hide_index=True
        )

        best = factory_summary.iloc[0]
        worst = factory_summary.iloc[-1]
        st.success(f"🏆 **{best['Factory']}** has the highest margin at **{best['Margin_%']:.1f}%**.")
        if worst['Margin_%'] < filtered_df['Gross Profit'].sum() / filtered_df['Sales'].sum() * 100 - 10:
            st.warning(f"⚠️ **{worst['Factory']}** has a margin of only **{worst['Margin_%']:.1f}%** — well below the company average. Review its product costs for renegotiation.")