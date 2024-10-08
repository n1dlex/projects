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

        # Відображення значень та середніх значень технічних метрик
        st.subheader("Технічні метрики")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Швидкість завантаження", f"{technical_df['download_speed'].iloc[0]:.2f} Mbps")
            st.metric("Середня швидкість завантаження", f"{technical_df['download_speed'].mean():.2f} Mbps")
        with col2:
            st.metric("Швидкість відвантаження", f"{technical_df['upload_speed'].iloc[0]:.2f} Mbps")
            st.metric("Середня швидкість відвантаження", f"{technical_df['upload_speed'].mean():.2f} Mbps")
        with col3:
            st.metric("Uptime", f"{technical_df['uptime'].iloc[0]:.2f}%")
            st.metric("Середній Uptime", f"{technical_df['uptime'].mean():.2f}%")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Packet Loss", f"{technical_df['packet_loss'].iloc[0]:.2f}%")
            st.metric("Середній Packet Loss", f"{technical_df['packet_loss'].mean():.2f}%")
        with col2:
            st.metric("Latency", f"{technical_df['latency'].iloc[0]:.2f} ms")
            st.metric("Середня затримка", f"{technical_df['latency'].mean():.2f} ms")
        with col3:
            st.metric("Jitter", f"{technical_df['jitter'].iloc[0]:.2f} ms")
            st.metric("Середній Jitter", f"{technical_df['jitter'].mean():.2f} ms")

        st.subheader("Таблиця технічних показників")
        st.dataframe(technical_df)

        # Графік швидкості передачі даних
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

    # Бізнес показники
    with tab2:
        st.header("Бізнес показники")

        # Відображення значень та середніх значень бізнесових метрик
        st.subheader("Бізнес метрики")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("ARPU", f"₴{business_df['arpu'].iloc[0]:.2f}")
            st.metric("Середній ARPU", f"₴{business_df['arpu'].mean():.2f}")
        with col2:
            st.metric("Churn Rate", f"{business_df['churn_rate'].iloc[0]:.2f}%")
            st.metric("Середній Churn Rate", f"{business_df['churn_rate'].mean():.2f}%")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("NPS", f"{business_df['nps'].iloc[0]:.2f}")
            st.metric("Середній NPS", f"{business_df['nps'].mean():.2f}")
        with col2:
            st.metric("Utilization Rate", f"{business_df['utilization_rate'].iloc[0]:.2f}%")
            st.metric("Середній Utilization Rate", f"{business_df['utilization_rate'].mean():.2f}%")

        st.subheader("Таблиця бізнес показників")
        st.dataframe(business_df)

        # Графік ARPU і Churn Rate
        st.subheader("Графік ARPU і Churn Rate")
        fig_business = px.line(business_df, x='date', y=['arpu', 'churn_rate'],
                               title='Динаміка ARPU і Churn Rate', 
                               labels={'value': 'Показники', 'date': 'Дата'})
        st.plotly_chart(fig_business, use_container_width=True)

    # Операційні показники
    with tab3:
        st.header("Операційні показники")

        # Відображення значень та середніх значень операційних метрик
        st.subheader("Операційні метрики")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Час вирішення (год)", f"{operational_df['avg_resolution_time'].iloc[0]:.2f}")
            st.metric("Середній час вирішення", f"{operational_df['avg_resolution_time'].mean():.2f}")
        with col2:
            st.metric("FCR Rate", f"{operational_df['fcr_rate'].iloc[0]:.2f}%")
            st.metric("Середній FCR Rate", f"{operational_df['fcr_rate'].mean():.2f}%")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Кількість звернень", f"{operational_df['support_tickets'].iloc[0]:.0f}")
            st.metric("Середня кількість звернень", f"{operational_df['support_tickets'].mean():.0f}")
        with col2:
            st.metric("Нові підключення", f"{operational_df['new_connections'].iloc[0]:.0f}")
            st.metric("Середні нові підключення", f"{operational_df['new_connections'].mean():.0f}")

        st.subheader("Таблиця операційних показників")
        st.dataframe(operational_df)

        # Графік звернень та часу вирішення
        st.subheader("Графік звернень та часу вирішення")
        fig_support = go.Figure()
        fig_support.add_trace(go.Bar(x=operational_df['date'], y=operational_df['support_tickets'], name='Кількість звернень'))
        fig_support.add_trace(go.Scatter(x=operational_df['date'], y=operational_df['avg_resolution_time'], mode='lines+markers',
                                         name='Час вирішення (год)'))
        fig_support.update_layout(title='Кількість звернень і час вирішення',
                                  xaxis_title='Дата', yaxis_title='Показники')
        st.plotly_chart(fig_support, use_container_width=True)

if __name__ == "__main__":
    main()
