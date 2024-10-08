# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2

# Функція для створення з'єднання з базою даних
def get_connection():
    return psycopg2.connect(
        host='test.cjyyo648mw6r.eu-north-1.rds.amazonaws.com',
        database='test',
        user='postgres',
        password='11111111'
    )

# Функція для отримання даних з бази
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

        return technical_df, business_df, operational_df

    finally:
        conn.close()

def main():
    st.set_page_config(page_title="КРІ Дашборд", layout="wide")
    st.title('Дашборд КРІ широкосмугового доступу до інтернету')

    try:
        technical_df, business_df, operational_df = get_data()
    except psycopg2.OperationalError as e:
        st.error(f"Помилка з'єднання з базою даних: {str(e)}")
        return

    # Rest of the code remains the same...
    
    tab1, tab2, tab3 = st.tabs(["Технічні КРІ", "Бізнес КРІ", "Операційні КРІ"])

    # Технічні показники
    with tab1:
        st.header("Технічні показники")

        # Метрики залишаються без змін
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Середня швидкість завантаження", f"{technical_df['download_speed'].mean():.2f} Mbps")
            st.metric("Середня затримка (Latency)", f"{technical_df['latency'].mean():.2f} ms")
        with col2:
            st.metric("Середня швидкість відвантаження", f"{technical_df['upload_speed'].mean():.2f} Mbps")
            st.metric("Середній Jitter", f"{technical_df['jitter'].mean():.2f} ms")
        with col3:
            st.metric("Середній Packet Loss", f"{technical_df['packet_loss'].mean():.2f}%")
            st.metric("Середній Uptime", f"{technical_df['uptime'].mean():.2f}%")

        st.subheader("Таблиця технічних показників")
        st.dataframe(technical_df)

        # Оновлені графіки для технічних КРІ
        st.subheader("Графіки технічних показників")
        
        # Створюємо графік з двома у-осями для всіх технічних метрик
        fig_technical = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Додаємо швидкості на основну вісь
        fig_technical.add_trace(
            go.Scatter(x=technical_df['timestamp'], y=technical_df['download_speed'], name="Швидкість завантаження", line=dict(color="blue")),
            secondary_y=False
        )
        fig_technical.add_trace(
            go.Scatter(x=technical_df['timestamp'], y=technical_df['upload_speed'], name="Швидкість відвантаження", line=dict(color="green")),
            secondary_y=False
        )
        
        # Додаємо інші метрики на додаткову вісь
        for column, color in zip(['latency', 'jitter', 'packet_loss', 'uptime'], ['red', 'orange', 'purple', 'brown']):
            fig_technical.add_trace(
                go.Scatter(x=technical_df['timestamp'], y=technical_df[column], name=column.title(), line=dict(color=color)),
                secondary_y=True
            )
        
        fig_technical.update_layout(
            title="Всі технічні показники",
            xaxis_title="Час",
            height=600
        )
        fig_technical.update_yaxes(title_text="Швидкість (Mbps)", secondary_y=False)
        fig_technical.update_yaxes(title_text="Інші показники", secondary_y=True)
        
        st.plotly_chart(fig_technical, use_container_width=True)

    # The rest of the code (business and operational tabs) remains the same...

if __name__ == "__main__":
    main()
