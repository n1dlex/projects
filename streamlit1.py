import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2

# Function to create a database connection
def get_connection():
    return psycopg2.connect(
        host='test.cjyyo648mw6r.eu-north-1.rds.amazonaws.com',
        database='test',
        user='postgres',
        password='11111111'
    )

# Function to fetch data from the database
def get_data():
    conn = get_connection()
    try:
        technical_df = pd.read_sql("""
            SELECT timestamp, download_speed, upload_speed, packet_loss, latency, jitter, uptime
            FROM technical_kpi
            ORDER BY timestamp DESC
            LIMIT 24
        """, conn)

        business_df = pd.read_sql("""
            SELECT date, arpu, churn_rate, nps, utilization_rate, cost_per_mb
            FROM business_kpi
            ORDER BY date DESC
            LIMIT 30
        """, conn)

        operational_df = pd.read_sql("""
            SELECT date, avg_resolution_time, support_tickets, fcr_rate, new_connections, capacity_utilization
            FROM operational_kpi
            ORDER BY date DESC
            LIMIT 30
        """, conn)

    finally:
        conn.close()

    return technical_df, business_df, operational_df

def format_metric(value, format_type):
    if format_type == 'speed':
        return f"{value:.1f} Mbps"
    elif format_type == 'percentage':
        return f"{value:.1f}%"
    elif format_type == 'time':
        return f"{value:.1f} мс"
    elif format_type == 'money':
        return f"₴{value:.2f}"
    else:
        return f"{value:.1f}"

def main():
    st.set_page_config(page_title="КРІ Дашборд", layout="wide")
    
    # Use CSS for improved appearance
    st.markdown("""
        <style>
        .metric-container {
            background-color: #f0f2f6;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .metric-title {
            font-size: 14px;
            color: #555;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #0e1117;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title('📊 Дашборд КРІ широкосмугового доступу до інтернету')

    try:
        technical_df, business_df, operational_df = get_data()
    except psycopg2.OperationalError as e:
        st.error(f"Помилка з'єднання з базою даних: {str(e)}")
        return

    # Display average values for technical KPIs
    st.markdown("### 📈 Середні значення технічних показників")
    for column in ['download_speed', 'upload_speed', 'packet_loss', 'latency', 'jitter', 'uptime']:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">{column.replace('_', ' ').title()}</div>
                <div class="metric-value">{format_metric(technical_df[column].mean(), 'speed' if 'speed' in column else 'percentage' if 'loss' in column or 'uptime' in column else 'time')}</div>
            </div>
        """, unsafe_allow_html=True)

    # Display average values for business KPIs
    st.markdown("### 📈 Середні значення бізнес-показників")
    for column in ['arpu', 'churn_rate', 'nps', 'utilization_rate', 'cost_per_mb']:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">{column.replace('_', ' ').title()}</div>
                <div class="metric-value">{format_metric(business_df[column].mean(), 'money' if 'arpu' in column or 'cost' in column else 'percentage')}</div>
            </div>
        """, unsafe_allow_html=True)

    # Display average values for operational KPIs
    st.markdown("### 📈 Середні значення операційних показників")
    for column in ['avg_resolution_time', 'support_tickets', 'fcr_rate', 'new_connections', 'capacity_utilization']:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">{column.replace('_', ' ').title()}</div>
                <div class="metric-value">{format_metric(operational_df[column].mean(), 'time' if 'resolution' in column else 'percentage' if 'rate' in column or 'utilization' in column else 'number')}</div>
            </div>
        """, unsafe_allow_html=True)

    # Tabs for different KPI categories
    tab1, tab2, tab3 = st.tabs(["📡 Технічні КРІ", "💼 Бізнес КРІ", "🔧 Операційні КРІ"])

    # Technical KPIs tab
    with tab1:
        st.markdown("## 📡 Технічні показники")
        st.dataframe(technical_df, use_container_width=True)

    # Business KPIs tab
    with tab2:
        st.markdown("## 💼 Бізнес показники")
        st.dataframe(business_df, use_container_width=True)

    # Operational KPIs tab
    with tab3:
        st.markdown("## 🔧 Операційні показники")
        st.dataframe(operational_df, use_container_width=True)

if __name__ == "__main__":
    main()
