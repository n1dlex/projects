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

    # Бізнес показники
    with tab2:
        st.header("Бізнес показники")

        # Метрики залишаються без змін
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

        # Оновлений графік для всіх бізнес КРІ
        st.subheader("Графік всіх бізнес показників")
        
        fig_business = make_subplots(specs=[[{"secondary_y": True}]])
        
        # ARPU на основній осі
        fig_business.add_trace(
            go.Scatter(x=business_df['date'], y=business_df['arpu'], name="ARPU", line=dict(color="blue")),
            secondary_y=False
        )
        
        # Інші метрики на додатковій осі
        for column, color in zip(['churn_rate', 'nps', 'utilization_rate'], ['red', 'green', 'purple']):
            fig_business.add_trace(
                go.Scatter(x=business_df['date'], y=business_df[column], name=column.replace('_', ' ').title(), line=dict(color=color)),
                secondary_y=True
            )
        
        # Додаємо cost_per_mb на окремий графік через різницю в масштабі
        st.subheader("Графік вартості за MB")
        fig_cost = px.line(business_df, x='date', y='cost_per_mb', title='Динаміка вартості за MB')
        
        fig_business.update_layout(
            title="Бізнес показники",
            xaxis_title="Дата",
            height=500
        )
        fig_business.update_yaxes(title_text="ARPU (₴)", secondary_y=False)
        fig_business.update_yaxes(title_text="Інші показники (%)", secondary_y=True)
        
        st.plotly_chart(fig_business, use_container_width=True)
        st.plotly_chart(fig_cost, use_container_width=True)

    # Операційні показники
    with tab3:
        st.header("Операційні показники")

        # Метрики залишаються без змін
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

        # Оновлені графіки для операційних КРІ
        st.subheader("Графіки операційних показників")

        # Створюємо графік з двома у-осями
        fig_operational = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Кількісні показники на основній осі
        fig_operational.add_trace(
            go.Bar(x=operational_df['date'], y=operational_df['support_tickets'], name="Кількість звернень"),
            secondary_y=False
        )
        fig_operational.add_trace(
            go.Bar(x=operational_df['date'], y=operational_df['new_connections'], name="Нові підключення"),
            secondary_y=False
        )
        
        # Відсоткові показники на додатковій осі
        fig_operational.add_trace(
            go.Scatter(x=operational_df['date'], y=operational_df['fcr_rate'], name="FCR Rate", line=dict(color="green")),
            secondary_y=True
        )
        fig_operational.add_trace(
            go.Scatter(x=operational_df['date'], y=operational_df['capacity_utilization'], name="Використання потужності", line=dict(color="red")),
            secondary_y=True
        )
        fig_operational.add_trace(
            go.Scatter(x=operational_df['date'], y=operational_df['avg_resolution_time'], name="Час вирішення", line=dict(color="orange")),
            secondary_y=True
        )
        
        fig_operational.update_layout(
            title="Всі операційні показники",
            xaxis_title="Дата",
            barmode='group',
            height=600
        )
        fig_operational.update_yaxes(title_text="Кількість", secondary_y=False)
        fig_operational.update_yaxes(title_text="Відсотки та час", secondary_y=True)
        
        st.plotly_chart(fig_operational, use_container_width=True)

if __name__ == "__main__":
    main()
