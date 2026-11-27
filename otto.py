import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#títulos
st.set_page_config(page_title="Simulador Ciclo de Otto", layout="wide")
st.title("Simulador del Ciclo Termodinámico de Otto")

#fluido
st.sidebar.header("1- Fluido de Trabajo")
fluido = st.sidebar.selectbox("Seleccionar fluido de trabajo", ["Aire", "Mezcla aire-combustible", "Personalizado"])

if fluido == "Aire":
    Rf_t, cv_t, k_t = 0.287, 0.718, 1.4
elif fluido == "Mezcla aire-combustible":
    Rf_t, cv_t, k_t = 0.290, 0.821, 1.35
else:
    Rf_t, cv_t, k_t = 0.287, 0.718, 1.4

#entrada
st.sidebar.header("2- Entrada de datos")
Rf = st.sidebar.number_input("Constante del gas R (kJ/kg·K)", value=Rf_t, step=0.001, format="%.3f")
cv = st.sidebar.number_input("Calor específico Cv (kJ/kg·K)", value=cv_t, step=0.001, format="%.3f")
k = st.sidebar.number_input("Relación de calores específicos (k)", value=k_t, step=0.01, format="%.2f")

P1 = st.sidebar.number_input("Presión inicial P1 (kPa)", value=100.0, min_value=0.01, step=5.0)
T1 = st.sidebar.number_input("Temperatura inicial T1 (K)", value=290.15, min_value=200.0, step=10.0)
r = st.sidebar.slider("Relación de compresión (r = V1/V2)", min_value=4.0, max_value=18.0, value=8.0, step=0.5)
q_en = st.sidebar.number_input("Calor agregado (entrada) (kJ/kg)", value=800.0, min_value=0.01, step=50.0)
T0 = st.sidebar.number_input("Temperatura ambiente T0 (K)", value=float(T1), min_value=1.0, step=5.0, format="%.2f")

#cálculos

#estado 1 (inicia compresión)
v1 = (Rf*T1)/P1  #m³/kg
s1 = 0.0

#estado 2 (adición de calor isocórico 2->3)
v2=v1/r
T2 = T1*(r**(k-1))
P2 = P1*(r**k)
s2 = s1

#estado 3 (expansión isentrópica 3->4)
v3 = v2
T3 = T2+(q_en/cv)
P3 = P2*(T3/T2)
s3 = s2+cv*np.log(T3/T2)

#estado 4 (rechazo de calor isócoro 4->1)
v4 = v1
T4 = T3*((1 / r)**(k - 1))
P4 = P3*((1 / r)**k)
s4 = s3

#proceso 1-2 compresión isentrópica
q12 = 0.0
w12 = cv*(T1-T2)
n12 = (abs(w12)/(cv*(T2-T1)))*100
ds_12 = s2 - s1
#proceso 2-3 adición de calor isócoro
w23 = P2*(v3-v2)  #igual a 0
q23 = cv*(T3-T2)
n23 = ((cv*(T3-T2))/q_en)*100
ds_23 = s3 - s2
#proceso 3-4 exp. isentrópica
q34 = 0.0
w34 = cv*(T3-T4)
n34 = (w34/(cv*T3))*100
ds_34 = s4 - s3
#proceso 4-1 rechazo de calor isócoro
w41 = P4*(v1-v4)  #igual a 0
q41 = cv*(T4-T1)
n41 = (q41/q23)*100
ds_41 = s1 - s4
#valores netos
wnet = w12+w23+w34+w41
qnet = q12+q23+q34-q41
nnet = (wnet/q_en)*100
ds_neto = ds_12 + ds_23 + ds_34 + ds_41
s_gen = (-q_en / T3) + (q41 / T0)
w_perd = T0 * s_gen      
w_ideal = wnet + w_perd

#tablas resultados
#propiedades
st.subheader("Propiedades por Estado")
prop_estados = pd.DataFrame({
    "Estado": ["1 (Compresión)", "2 (Combustión)", "3 (Expansión)", "4 (Rechazo de Calor)"],
    "Presión (kPa)": [P1, P2, P3, P4],
    "Temperatura (K)": [T1, T2, T3, T4],
    "Volumen (m³/kg)": [v1, v2, v3, v4],
    "Entropía Δs (kJ/kg·K)": [s1, s2, s3, s4]
})
st.dataframe(prop_estados.style.format({
    "Presión (kPa)": "{:.4f}",
    "Temperatura (K)": "{:.4f}",
    "Volumen (m³/kg)": "{:.5f}",
    "Entropía s (kJ/kg·K)": "{:.5f}"
}), use_container_width=True, hide_index=True)

#calor, trabajo, eficiencia
st.subheader("Calor, Trabajo y Eficiencia")
parametros_cal = pd.DataFrame({
    "Proceso": [
        "1 → 2: ",
        "2 → 3: ",
        "3 → 4: ",
        "4 → 1: ",
        "━━━ Total del Ciclo ━━━"
    ],
    "Calor q (kJ/kg)": [
        f"{q12:.2f}",
        f"{q23:.2f}",
        f"{q34:.2f}",
        f"-{q41:.2f}",
        f"{qnet:.2f}"
    ],
    "Trabajo w (kJ/kg)": [
        f"{w12:.2f}",
        f"{w23:.2f}",
        f"{w34:.2f}",
        f"{w41:.2f}",
        f"{wnet:.2f}"
    ],
    "Cambio Entropía Δs (kJ/kg·K)": [
        f"{ds_12:.2f}",
        f"+{ds_23:.2f}",
        f"{ds_34:.2f}",
        f"{ds_41:.2f}",
        f"{ds_neto:.2f}"
    ],
    "Eficiencia (%)": [
        f"{n12:.2f} %",
        f"{n23:.2f} %",
        f"{n34:.2f} %",
        f"{n41:.2f} %",
        f"{nnet:.2f} %"
    ]
})
st.dataframe(parametros_cal, use_container_width=True, hide_index=True)

st.subheader("Parámetros adicionales")
col1, col2, col3 = st.columns(3)
col1.metric("Trabajo Ideal (w_ideal)", f"{w_ideal:.2f} kJ/kg")
col2.metric("Trabajo Perdido (w_lost", f"{w_perd:.2f} kJ/kg")
col3.metric("Entropía Generada (s_gen)", f"{s_gen:.4f} kJ/kg·K")

#diagramas
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Free Serif', 'Utkal', 'Free Serif']
tab1, tab2 = st.tabs(["Diagramas termodinámicos", "Ecuaciones"])
#gráficos P-v y T-s
with tab1:
    st.subheader("Diagramas Termodinámicos del Ciclo")
    col_graf1, col_graf2 = st.columns(2)

    #diagrama P-v
    with col_graf1:
        fig1, ax1 = plt.subplots(figsize=(5.5, 4.2))
        v_12 = np.linspace(v1, v2, 100)
        P_12 = P1 * (v1 / v_12) ** k

        v_34 = np.linspace(v3, v4, 100)
        P_34 = P3 * (v3 / v_34) ** k

        ax1.plot(v_12, P_12, 'b-', linewidth=2, label="1→2 Compresión")
        ax1.plot([v2, v3], [P2, P3], 'r-', linewidth=2, label="2→3 Adición Q")
        ax1.plot(v_34, P_34, 'g-', linewidth=2, label="3→4 Expansión")
        ax1.plot([v4, v1], [P4, P1], 'c-', linewidth=2, label="4→1 Rechazo Q")
        ax1.scatter([v1, v2, v3, v4], [P1, P2, P3, P4], color='black', zorder=5, s=30)

        #desplazamiento para que no toquen las líneas
        offsets_pv = [(4, -10), (4, 4), (4, 4), (4, 4)]
        for i, txt in enumerate(['1', '2', '3', '4']):
            ax1.annotate(txt, ([v1, v2, v3, v4][i], [P1, P2, P3, P4][i]),
                         textcoords="offset points", xytext=offsets_pv[i],
                         fontsize=10, fontweight='bold')

        ax1.set_title("Diagrama P - V", fontsize=11, fontweight='bold')
        ax1.set_xlabel("Volumen (m³/kg)", fontsize=9)
        ax1.set_ylabel("Presión P (kPa)", fontsize=9)
        ax1.tick_params(labelsize=8)
        ax1.margins(x=0.12, y=0.12)  #márgenes
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.legend(fontsize=8, loc="upper right")
        plt.tight_layout()
        st.pyplot(fig1)

    #diagrama T-s
    with col_graf2:
        fig2, ax2 = plt.subplots(figsize=(5.5, 4.2))
        T_23 = np.linspace(T2, T3, 100)
        s_23 = s2 + cv * np.log(T_23 / T2)

        T_41 = np.linspace(T4, T1, 100)
        s_41 = s4 + cv * np.log(T_41 / T4)

        ax2.plot([s1, s2], [T1, T2], 'b-', linewidth=2, label="1→2 Compresión")
        ax2.plot(s_23, T_23, 'r-', linewidth=2, label="2→3 Adición Q")
        ax2.plot([s3, s4], [T3, T4], 'g-', linewidth=2, label="3→4 Expansión")
        ax2.plot(s_41, T_41, 'c-', linewidth=2, label="4→1 Rechazo Q")
        ax2.scatter([s1, s2, s3, s4], [T1, T2, T3, T4], color='black', zorder=5, s=30)

        offsets_ts = [(-10, -8), (-10, 4), (4, 4), (4, -8)]
        for i, txt in enumerate(['1', '2', '3', '4']):
            ax2.annotate(txt, ([s1, s2, s3, s4][i], [T1, T2, T3, T4][i]),
                         textcoords="offset points", xytext=offsets_ts[i],
                         fontsize=10, fontweight='bold')

        ax2.set_title("Diagrama T - s", fontsize=11, fontweight='bold')
        ax2.set_xlabel("Cambio de Entropía Δs (kJ/kg·K)", fontsize=9)
        ax2.set_ylabel("Temperatura T (K)", fontsize=9)
        ax2.tick_params(labelsize=8)
        ax2.margins(x=0.12, y=0.12)
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.legend(fontsize=8, loc="upper left")
        plt.tight_layout()
        st.pyplot(fig2)


with tab2:
    st.markdown("Ecuaciones Fundamentales Implementadas")
    st.latex(r"r = \frac{V_1}{V_2} = \frac{v_1}{v_2}")
    st.latex(r"T_2 = T_1 r^{k-1}, \qquad P_2 = P_1 r^k")
    st.latex(r"q_{\text{entrada}} = c_v (T_3 - T_2), \qquad P_3 = P_2 \left(\frac{T_3}{T_2}\right)")
    st.latex(r"T_4 = T_3 \left(\frac{1}{r}\right)^{k-1}, \qquad P_4 = P_3 \left(\frac{1}{r}\right)^k")
    st.latex(r"\eta_{\text{th}} = \frac{w_{\text{neto}}}{q_{\text{entrada}}} = 1 - \frac{1}{r^{k-1}}")
    st.latex(r"w_{\text{ideal}} = q_{\text{entrada}}\left(1 - \frac{T_0}{T_3}\right), \qquad s_{\text{gen}} = -\frac{q_{\text{entrada}}}{T_3} + \frac{q_{\text{salida}}}{T_0}, \qquad w_{\text{lost}} = T_0 s_{\text{gen}}")
