import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from modules.data_loader import load_data
from modules.styling import configure_page_style

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Chart Analysis",
    page_icon="📈",
    layout="wide"
)

# --- APPLY CUSTOM STYLES ---
configure_page_style()

# --- HELPER FUNCTION ---
def create_price_chart(data, title, chart_type="Line Chart", show_ma=False, ma_periods=[]):
    """Create a price chart with optional moving averages"""
    
    fig = go.Figure()
    
    # Main price chart
    if chart_type == "Line Chart":
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Price'],
            mode='lines',
            name='Price',
            line=dict(color='#00816D', width=2)
        ))
    elif chart_type == "Area Chart":
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Price'],
            mode='lines',
            name='Price',
            fill='tozeroy',
            line=dict(color='#00816D', width=2),
            fillcolor='rgba(0, 129, 109, 0.1)'
        ))
    elif chart_type == "Column Chart":
        fig.add_trace(go.Bar(
            x=data['Date'],
            y=data['Price'],
            name='Price',
            marker=dict(
                color=data['Price'],
                colorscale='Teal',
                line=dict(color='#00816D', width=0.5)
            )
        ))
    
    # Add moving averages
    if show_ma and ma_periods:
        colors = ['#e11d48', '#fb923c', '#3b82f6', '#8b5cf6']
        for i, period in enumerate(ma_periods):
            if len(data) >= period:
                ma_values = data['Price'].rolling(window=period).mean()
                fig.add_trace(go.Scatter(
                    x=data['Date'],
                    y=ma_values,
                    mode='lines',
                    name=f'MA{period}',
                    line=dict(
                        color=colors[i % len(colors)],
                        width=1.5,
                        dash='dot'
                    )
                ))
    
    fig.update_layout(
        title=f"{title} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode='x unified',
        height=500,
        template="plotly_white",
        font=dict(family="Manrope, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig



# --- DATA LOADING ---
df_data, df_list = load_data()

if df_data is not None and df_list is not None:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Chart Filters")
    
    # Date Range Selector
    
    min_date = df_data['Date'].min()
    max_date = df_data['Date'].max()

    # Sử dụng st.columns để tạo 2 cột cho 2 ô chọn ngày
    col1, col2 = st.sidebar.columns(2)

    # Ô chọn ngày bắt đầu
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=max_date - timedelta(days=20), # Giá trị mặc định
            min_value=min_date,
            max_value=max_date,
            key="start_date"
        )

# Ô chọn ngày kết thúc
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date, # Giá trị mặc định
            min_value=min_date,
            max_value=max_date,
            key="end_date"
        )

    # (Cải tiến) Kiểm tra logic ngày tháng để tránh lỗi
    if start_date > end_date:
        st.sidebar.error("Lỗi: Ngày bắt đầu không được sau ngày kết thúc.")
        # Dừng ứng dụng lại nếu ngày không hợp lệ để tránh vẽ biểu đồ sai
        st.stop()
    
    # Sector Filter
    
    unique_sectors = sorted(df_list['Sector'].astype(str).unique())
    selected_sectors = st.sidebar.multiselect(
        "Select Sectors",
        options=unique_sectors,
        default=[]
    )
    
    # Commodity Filter based on selected sectors
    
    if selected_sectors:
        commodity_options = sorted(
            df_list[df_list['Sector'].isin(selected_sectors)]['Commodities'].astype(str).unique()
        )
    else:
        commodity_options = sorted(df_list['Commodities'].astype(str).unique())
    
    selected_commodities = st.sidebar.multiselect(
        "Select Commodities (max 10)",
        options=commodity_options,
        default=[],
        max_selections=10
    )
    
    # Chart Type Selector
    st.sidebar.subheader("📈 Chart Options")
    chart_type = st.sidebar.radio(
        "Chart Type",
        options=["Line Chart", "Area Chart", "Column Chart"],
        index=0
    )
    
    show_volume = st.sidebar.checkbox("Show Trading Volume", value=False)
    show_ma = st.sidebar.checkbox("Show Moving Averages", value=True)
    
    if show_ma:
        ma_periods = st.sidebar.multiselect(
            "Moving Average Periods",
            options=[10, 20, 50, 100, 200],
            default=[10, 20]
        )
    
    # --- FILTER DATA ---
    if selected_commodities:
        # Filter data based on selections
        filtered_data = df_data[
            (df_data['Commodities'].isin(selected_commodities)) &
            (df_data['Date'] >= pd.to_datetime(start_date)) &
            (df_data['Date'] <= pd.to_datetime(end_date))
        ].copy()
        
        if not filtered_data.empty:
            # --- CREATE TABS ---
            # --- CREATE STYLED TABS ---
            st.markdown("""
            <style>
                /* Style cho tab buttons */
                .stTabs [data-baseweb="tab-list"] {
                    gap: 8px;
                    background: linear-gradient(135deg, rgba(0,129,109,0.1) 0%, rgba(16,185,129,0.1) 100%);
                    padding: 10px;
                    border-radius: 10px;
                }
                
                /* Style cho từng tab */
                .stTabs [data-baseweb="tab"] {
                    height: 50px;
                    padding: 0 24px;
                    background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
                    border-radius: 8px;
                    border: 2px solid #00816D;
                    color: #00816D;
                    font-weight: 900;
                    font-size: 20px;
                    transition: all 0.3s ease;
                }
                
                /* Hover effect */
                .stTabs [data-baseweb="tab"]:hover {
                    background: linear-gradient(135deg, #00816D 0%, #10b981 100%);
                    color: white;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,129,109,0.3);
                }
                
                /* Active tab với gradient */
                .stTabs [aria-selected="true"] {
                    background: linear-gradient(135deg, #00816D 0%, #10b981 100%) !important;
                    color: white !important;
                    border: none !important;
                    box-shadow: 0 6px 20px rgba(0,129,109,0.4);
                    transform: scale(1.05);
                }
                
                /* Tab panel background */
                .stTabs [data-baseweb="tab-panel"] {
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }
                
                /* Tab highlight bar - ẩn đi */
                .stTabs [data-baseweb="tab-highlight"] {
                    display: none;
                }
                
                /* Tab border bottom - custom */
                .stTabs [data-baseweb="tab-list"] {
                    border-bottom: 2px solid #00816D;
                }
            </style>
            """, unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["📈 Price Charts", "📊 Comparison", "📉 Performance Analysis"])
            
            # --- TAB 1: INDIVIDUAL PRICE CHARTS ---
            with tab1:
                               
                # Create individual charts for each commodity
                num_commodities = len(selected_commodities)
                rows = (num_commodities + 1) // 2  # 2 columns layout
                
                if num_commodities == 1:
                    # Single large chart
                    commodity = selected_commodities[0]
                    commodity_data = filtered_data[filtered_data['Commodities'] == commodity].sort_values('Date')
                    
                    fig = create_price_chart(commodity_data, commodity, chart_type, show_ma, ma_periods if show_ma else [])
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    # Multiple charts in grid
                    fig = make_subplots(
                        rows=rows, cols=2,
                        subplot_titles=selected_commodities[:num_commodities],
                        vertical_spacing=0.1,
                        horizontal_spacing=0.05
                    )
                    
                    for idx, commodity in enumerate(selected_commodities):
                        row = idx // 2 + 1
                        col = idx % 2 + 1
                        
                        commodity_data = filtered_data[filtered_data['Commodities'] == commodity].sort_values('Date')
                        
                        # Add main price line
                        fig.add_trace(
                            go.Scatter(
                                x=commodity_data['Date'],
                                y=commodity_data['Price'],
                                mode='lines',
                                name=commodity,
                                line=dict(width=2,shape='spline', smoothing=0.2),
                                showlegend=False
                            ),
                            row=row, col=col
                        )
                        
                        # Add moving averages if selected
                        if show_ma and ma_periods:
                            for period in ma_periods:
                                if len(commodity_data) >= period:
                                    ma_values = commodity_data['Price'].rolling(window=period).mean()
                                    fig.add_trace(
                                        go.Scatter(
                                            x=commodity_data['Date'],
                                            y=ma_values,
                                            mode='lines',
                                            name=f'MA{period}',
                                            line=dict(width=1, dash='dot'),
                                            opacity=0.7,
                                            showlegend=False
                                        ),
                                        row=row, col=col
                                    )
                    
                    fig.update_layout(
                        height=300 * rows,
                        showlegend=False,
                        template="plotly_white",
                        font=dict(family="Manrope, sans-serif")
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # --- TAB 2: COMPARISON CHART ---
            with tab2:
                                
                # Normalize prices for comparison
                fig_compare = go.Figure()
                
                for commodity in selected_commodities:
                    commodity_data = filtered_data[filtered_data['Commodities'] == commodity].sort_values('Date')
                    
                    if not commodity_data.empty:
                       
                        first_price = commodity_data.iloc[0]['Price']
                        normalized_prices = (commodity_data['Price'] / first_price-1) * 100
                        
                        fig_compare.add_trace(
                            go.Scatter(
                                x=commodity_data['Date'],
                                y=normalized_prices,
                                mode='lines',
                                name=commodity,
                                line=dict(width=2, shape='spline', smoothing=0.2)
                            )
                        )
                
                fig_compare.update_layout(
                    
                    xaxis_title="Date",
                    yaxis_ticksuffix="%", 
                    hovermode='x unified',
                    height=500,
                    template="plotly_white",
                    font=dict(family="Manrope, sans-serif"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_compare, use_container_width=True)
                
                # Performance metrics
                st.markdown("""
                    <h3 style='color: #00816D; font-weight: 600; margin: 20px 0;'>
                        Performance Metrics
                    </h3>
                """, unsafe_allow_html=True)
                
                metrics_data = []
                for commodity in selected_commodities:
                    commodity_data = filtered_data[filtered_data['Commodities'] == commodity].sort_values('Date')
                    if len(commodity_data) > 1:
                        first_price = commodity_data.iloc[0]['Price']
                        last_price = commodity_data.iloc[-1]['Price']
                        change_pct = ((last_price - first_price) / first_price) * 100
                        
                        metrics_data.append({
                            'Commodity': commodity,
                            'Start Price': f"{first_price:,.0f}",
                            'End Price': f"{last_price:,.0f}",
                            'Change (%)': f"{change_pct:.1f}%",
                            'Min Price': f"{commodity_data['Price'].min():,.0f}",
                            'Max Price': f"{commodity_data['Price'].max():,.0f}",
                            'Volatility': f"{commodity_data['Price'].std():,.0f}"
                        })
                
                if metrics_data:
                    metrics_df = pd.DataFrame(metrics_data)
                    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            
            # --- TAB 3: PERFORMANCE ANALYSIS ---
            with tab3:
                # --- BƯỚC 1: ĐỊNH NGHĨA THANG MÀU CỦA BẠN ---
                my_colorscale = [
                    [0.0, '#e11d48'],     # Âm: màu đỏ của bạn
                    [0.5, '#f0f9ff'],    # Trung tính: màu trắng
                    [1.0, '#00816D']      # Dương: màu xanh của bạn
                ]
                
                # Heatmap of monthly returns
                if len(selected_commodities) > 1:
                                        
                    # Calculate monthly returns
                    monthly_returns = pd.DataFrame()
                    
                    for commodity in selected_commodities:
                        commodity_data = filtered_data[filtered_data['Commodities'] == commodity].sort_values('Date')
                        commodity_data.set_index('Date', inplace=True)
                        monthly_prices = commodity_data['Price'].resample('M').last()
                        monthly_pct = monthly_prices.pct_change() * 100
                        monthly_returns[commodity] = monthly_pct
                    
                    # Create heatmap
                    # 1. Sao chép dữ liệu để xử lý riêng cho việc hiển thị
                    display_returns = monthly_returns.T

                    # 2. Chuẩn bị phần text hiển thị: chuyển NaN thành chuỗi rỗng
                    text_values = display_returns.round(1).fillna('').astype(str)

                    # 3. Thay thế NaN bằng None trong dữ liệu z để Plotly hiểu là ô trống
                    z_values = display_returns.where(pd.notna(display_returns), None)

                    fig_heatmap = go.Figure(data=go.Heatmap(
                        z=z_values,
                        x=monthly_returns.index.strftime('%Y-%m'),
                        y=monthly_returns.columns,
                        colorscale='RdYlGn',
                        zmid=0,
                        # Sử dụng text_values đã được xử lý
                        text=text_values,
                        # Cập nhật texttemplate để không thêm dấu '%' cho ô trống
                        texttemplate="%{text}",
                        textfont={"size": 10},
                        colorbar=dict(title="Return (%)")
                    ))
                    
                    fig_heatmap.update_layout(
                        title="Monthly Returns Heatmap (%)",
                        xaxis_title="Month",
                        yaxis_title="Commodity",
                        height=400,
                        template="plotly_white",
                        font=dict(family="Manrope, sans-serif")
                    )
                    
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Correlation matrix
                if len(selected_commodities) > 1:
                                        
                    # Calculate correlation
                    corr_data = pd.DataFrame()
                    for commodity in selected_commodities:
                        commodity_data = filtered_data[filtered_data['Commodities'] == commodity].sort_values('Date')
                        corr_data[commodity] = commodity_data.set_index('Date')['Price']
                    
                    correlation_matrix = corr_data.corr()
                    text_values = correlation_matrix.round(2).fillna('').astype(str)
                    fig_corr = go.Figure(data=go.Heatmap(
                        z=correlation_matrix.values,
                        x=correlation_matrix.columns,
                        y=correlation_matrix.columns,
                        colorscale='RdYlGn',
                        zmid=0,
                        text=text_values,
                        texttemplate='%{text}',
                        colorbar=dict(title="Correlation")
                    ))
                    
                    fig_corr.update_layout(
                        title="Price Correlation Matrix",
                        height=400,
                        template="plotly_white",
                        font=dict(family="Manrope, sans-serif")
                    )
                    
                    st.plotly_chart(fig_corr, use_container_width=True)
        
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.info("Please select at least one commodity to display charts.")
        
else:
    st.error("Failed to load data files. Please check the 'data' directory.")

