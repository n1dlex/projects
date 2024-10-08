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

    # Відображення середніх значень всіх метрик
    st.header("Середні показники всіх метрик")

    col1, col2, col3 = st.columns(3)
    # Технічні показники
    with col1:
        st.subheader("Технічні показники")
        st.metric("Середня швидкість завантаження", f"{technical_df['download_speed'].mean():.2f} Mbps")
        st.metric("Середня швидкість відвантаження", f"{technical_df['upload_speed'].mean():.2f} Mbps")
        st.metric("Середній Uptime", f"{technical_df['uptime'].mean():.2f}%")
        st.metric("Середній packet loss", f"{technical_df['packet_loss'].mean():.2f}%")
        st.metric("Середня затримка (Latency)", f"{technical_df['latency'].mean():.2f} ms")
        st.metric("Середній Jitter", f"{technical_df['jitter'].mean():.2f} ms")

    # Бізнес показники
    with col2:
        st.subheader("Бізнес показники")
        st.metric("Середній ARPU", f"₴{business_df['arpu'].mean():.2f}")
        st.metric("Середній Churn Rate", f"{business_df['churn_rate'].mean():.2f}%")
        st.metric("Середній NPS", f"{business_df['nps'].mean():.2f}")
        st.metric("Середній Utilization Rate", f"{business_df['utilization_rate'].mean():.2f}%")
        st.metric("Середня вартість за MB", f"₴{business_df['cost_per_mb'].mean():.2f}")

    # Операційні показники
    with col3:
        st.subheader("Операційні показники")
        st.metric("Середній час вирішення (год)", f"{operational_df['avg_resolution_time'].mean():.2f}")
        st.metric("Середня кількість звернень", f"{operational_df['support_tickets'].mean():.0f}")
        st.metric("Середній First Call Resolution Rate", f"{operational_df['fcr_rate'].mean():.2f}%")
        st.metric("Середні нові підключення", f"{operational_df['new_connections'].mean():.0f}")
        st.metric("Середня завантаженість ємностей", f"{operational_df['capacity_utilization'].mean():.2f}%")

    st.markdown("---")  # Розділювальна лінія

    # Вкладки для різних категорій КРІ
    tab1, tab2, tab3 = st.tabs(["Технічні КРІ", "Бізнес КРІ", "Операційні КРІ"])

    with tab1:
        st.header("Технічні показники")
        st.subheader("Таблиця технічних показників")
        st.dataframe(technical_df)

        # Графік швидкості
        st.subheader("Графік швидкості передачі даних")
        fig_speed = px.line(technical_df, x='timestamp', y=['download_speed', 'upload_speed'],
                            title='Швидкість передачі даних', labels={'value': 'Швидкість (Mbps)', 'timestamp': 'Час'})
        st.plotly_chart(fig_speed, use_container_width=True)

        # Графік якості з\'єднання
        st.subheader("Графік якості з\'єднання")
        fig_quality = px.line(technical_df, x='timestamp', y=['packet_loss', 'latency', 'jitter'],
                              title="Показники якості з'єднання", 
                              labels={'value': 'Показники (мс або %)', 'timestamp': 'Час'})
        st.plotly_chart(fig_quality, use_container_width=True)

    with tab2:
        st.header("Бізнес показники")
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
        st.subheader("Таблиця операційних показників")
        st.dataframe(operational_df)

        # Графік звернень та часу вирішення
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
