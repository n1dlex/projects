
!pip install plotly psycopg2

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
from datetime import datetime, timedelta
import numpy as np

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

    # Отримання технічних КРІ
    technical_df = pd.read_sql("""
        SELECT timestamp, download_speed, upload_speed, packet_loss, latency, jitter, uptime
        FROM technical_kpi
        ORDER BY timestamp DESC
        LIMIT 24
    """, conn)

    # Отримання бізнес КРІ
    business_df = pd.read_sql("""
        SELECT date, arpu, churn_rate, nps, utilization_rate, cost_per_mb
        FROM business_kpi
        ORDER BY date DESC
        LIMIT 30
    """, conn)

    # Отримання операційних КРІ
    operational_df = pd.read_sql("""
        SELECT date, avg_resolution_time, support_tickets, fcr_rate, new_connections, capacity_utilization
        FROM operational_kpi
        ORDER BY date DESC
        LIMIT 30
    """, conn)

    conn.close()
    return technical_df, business_df, operational_df

def main():
    st.title('Дашборд КРІ широкосмугового доступу до інтернету')

    try:
        technical_df, business_df, operational_df = get_data()
    except Exception as e:
        st.warning("Використовуються тестові дані, оскільки немає з'єднання з базою даних")
        technical_df, business_df, operational_df = generate_test_data()

    # Вкладки для різних категорій КРІ
    tab1, tab2, tab3 = st.tabs(["Технічні КРІ", "Бізнес КРІ", "Операційні КРІ"])

    with tab1:
        st.header("Технічні показники")

        # Графік швидкості
        fig_speed = px.line(technical_df, x='timestamp', y=['download_speed', 'upload_speed'],
                           title='Швидкість передачі даних')
        st.plotly_chart(fig_speed)

        # Графік якості з'єднання
        fig_quality = px.line(technical_df, x='timestamp', y=['packet_loss', 'latency', 'jitter'],
                             title='Показники якості з\'єднання')
        st.plotly_chart(fig_quality)

        # Метрика аптайму
        latest_uptime = technical_df['uptime'].iloc[0]
        st.metric("Поточний Uptime", f"{latest_uptime:.2f}%")

    with tab2:
        st.header("Бізнес показники")

        col1, col2, col3 = st.columns(3)
        with col1:
            latest_arpu = business_df['arpu'].iloc[0]
            st.metric("ARPU", f"₴{latest_arpu:.2f}")
        with col2:
            latest_churn = business_df['churn_rate'].iloc[0]
            st.metric("Churn Rate", f"{latest_churn:.2f}%")
        with col3:
            latest_nps = business_df['nps'].iloc[0]
            st.metric("NPS", latest_nps)

        # Графік ARPU і Churn Rate
        fig_business = px.line(business_df, x='date', y=['arpu', 'churn_rate'],
                              title='ARPU і Churn Rate')
        st.plotly_chart(fig_business)

    with tab3:
        st.header("Операційні показники")

        # Графік кількості звернень і часу вирішення
        fig_support = go.Figure()
        fig_support.add_trace(go.Bar(x=operational_df['date'], y=operational_df['support_tickets'],
                                    name='Кількість звернень'))
        fig_support.add_trace(go.Line(x=operational_df['date'], y=operational_df['avg_resolution_time'],
                                     name='Час вирішення (год)', yaxis='y2'))
        fig_support.update_layout(
            title='Показники підтримки',
            yaxis2=dict(overlaying='y', side='right')
        )
        st.plotly_chart(fig_support)

        # Метрики операційної ефективності
        col1, col2 = st.columns(2)
        with col1:
            latest_fcr = operational_df['fcr_rate'].iloc[0]
            st.metric("First Call Resolution Rate", f"{latest_fcr:.2f}%")
        with col2:
            latest_connections = operational_df['new_connections'].iloc[0]
            st.metric("Нові підключення (за день)", latest_connections)

if __name__ == "__main__":
    main()
