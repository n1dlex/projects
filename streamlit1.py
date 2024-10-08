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
    
    # Використання CSS для покращення вигляду
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

    # Головні KPI у верхній частині
    st.markdown("### 📈 Середні показники")
    col1, col2, col3, col4 = st.columns(4)
    
    # Технічні показники
    with col1:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Середня швидкість завантаження</div>
                <div class="metric-value">{format_metric(technical_df['download_speed'].mean(), 'speed')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Середня швидкість вивантаження</div>
                <div class="metric-value">{format_metric(technical_df['upload_speed'].mean(), 'speed')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Середнє значення втрат пакетів</div>
                <div class="metric-value">{format_metric(technical_df['packet_loss'].mean(), 'percentage')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Середнє значення затримки</div>
                <div class="metric-value">{format_metric(technical_df['latency'].mean(), 'time')}</div>
            </div>
        """, unsafe_allow_html=True)

    # Вкладки для різних категорій КРІ
    tab1, tab2, tab3 = st.tabs(["📡 Технічні КРІ", "💼 Бізнес КРІ", "🔧 Операційні КРІ"])

    # Технічні показники
    with tab1:
        st.markdown("## 📡 Технічні показники")
        
        # Графіки в два стовпці
        col1, col2 = st.columns(2)
        
        with col1:
            # Графік швидкостей
            fig_speed = px.line(technical_df, x='timestamp', 
                               y=['download_speed', 'upload_speed'],
                               labels={'value': 'Швидкість (Mbps)', 
                                      'timestamp': 'Час',
                                      'variable': 'Тип швидкості'},
                               title="📶 Швидкість передачі даних")
            fig_speed.update_layout(height=300)
            st.plotly_chart(fig_speed, use_container_width=True)

            # Графік packet loss та uptime
            fig_quality = px.line(technical_df, x='timestamp', 
                                 y=['packet_loss', 'uptime'],
                                 labels={'value': 'Відсотки (%)', 
                                        'timestamp': 'Час',
                                        'variable': 'Показник'},
                                 title="📊 Якість з'єднання")
            fig_quality.update_layout(height=300)
            st.plotly_chart(fig_quality, use_container_width=True)

        with col2:
            # Графік затримки та джитера
            fig_latency = px.line(technical_df, x='timestamp', 
                                 y=['latency', 'jitter'],
                                 labels={'value': 'Мілісекунди (ms)', 
                                        'timestamp': 'Час',
                                        'variable': 'Показник'},
                                 title="⏱️ Затримка та джитер")
            fig_latency.update_layout(height=300)
            st.plotly_chart(fig_latency, use_container_width=True)

        # Таблиця з можливістю сортування
        st.markdown("### 📋 Детальні дані")
        st.dataframe(technical_df, use_container_width=True)

    # Бізнес показники
    with tab2:
        st.markdown("## 💼 Бізнес показники")
        
        # Середні бізнес показники
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середній ARPU</div>
                    <div class="metric-value">{format_metric(business_df['arpu'].mean(), 'money')}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середній Churn Rate</div>
                    <div class="metric-value">{format_metric(business_df['churn_rate'].mean(), 'percentage')}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середнє NPS</div>
                    <div class="metric-value">{format_metric(business_df['nps'].mean(), 'money')}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середня вартість за MB</div>
                    <div class="metric-value">{format_metric(business_df['cost_per_mb'].mean(), 'money')}</div>
                </div>
            """, unsafe_allow_html=True)

        # Графіки бізнес показників
        col1, col2 = st.columns(2)

        with col1:
            # ARPU та Cost per MB
            fig_arpu = make_subplots(specs=[[{"secondary_y": True}]])
            fig_arpu.add_trace(
                go.Scatter(x=business_df['date'], y=business_df['arpu'],
                          name="ARPU", line=dict(color="#1f77b4")),
                secondary_y=False)
            fig_arpu.add_trace(
                go.Scatter(x=business_df['date'], y=business_df['cost_per_mb'],
                          name="Cost per MB", line=dict(color="#ff7f0e")),
                secondary_y=True)
            fig_arpu.update_layout(title="💰 ARPU та вартість за MB", height=300)
            fig_arpu.update_yaxes(title_text="ARPU (₴)", secondary_y=False)
            fig_arpu.update_yaxes(title_text="Вартість за MB (₴)", secondary_y=True)
            st.plotly_chart(fig_arpu, use_container_width=True)

        with col2:
            # Churn Rate та NPS
            fig_churn_nps = make_subplots(specs=[[{"secondary_y": True}]])
            fig_churn_nps.add_trace(
                go.Scatter(x=business_df['date'], y=business_df['churn_rate'],
                          name="Churn Rate", line=dict(color="#d62728")),
                secondary_y=False)
            fig_churn_nps.add_trace(
                go.Scatter(x=business_df['date'], y=business_df['nps'],
                          name="NPS", line=dict(color="#2ca02c")),
                secondary_y=True)
            fig_churn_nps.update_layout(title="📉 Churn Rate та NPS", height=300)
            fig_churn_nps.update_yaxes(title_text="Churn Rate (%)", secondary_y=False)
            fig_churn_nps.update_yaxes(title_text="NPS", secondary_y=True)
            st.plotly_chart(fig_churn_nps, use_container_width=True)

        # Таблиця з можливістю сортування
        st.markdown("### 📋 Детальні дані")
        st.dataframe(business_df, use_container_width=True)

    # Операційні показники
    with tab3:
        st.markdown("## 🔧 Операційні показники")

        # Середні операційні показники
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середній час вирішення</div>
                    <div class="metric-value">{format_metric(operational_df['avg_resolution_time'].mean(), 'time')}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середня кількість квитків</div>
                    <div class="metric-value">{operational_df['support_tickets'].mean():.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середній FCR Rate</div>
                    <div class="metric-value">{format_metric(operational_df['fcr_rate'].mean(), 'percentage')}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-title">Середня кількість нових з'єднань</div>
                    <div class="metric-value">{operational_df['new_connections'].mean():.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        # Графіки операційних показників
        col1, col2 = st.columns(2)

        with col1:
            # Час вирішення проблем та нові з'єднання
            fig_resolution = make_subplots(specs=[[{"secondary_y": True}]])
            fig_resolution.add_trace(
                go.Scatter(x=operational_df['date'], y=operational_df['avg_resolution_time'],
                          name="Середній час вирішення", line=dict(color="#1f77b4")),
                secondary_y=False)
            fig_resolution.add_trace(
                go.Scatter(x=operational_df['date'], y=operational_df['new_connections'],
                          name="Нові з'єднання", line=dict(color="#ff7f0e")),
                secondary_y=True)
            fig_resolution.update_layout(title="⏳ Час вирішення проблем та нові з'єднання", height=300)
            fig_resolution.update_yaxes(title_text="Час вирішення (години)", secondary_y=False)
            fig_resolution.update_yaxes(title_text="Нові з'єднання", secondary_y=True)
            st.plotly_chart(fig_resolution, use_container_width=True)

        with col2:
            # Кількість квитків підтримки та коефіцієнт FCR
            fig_tickets = make_subplots(specs=[[{"secondary_y": True}]])
            fig_tickets.add_trace(
                go.Scatter(x=operational_df['date'], y=operational_df['support_tickets'],
                          name="Квитки підтримки", line=dict(color="#d62728")),
                secondary_y=False)
            fig_tickets.add_trace(
                go.Scatter(x=operational_df['date'], y=operational_df['fcr_rate'],
                          name="FCR Rate", line=dict(color="#2ca02c")),
                secondary_y=True)
            fig_tickets.update_layout(title="🎟️ Квитки підтримки та FCR Rate", height=300)
            fig_tickets.update_yaxes(title_text="Кількість квитків", secondary_y=False)
            fig_tickets.update_yaxes(title_text="FCR Rate (%)", secondary_y=True)
            st.plotly_chart(fig_tickets, use_container_width=True)

        # Таблиця з можливістю сортування
        st.markdown("### 📋 Детальні дані")
        st.dataframe(operational_df, use_container_width=True)

if __name__ == "__main__":
    main()
