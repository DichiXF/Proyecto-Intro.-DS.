# Importar bibliotecas
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Cargar los datos
@st.cache
def load_data():
    file_path = "Limpieza1.csv"  # Cambia esto si tu archivo tiene otro nombre
    return pd.read_csv(file_path)

data = load_data()

# Función para eliminar valores atípicos
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# Limpiar datos de salarios eliminando valores atípicos
data_cleaned = remove_outliers(data, "salary_in_usd")

# Configuración del dashboard
st.title("Dashboard de Análisis de Salarios de Científicos de Datos")
st.markdown("""
Explora las relaciones entre tipo de trabajo, nivel de experiencia y como se relaciona con su salario.
""")

# --- Filtros ---
st.sidebar.header("Filtros")
employment_type = st.sidebar.multiselect(
    "Tipo de empleo:",
    options=data_cleaned["employment_type"].unique(),
    default=data_cleaned["employment_type"].unique()
)
experience_level = st.sidebar.multiselect(
    "Nivel de experiencia:",
    options=data_cleaned["experience_level"].unique(),
    default=data_cleaned["experience_level"].unique()
)

filtered_data = data_cleaned[
    (data_cleaned["employment_type"].isin(employment_type)) &
    (data_cleaned["experience_level"].isin(experience_level))
]

# --- Panel General de Estadísticas ---
st.subheader("Estadísticas Generales")

# Nivel de experiencia con el mayor número de personas
exp_nivel_mayor = filtered_data['experience_level'].value_counts().idxmax()

# Promedio de salario
promedio_salario = filtered_data['salary_in_usd'].mean()

# Título más popular
titulo_mas_popular = filtered_data['job_title'].value_counts().idxmax()

# Mediana de trabajo remoto
mediana_remoto = filtered_data['remote_ratio'].median() * 100  # Mediana en porcentaje

# Tipo de empleo más común
tipo_empleo_mas_comun = filtered_data['employment_type'].value_counts().idxmax()

# Mostrar las métricas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Nivel de Experiencia con más Personas", exp_nivel_mayor)
with col2:
    st.metric("Salario Promedio (USD)", f"${promedio_salario:,.2f}")
with col3:
    st.metric("Título más Popular", titulo_mas_popular)

col4, col5 = st.columns(2)

with col4:
    st.metric("Mediana de Trabajo Remoto (%)", f"{mediana_remoto:.1f}%")
with col5:
    st.metric("Tipo de Empleo más Común", tipo_empleo_mas_comun)

# --- GRÁFICAS ---
st.subheader("Visualizaciones de Datos Filtrados")

# Crear una cuadrícula de 3 columnas para las gráficas
col1, col2, col3 = st.columns(3, gap="small")  # Agregar 'gap="small"' para ajustar espaciado

# 1. Distribución de salarios
with col1:
    st.subheader("Distribución de Salarios (USD) ㅤㅤㅤㅤㅤㅤ")
    fig, ax = plt.subplots(figsize=(6, 4))  # Uniformar figsize
    sns.histplot(data=filtered_data, x="salary_in_usd", kde=True, color="blue", bins=30, ax=ax)
    ax.set_title("Distribución de Salarios")
    ax.set_xlabel("Salario en USD")
    st.pyplot(fig)

# 2. Relación entre nivel de experiencia y salario (sin valores atípicos)
with col2:
    st.subheader("Relación Nivel de Experiencia y Salario")
    fig, ax = plt.subplots(figsize=(6, 4))  # Uniformar figsize
    sns.boxplot(data=filtered_data, x="experience_level", y="salary_in_usd", palette="muted", ax=ax)
    ax.set_title("Salario por Nivel de Experiencia")
    ax.set_xlabel("Nivel de Experiencia")
    ax.set_ylabel("Salario en USD")
    st.pyplot(fig)

# 3. Trabajo remoto por tipo de empleo
with col3:
    st.subheader("Trabajo Remoto según Tipo de Empleo")
    remote_ratio_avg = (
        filtered_data.groupby("employment_type")["remote_ratio"]
        .mean()
        .reset_index()
        .rename(columns={"remote_ratio": "avg_remote_ratio"})
    )
    fig, ax = plt.subplots(figsize=(6, 4))  # Uniformar figsize
    ax.pie(
        remote_ratio_avg["avg_remote_ratio"],
        labels=remote_ratio_avg["employment_type"],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("coolwarm", len(remote_ratio_avg)),
    )
    ax.set_title("Trabajo Remoto por Tipo de Empleo")
    st.pyplot(fig)

# Crear otra cuadrícula para las siguientes gráficas
col4, col5, col6 = st.columns(3, gap="small")

# 4. Top 10 Salario por ubicación
with col4:
    st.subheader("Top 10: Salario Promedio por Ubicación de la Empresa")
    avg_salary_by_location = (
        filtered_data.groupby("company_location")["salary_in_usd"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .head(10)
    )
    fig, ax = plt.subplots(figsize=(6, 4))  # Uniformar figsize
    sns.barplot(
        data=avg_salary_by_location,
        x="salary_in_usd",
        y="company_location",
        palette="viridis",
        ax=ax
    )
    ax.set_title("Top 10 Salario por Ubicación")
    ax.set_xlabel("Salario Promedio (USD)")
    ax.set_ylabel("Ubicación")
    st.pyplot(fig)

# 5. Relación entre tamaño de empresa y salario (sin atípicos)
with col5:
    st.subheader("Relación entre Tamaño de Empresa y Salario")
    fig, ax = plt.subplots(figsize=(6, 4))  # Uniformar figsize
    sns.boxplot(data=filtered_data, x="company_size", y="salary_in_usd", palette="cool", ax=ax)
    ax.set_title("Salario por Tamaño de Empresa")
    ax.set_xlabel("Tamaño de la Empresa")
    ax.set_ylabel("Salario en USD")
    st.pyplot(fig)

# 6. Trabajo remoto por tamaño de empresa
with col6:
    st.subheader("Proporción de Trabajo Remoto por Tamaño de Empresa")
    fig, ax = plt.subplots(figsize=(6, 4))  # Uniformar figsize
    sns.barplot(data=filtered_data, x="company_size", y="remote_ratio", palette="pastel", ax=ax)
    ax.set_title("Trabajo Remoto por Tamaño de Empresa")
    ax.set_xlabel("Tamaño de la Empresa")
    ax.set_ylabel("Proporción de Trabajo Remoto (%)")
    st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("Fuente: Dataset proporcionado (`Limpieza1.csv`)")
