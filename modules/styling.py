import streamlit as st
import pandas as pd
import base64
import os

def get_base64_of_bin_file(bin_file):
    """
    Encodes a binary file to a base64 string.
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def configure_page_style():
    """
    Applies custom CSS for the page, including a background image for the app and sidebar.
    """
    # Path should point to your .png file. Please ensure it is named DC.png
    img_path = os.path.join("assets", "DC.png")

    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        
        page_bg_img = f"""
        <style>
        
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700&display=swap');

        /* Define color palette */
        :root {{
            --primary-teal: #00816D;
            --secondary-red: #e11d48;
            --accent-green: #10b981;
        }}

        /* Apply font and base styles */
        html, body, .st-emotion-cache-10trblm {{
            font-family: 'Manrope', sans-serif;
        }}
        /* --- Sidebar Navigation Links --- */

            /* Định dạng màu chữ cho các link trong sidebar */
        [data-testid="stSidebarNav"] a span {{
            color: #FFFFFF ;
        }}

        /* Định dạng màu chữ cho link của trang ĐANG được chọn (để dễ đọc trên nền sáng) */
        [data-testid="stSidebarNav"] a[aria-current="page"] span {{
            color: #FFFFFF ; /* Dùng màu xanh teal chủ đạo của bạn */
        }}
        /* Main App Background */
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Sidebar Styling - Solid color background */
        [data-testid="stSidebar"] > div:first-child {{
            background-color: var(--primary-teal);
        }}
        
        /* Make text elements in the sidebar white, EXCEPT for the page navigation links */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .st-emotion-cache-16txtl3,
        [data-testid="stSidebar"] .st-emotion-cache-10trblm {{
            color: #FFFFFF;
        }}
        [data-testid="stSidebar"] .st-emotion-cache-1g8p9hb {{
             color: #E0E0E0;
        }}
        
        /* KEY FIX: Hide the text on the main sidebar collapse button at the bottom */
        [data-testid="stSidebarCollapseButton"] p {{
            display: none;
        }}

        /* Main Content Styling - Fully transparent */
        .block-container {{
            background-color: transparent;
            padding: 2rem 3rem;
        }}
        
        /* Header styles with text shadow for readability */
        h1, h2, h3 {{
            color: #FFFFFF;
            font-weight: 700;
           
        }}
        .st-emotion-cache-10trblm, .st-emotion-cache-16txtl3 {{
            color: var(--primary-teal);
            text-shadow: 0px 1px 3px rgba(255, 255, 255, 0.7);
        }}
       
                
        /* Wrapper styles to create the "card" effect */
        .metric-container-wrapper, .chart-wrapper {{
            background-color: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            margin-bottom: 2rem;
        }}
        
        
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    else:
        st.warning("Background image not found. Please ensure 'assets/DC.png' exists.")

def display_market_metrics(df: pd.DataFrame):
    """
    Displays the Key Market Metrics with a new, cleaner style.
    """
    if df.empty:
        st.info("No data available to display Key Market Metrics for the selected filters.")
        return

    css_style = """
    <style>
        .metric-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }
        .metric-card {
            background-color: #FFFFFF; /* Solid white background for KPIs */
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 120px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-top: 5px solid;
            color: #333;
        }
        
        .metric-card .commodity-name {
            font-size: 20px;
            font-weight: 700;
            margin: auto 0;
            line-height: 1.2;
        }
        .metric-card .value {
            font-size: 18px;
            font-weight: 700;
        }
        .bullish-card .title { color: var(--accent-green); }
        .bullish-card { border-color: var(--accent-green); }
        .bullish-card .value { color: var(--accent-green); }
        .bearish-card .title { color: var(--secondary-red); }
        .bearish-card { border-color: var(--secondary-red); }
        .bearish-card .value { color: var(--secondary-red); }

        .avg-card .title { color: #ea580c; }
        .avg-card { border-color: #ea580c; }
        .avg-card .value { color: #ea580c; }

        .leader-card .title { color: #7c3aed; }
        .leader-card { border-color: #7c3aed; }
        .leader-card .value { color: #7c3aed; }
    </style>
    """
    
    st.markdown("""
    <h2 style='
        color: #FFFFFF; 
        font-size: 2.0rem; 
        font-weight: 500;
        text-align: left;
    '>
        Key Market Metrics
    </h2>
""", unsafe_allow_html=True)
    
    # Calculations
    most_bullish = df.loc[df['%Week'].idxmax()] if not df['%Week'].empty and df['%Week'].notna().any() else None
    most_bearish = df.loc[df['%Week'].idxmin()] if not df['%Week'].empty and df['%Week'].notna().any() else None
    avg_weekly_change = df['%Week'].mean() if not df['%Week'].empty else 0
    monthly_leader = df.loc[df['%Month'].idxmax()] if not df['%Month'].empty and df['%Month'].notna().any() else None

    # HTML Content
    html_content = f"""
    <div class="metric-container">
        <div class="metric-card bullish-card">
            <div class="title">↑ Most Bullish (Weekly)</div>
            <div class="commodity-name">{most_bullish['Commodities'] if most_bullish is not None else 'N/A'}</div>
            <div class="value">{f"{most_bullish['%Week']:.1%}" if most_bullish is not None and pd.notna(most_bullish['%Week']) else 'N/A'}</div>
        </div>
        <div class="metric-card bearish-card">
            <div class="title">↓ Most Bearish (Weekly)</div>
            <div class="commodity-name">{most_bearish['Commodities'] if most_bearish is not None else 'N/A'}</div>
            <div class="value">{f"{most_bearish['%Week']:.1%}" if most_bearish is not None and pd.notna(most_bearish['%Week']) else 'N/A'}</div>
        </div>
        <div class="metric-card avg-card">
            <div class="title">Avg. Weekly Change</div>
            <div class="commodity-name" style="font-size: 28px;">{f"{avg_weekly_change:.1%}" if pd.notna(avg_weekly_change) else 'N/A'}</div>
            <div class="value">All Selected</div>
        </div>
        <div class="metric-card leader-card">
            <div class="title">🏆 Monthly Leader</div>
            <div class="commodity-name">{monthly_leader['Commodities'] if monthly_leader is not None else 'N/A'}</div>
            <div class="value">{f"{monthly_leader['%Month']:.1%}" if monthly_leader is not None and pd.notna(monthly_leader['%Month']) else 'N/A'}</div>
        </div>
    </div>
    """
    
    st.markdown(css_style + html_content, unsafe_allow_html=True)

def style_dataframe(df: pd.DataFrame):
    df_to_style = df.copy()

    # Định dạng hiển thị (giữ nguyên)
    format_dict = {
        'Current Price': '{:,.0f}',
        '30D Avg': '{:,.0f}',
        '52W High': '{:,.0f}',
        '52W Low': '{:,.0f}',
        '%Day': '{:.1%}',
        '%Week': '{:.1%}',
        '%Month': '{:.1%}',
        '%Quarter': '{:.1%}',
        '%YTD': '{:.1%}',
    }
    percent_cols = ['%Day', '%Week', '%Month', '%Quarter', '%YTD']

    # Hàm style (giữ nguyên)
    def style_percent_cell(val):
        if pd.isna(val):
            return 'font-weight: 300;'
        
        if val > 0:
            bg_intensity = min(abs(val) * 10, 1.5)
            return f'background-color: rgba(16, 185, 129, {bg_intensity}); font-weight: 300;'
        elif val < 0:
            bg_intensity = min(abs(val) * 10, 1.5)
            return f'background-color: rgba(225, 29, 72, {bg_intensity}); font-weight: 300;'
        else:
            return 'background-color: #FFFFFF; font-weight: 300;'

    styler = df_to_style.style.format(format_dict, na_rep='—')
    
    for col in percent_cols:
        if col in df_to_style.columns:
            styler = styler.applymap(style_percent_cell, subset=[col])
    
    text_columns = ['Commodities', 'Sector', 'Nation', 'Change type', 'Impact']
    
    table_styles = [
        {
            'selector': '',
            'props': [
                ('font-family', 'Manrope, sans-serif'),
                ('color', '#000000'),
                ('font-size', '12px'),
            ]
        },
        # ĐÃ XÓA selector 'table' khỏi đây
        {
            'selector': 'td',
            'props': [
                ('padding', '8px'),
                ('border-bottom', '1px solid #f0f0f0'),
                ('font-weight', '400'),
                ('text-align', 'right'),
            ]
        },
        {
            'selector': 'th',
            'props': [
                # 1. Các dòng mới để cố định header
                ('position', 'sticky'),
                ('top', '0'),
                ('z-index', '1'), # Đảm bảo header luôn nằm trên các dòng khác
                
                # 2. Các style cũ (giữ nguyên và rất quan trọng)
                ('font-weight', '600'),
                ('padding', '10px'),
                ('background-color', '#00816D'), # Màu nền là bắt buộc cho sticky header
                ('color', '#f5f5f5'),
                ('text-align', 'left'),
            ]
        },
        {
            'selector': 'tr:hover',
            'props': [('background-color', '#f5f5f5')]
        }
    ]

    for i, col_name in enumerate(df_to_style.columns):
        if col_name in text_columns:
            table_styles.append({
                'selector': f'td:nth-child({i + 1})',
                'props': [('text-align', 'left')]
            })

    styler = styler.set_table_styles(table_styles)

    # --- THAY ĐỔI QUAN TRỌNG NHẤT TẠI ĐÂY ---
    # Gắn style trực tiếp vào thẻ <table> để đảm bảo được áp dụng
    styler = styler.set_table_attributes('style="width:100%; background-color:white; border-collapse: collapse;"')
    
    styler = styler.hide(axis="index")
    
    return styler