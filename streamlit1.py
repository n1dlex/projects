# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

    finally:
        conn.close()

    return technical_df, business_df, operational_df

def main():
    st.set_page_config(page_title="КРІ Дашборд", layout="wide")
    st.title('Дашборд КРІ широкосмугового доступу до інтернету')

    try:
        technical_df, business_df, operational_df = get_data()
    except psycopg2.OperationalError as e:
        st.error(f"Помилка з'єднання з базою даних: {str(e)}")
        return

    # Вкладки для різних категорій КРІ
    tab1, tab2, tab3 = st.tabs(["Технічні КРІ", "Бізнес КРІ", "Операційні КРІ"])

    # Технічні показники
    with tab1:
        st.header("Технічні показники")

        # Відображення всіх середніх значень технічних метрик
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

        # Графіки залишаються без змін...

    # Бізнес показники
    with tab2:
        st.header("Бізнес показники")

        # Відображення всіх середніх значень бізнесових метрик
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Середній ARPU", f"₴{business_df['arpu'].mean():.2f}")
            st.metric("Середній NPS", f"{business_df['nps'].mean():.2f}")
        with col2:
            st.metric("Середній Churn Rate", f"{business_df['churn_rate'].mean():.2f}%")
            st.metric("Середня вартість за MB", f"₴{business_df['cost_per_mb'].mean():.4f}")
        with col3:
            st.metric("Середній Utilization Rate", f"{business_df['utilization_rate'].mean():.2f}%")

        st.subheader("Таблиця бізнес показників")
        st.dataframe(business_df)

        # Графіки залишаються без змін...

    # Операційні показники
    with tab3:
        st.header("Операційні показники")

        # Відображення всіх середніх значень операційних метрик
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Середній час вирішення (год)", f"{operational_df['avg_resolution_time'].mean():.2f}")
            st.metric("Середня кількість звернень", f"{operational_df['support_tickets'].mean():.0f}")
        with col2:
            st.metric("Середній FCR Rate", f"{operational_df['fcr_rate'].mean():.2f}%")
            st.metric("Середні нові підключення", f"{operational_df['new_connections'].mean():.0f}")
        with col3:
            st.metric("Середнє використання потужності", f"{operational_df['capacity_utilization'].mean():.2f}%")

        st.subheader("Таблиця операційних показників")
        st.dataframe(operational_df)

        # Графіки залишаються без змін...

if __name__ == "__main__":
    main()
