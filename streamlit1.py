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

    with tab1:
        st.header("Технічні показники")

        # Обчислення середніх значень для uptime
        avg_uptime = technical_df['uptime'].mean()

        # Відображення середніх показників зверху
        st.metric("Середній Uptime", f"{avg_uptime:.2f}%")

        st.subheader("Таблиця технічних показників")
        st.dataframe(technical_df)

        # Графік швидкості
        st.subheader("Графік швидкості передачі даних")
        fig_speed = px.line(technical_df, x='timestamp', y=['download_speed', 'upload_speed'],
                            title='Швидкість передачі даних', labels={'value': 'Швидкість (Mbps)', 'timestamp': 'Час'})
        st.plotly_chart(fig_speed, use_container_width=True)

        # Графік якості з'єднання
        st.subheader("Графік якості з\'єднання")
        fig_quality = px.line(technical_df, x='timestamp', y=['packet_loss', 'latency', 'jitter'],
                              title="Показники якості з'єднання", 
                              labels={'value': 'Показники (мс або %)', 'timestamp': 'Час'})
        st.plotly_chart(fig_quality, use_container_width=True)

    with tab2:
        st.header("Бізнес показники")

        # Обчислення середніх значень для ARPU і Churn Rate
        avg_arpu = business_df['arpu'].mean()
        avg_churn = business_df['churn_rate'].mean()

        # Відображення середніх показників зверху
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Середній ARPU", f"₴{avg_arpu:.2f}")
        with col2:
            st.metric("Середній Churn Rate", f"{avg_churn:.2f}%")

        st.subheader("Таблиця бізнес-показників")
        st.dataframe(business_df)

        # Графік ARPU і Churn Rate
        st.subheader("Графік ARPU і Churn Rate")
        fig_business = px.line(business_df, x='date', y=['arpu', 'churn_rate'],
                               title='Динаміка ARPU і Churn Rate', 
                               labels={'value': 'Показники', 'date': 'Дата'})
        st.plotly_chart(fig_business, use_container_width=True)

    with tab3:
        st.header("Операційні показники")

        # Обчислення середніх значень для часу вирішення і нових підключень
        avg_resolution_time = operational_df['avg_resolution_time'].mean()
        avg_new_connections = operational_df['new_connections'].mean()

        # Відображення середніх показників зверху
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Середній час вирішення (год)", f"{avg_resolution_time:.2f}")
        with col2:
            st.metric("Середні нові підключення", f"{avg_new_connections:.0f}")

        st.subheader("Таблиця операційних показників")
        st.dataframe(operational_df)

        # Графік кількості звернень і часу вирішення
        st.subheader("Графік звернень та часу вирішення")
        fig_support = go.Figure()
        fig_support.add_trace(go.Bar(x=operational_df['date'], y=operational_df['support_tickets'], name='Кількість звернень'))
        fig_support.add_trace(go.Scatter(x=operational_df['date'], y=operational_df['avg_resolution_time'], mode='lines+markers',
                                         name='Час вирішення (год)', yaxis='y2'))
        fig_support.update_layout(
            title='Звернення та час вирішення',
            yaxis=dict(title='Кількість звернень'),
            yaxis2=dict(title='Час вирішення (год)', overlaying='y', side='right'),
            xaxis=dict(title='Дата'),
        )
        st.plotly_chart(fig_support, use_container_width=True)

if __name__ == "__main__":
    main()
