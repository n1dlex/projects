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

# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2

# Функції get_connection() і get_data() залишаються без змін

def main():
    st.set_page_config(page_title="КРІ Дашборд", layout="wide")
    st.title('Дашборд КРІ широкосмугового доступу до інтернету')

    try:
        technical_df, business_df, operational_df = get_data()
    except psycopg2.OperationalError as e:
        st.error(f"Помилка з'єднання з базою даних: {str(e)}")
        return

    tab1, tab2, tab3 = st.tabs(["Технічні КРІ", "Бізнес КРІ", "Операційні КРІ"])

    # Технічні показники
    with tab1:
        st.header("Технічні показники")

        # Метрики у верхній частині
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

        # Таблиця даних
        st.subheader("Таблиця технічних показників")
        st.dataframe(technical_df)

        # Графік швидкостей
        st.subheader("Швидкість передачі даних")
        fig_speed = px.line(technical_df, x='timestamp', 
                           y=['download_speed', 'upload_speed'],
                           labels={'value': 'Швидкість (Mbps)', 'timestamp': 'Час',
                                  'variable': 'Тип швидкості'},
                           height=400)
        fig_speed.update_layout(yaxis_title="Швидкість (Mbps)")
        st.plotly_chart(fig_speed, use_container_width=True)

        # Графік затримки та джитера
        st.subheader("Затримка та джитер")
        fig_latency = go.Figure()
        fig_latency.add_trace(go.Scatter(x=technical_df['timestamp'], y=technical_df['latency'],
                                        name="Затримка", line=dict(color="red")))
        fig_latency.add_trace(go.Scatter(x=technical_df['timestamp'], y=technical_df['jitter'],
                                        name="Джитер", line=dict(color="orange")))
        fig_latency.update_layout(height=400, yaxis_title="Мілісекунди (ms)")
        st.plotly_chart(fig_latency, use_container_width=True)

        # Графік packet loss та uptime
        st.subheader("Packet Loss та Uptime")
        fig_quality = go.Figure()
        fig_quality.add_trace(go.Scatter(x=technical_df['timestamp'], y=technical_df['packet_loss'],
                                        name="Packet Loss", line=dict(color="purple")))
        fig_quality.add_trace(go.Scatter(x=technical_df['timestamp'], y=technical_df['uptime'],
                                        name="Uptime", line=dict(color="green")))
        fig_quality.update_layout(height=400, yaxis_title="Відсотки (%)")
        st.plotly_chart(fig_quality, use_container_width=True)

    # Бізнес показники
    with tab2:
        st.header("Бізнес показники")

        # Метрики у верхній частині
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Середній ARPU", f"₴{business_df['arpu'].mean():.2f}")
            st.metric("Середній NPS", f"{business_df['nps'].mean():.2f}")
        with col2:
            st.metric("Середній Churn Rate", f"{business_df['churn_rate'].mean():.2f}%")
            st.metric("Середня вартість за MB", f"₴{business_df['cost_per_mb'].mean():.4f}")
        with col3:
            st.metric("Середній Utilization Rate", f"{business_df['utilization_rate'].mean():.2f}%")

        # Таблиця даних
        st.subheader("Таблиця бізнес показників")
        st.dataframe(business_df)

        # Графік ARPU та вартості за MB
        st.subheader("ARPU та вартість за MB")
        fig_arpu = make_subplots(specs=[[{"secondary_y": True}]])
        fig_arpu.add_trace(go.Scatter(x=business_df['date'], y=business_df['arpu'],
                                     name="ARPU", line=dict(color="blue")), secondary_y=False)
        fig_arpu.add_trace(go.Scatter(x=business_df['date'], y=business_df['cost_per_mb'],
                                     name="Вартість за MB", line=dict(color="red")), secondary_y=True)
        fig_arpu.update_layout(height=400)
        fig_arpu.update_yaxes(title_text="ARPU (₴)", secondary_y=False)
        fig_arpu.update_yaxes(title_text="Вартість за MB (₴)", secondary_y=True)
        st.plotly_chart(fig_arpu, use_container_width=True)

        # Графік Churn Rate та NPS
        st.subheader("Churn Rate та NPS")
        fig_churn_nps = go.Figure()
        fig_churn_nps.add_trace(go.Scatter(x=business_df['date'], y=business_df['churn_rate'],
                                          name="Churn Rate", line=dict(color="red")))
        fig_churn_nps.add_trace(go.Scatter(x=business_df['date'], y=business_df['nps'],
                                          name="NPS", line=dict(color="green")))
        fig_churn_nps.update_layout(height=400, yaxis_title="Значення")
        st.plotly_chart(fig_churn_nps, use_container_width=True)

    # Операційні показники
    with tab3:
        st.header("Операційні показники")

        # Метрики у верхній частині
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Середній час вирішення (год)", f"{operational_df['avg_resolution_time'].mean():.2f}")
            st.metric("Середня кількість звернень", f"{operational_df['support_tickets'].mean():.0f}")
        with col2:
            st.metric("Середній FCR Rate", f"{operational_df['fcr_rate'].mean():.2f}%")
            st.metric("Середні нові підключення", f"{operational_df['new_connections'].mean():.0f}")
        with col3:
            st.metric("Середнє використання потужності", f"{operational_df['capacity_utilization'].mean():.2f}%")

        # Таблиця даних
        st.subheader("Таблиця операційних показників")
        st.dataframe(operational_df)

        # Графік кількості звернень та нових підключень
        st.subheader("Звернення та нові підключення")
        fig_tickets = go.Figure()
        fig_tickets.add_trace(go.Bar(x=operational_df['date'], y=operational_df['support_tickets'],
                                    name="Кількість звернень"))
        fig_tickets.add_trace(go.Bar(x=operational_df['date'], y=operational_df['new_connections'],
                                    name="Нові підключення"))
        fig_tickets.update_layout(height=400, yaxis_title="Кількість", barmode='group')
        st.plotly_chart(fig_tickets, use_container_width=True)

        # Графік FCR Rate та використання потужності
        st.subheader("FCR Rate та використання потужності")
        fig_fcr = go.Figure()
        fig_fcr.add_trace(go.Scatter(x=operational_df['date'], y=operational_df['fcr_rate'],
                                    name="FCR Rate", line=dict(color="green")))
        fig_fcr.add_trace(go.Scatter(x=operational_df['date'], y=operational_df['capacity_utilization'],
                                    name="Використання потужності", line=dict(color="blue")))
        fig_fcr.update_layout(height=400, yaxis_title="Відсотки (%)")
        st.plotly_chart(fig_fcr, use_container_width=True)

        # Графік середнього часу вирішення
        st.subheader("Середній час вирішення")
        fig_resolution = px.line(operational_df, x='date', y='avg_resolution_time',
                                labels={'avg_resolution_time': 'Години', 'date': 'Дата'},
                                height=400)
        st.plotly_chart(fig_resolution, use_container_width=True)

if __name__ == "__main__":
    main()
