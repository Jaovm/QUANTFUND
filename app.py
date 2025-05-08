import streamlit as st

# Configuração da página
st.set_page_config(layout="wide", page_title="Modelo Quant-Fundamentalista")

# Barra lateral para navegação
st.sidebar.title("Navegação")
app_mode = st.sidebar.selectbox("Escolha o Módulo:",
    ["Página Inicial", "Análise de Ativos", "Backtesting", "Recomendações", "Otimização de Carteira", "Cenário Macroeconômico"])

# Conteúdo da Página Inicial
if app_mode == "Página Inicial":
    st.title("Bem-vindo ao Modelo Quantitativo e Fundamentalista")
    st.markdown("""
    Este é um sistema interativo para análise de investimentos, combinando abordagens quantitativas e fundamentalistas.
    Utilize o menu na barra lateral para navegar entre os diferentes módulos.
    """)
    st.subheader("Funcionalidades Principais:")
    st.markdown("""
    - **Análise de Ativos:** Visualize dados históricos, indicadores fundamentalistas e quantitativos de empresas.
    - **Backtesting:** Teste estratégias de investimento com dados históricos.
    - **Recomendações:** Receba sugestões de ativos com base em múltiplos critérios e no cenário macroeconômico.
    - **Otimização de Carteira:** Construa e balanceie sua carteira de investimentos com base em diferentes teorias de alocação.
    - **Cenário Macroeconômico:** Acompanhe indicadores macroeconômicos relevantes.
    """)

elif app_mode == "Análise de Ativos":
    st.title("Módulo: Análise de Ativos")
    st.write("Em desenvolvimento...")
    # Aqui virá o código para análise de ativos individuais

elif app_mode == "Backtesting":
    st.title("Módulo: Backtesting de Estratégias")
    st.write("Em desenvolvimento...")
    # Aqui virá o código para o módulo de backtesting

elif app_mode == "Recomendações":
    st.title("Módulo: Recomendações de Investimento")
    st.write("Em desenvolvimento...")
    # Aqui virá o código para o sistema de recomendações

elif app_mode == "Otimização de Carteira":
    st.title("Módulo: Otimização de Carteira")
    st.write("Em desenvolvimento...")
    # Aqui virá o código para otimização e balanceamento de carteira

elif app_mode == "Cenário Macroeconômico":
    st.title("Módulo: Análise de Cenário Macroeconômico")
    st.write("Em desenvolvimento...")
    # Aqui virá o código para análise de dados macroeconômicos

# Rodapé (opcional)
# st.sidebar.markdown("---_)
# st.sidebar.info("Desenvolvido por Manus AI")

