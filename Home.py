import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.data_loader import load_data
from modules.calculations import calculate_price_changes
from modules.styling import configure_page_style, style_dataframe, display_market_metrics

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Commodity Dashboard",
    page_icon="💹",
    layout="wide"
)

# --- APPLY CUSTOM STYLES ---
configure_page_style()


# --- HEADER ---
st.markdown("""
    <h1 style='
        color: #FFFFFF; 
        font-size: 2.5rem; 
        font-weight: 700;
        text-align: left;
         '>
        💹 Commodity Market Dashboard
    </h1>
""", unsafe_allow_html=True)


# --- DATA LOADING (with caching) ---
df_data, df_list = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")

if df_data is not None and df_list is not None:
    # Date Selector
    min_date = df_data['Date'].min()
    max_date = df_data['Date'].max()
    selected_date = st.sidebar.date_input(
        "Select Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

    # Sector Filter
    unique_sectors = sorted(df_list['Sector'].astype(str).unique())
    selected_sectors = st.sidebar.multiselect(
        "Filter by Sector",
        options=unique_sectors,
        default=[]
    )

    # Commodity Filter
    if selected_sectors:
        commodity_options = sorted(df_list[df_list['Sector'].isin(selected_sectors)]['Commodities'].astype(str).unique())
    else:
        commodity_options = sorted(df_list['Commodities'].astype(str).unique())
    
    selected_commodities = st.sidebar.multiselect(
        "Filter by Commodity",
        options=commodity_options,
        default=[]
    )
    
    # --- DATA CALCULATION ---
    analysis_df = calculate_price_changes(df_data, df_list, selected_date)

    # --- MAIN CONTENT ---
    

    if not analysis_df.empty:
        # --- Filter Data based on selection ---
        filtered_df = analysis_df.copy()
        
        if selected_sectors:
            filtered_df = filtered_df[filtered_df['Sector'].isin(selected_sectors)]
            
        if selected_commodities:
            filtered_df = filtered_df[filtered_df['Commodities'].isin(selected_commodities)]

        # --- Display Key Market Metrics ---
       
        display_market_metrics(filtered_df)
        

        # --- Display Data Table ---
        
        st.markdown("""
         <h2 style='
        color: #FFFFFF; 
        font-size: 2rem; 
        font-weight: 400;
        text-align: left;
         '>
        Detailed Price Table
          </h2>
        """, unsafe_allow_html=True)
        
        if not filtered_df.empty:
            display_table = filtered_df.copy()
            # Hàm style_dataframe giờ đã bao gồm cả việc ẩn index và set width 100%
            styled_df_object = style_dataframe(display_table)
            
            # Tạo bảng HTML
            html_table = styled_df_object.to_html()

            # Bọc bảng HTML vào một div có chiều cao cố định và thanh cuộn
            scrollable_container = f"""
            <div style="height: 500px; overflow-y: auto; width: 100%;">
                {html_table}
            </div>
            """
        else:
            st.warning("No data matches your filter criteria.")
        st.markdown(scrollable_container, unsafe_allow_html=True)

        # --- DYNAMIC BAR CHART SECTION (using Plotly) ---
        st.markdown("""
         <h3 style='
        color: #FFFFFF; 
        font-size: 2rem; 
        font-weight: 400;
        text-align: left;
         '>
        Performance Chart & Impact
          </h3>
        """, unsafe_allow_html=True)
       

        if not filtered_df.empty:
            # Dropdown to select chart type
            chart_options = {
                "Weekly Performance": "%Week",
                "Daily Performance": "%Day",
                "Monthly Performance": "%Month",
                "Quarterly Performance": "%Quarter",
                "YTD Performance": "%YTD"
            }
            selected_chart_label = st.selectbox(
                "Select Chart to Display",
                options=list(chart_options.keys())
            )
            
            selected_column = chart_options[selected_chart_label]

            if selected_column in filtered_df.columns:
                chart_data = filtered_df[['Commodities', selected_column, 'Impact']].copy()
                chart_data.dropna(subset=[selected_column], inplace=True)
                
                # Filter out commodities with 0% change
                chart_data = chart_data[chart_data[selected_column] != 0]
                
                if not chart_data.empty:
                    # Sort DESCENDING to have positive values first
                    chart_data = chart_data.sort_values(by=selected_column, ascending=False)
                    
                    # --- Create a single figure with two subplots (columns) ---
                    fig = make_subplots(
                        rows=1, cols=2,
                        shared_yaxes=True,
                        column_widths=[0.8, 0.2],
                        horizontal_spacing=0.04
                    )

                    # --- Trace 1: Performance Bars ---
                    # KEY CHANGE: Apply new color scheme
                    colors = ['#10b981' if val > 0 else '#e11d48' for val in chart_data[selected_column]]
                    fig.add_trace(go.Bar(
                        y=chart_data['Commodities'],
                        x=chart_data[selected_column],
                        orientation='h',
                        marker_color=colors,
                        text=chart_data[selected_column].apply(lambda x: f'{x:.1%}'),
                        textposition='outside',
                        hoverinfo='none',
                        showlegend=False
                    ), row=1, col=1)

                    # --- Trace 2: Impact Text ---
                    fig.add_trace(go.Scatter(
                        y=chart_data['Commodities'],
                        x=[-5] * len(chart_data),
                        mode='text',
                        text=chart_data['Impact'].fillna(''),
                        textposition="middle left",
                        textfont=dict(size=11, color='#333'),
                        hoverinfo='none',
                        showlegend=False
                    ), row=1, col=2)
                    
                    # --- General Layout Updates ---
                    chart_height = max(200, len(chart_data) * 20)
                    fig.update_layout(
                        template="plotly_white",
                        height=chart_height,
                        margin=dict(l=20, r=20, t=50, b=20),
                        font=dict(family="Manrope, sans-serif"),
                        # --- Main Title ---
                        title=dict(
                            text=f"<b>{selected_chart_label}</b>",
                            x=0.35,
                            xanchor='center',
                            y=0.98
                        )
                    )

                    # --- Axis Updates ---
                    fig.update_yaxes(autorange="reversed", showticklabels=True, row=1, col=1)
                    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=1, col=2)
                    fig.update_xaxes(title_text="Change", tickformat=".0%", row=1, col=1)
                    fig.update_xaxes(visible=False, showgrid=False, zeroline=False, row=1, col=2)

                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.info(f"No data available for '{selected_chart_label}' with the selected filters (after removing 0% changes).")
            else:
                 st.warning(f"Could not generate chart. The required data column '{selected_column}' is missing.")
        else:
            st.warning("No data to display in the chart with the current filters.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("Failed to load data files. Please check the 'data' directory.")


