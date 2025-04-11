
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Conversor de Sobras", layout="centered")
st.title("🔧 Conversor de Sobras para CSV Padronizado")
st.markdown("Envie o PDF com as sobras e o CSV base para gerar o novo arquivo padronizado.")

# Função para extrair linhas do PDF
def extrair_linhas_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    linhas_extraidas = []
    for page in doc:
        texto = page.get_text()
        for linha in texto.split("\n"):
            if any(palavra in linha for palavra in ["MDP", "MDF"]):
                partes = linha.split()
                if len(partes) >= 5:
                    tipo = partes[0]
                    cor = ' '.join(partes[2:-3])
                    esp = partes[1].replace('mm', '').replace('MM', '').strip()
                    largura = partes[-3].replace('.', '').replace(',', '.')
                    profundidade = partes[-2].replace('.', '').replace(',', '.')
                    try:
                        esp_float = float(esp)
                        larg = int(float(largura))
                        prof = int(float(profundidade))
                        item = f"{tipo} - {cor} {esp_float}mm,L,{larg},{prof},{esp_float},8,8,,1"
                        linhas_extraidas.append(item)
                    except:
                        pass
    return linhas_extraidas

# Upload dos arquivos
pdf = st.file_uploader("📄 Envie o PDF de sobras", type=["pdf"])
csv = st.file_uploader("📊 Envie o CSV base (opcional)", type=["csv"])

if pdf is not None:
    with st.spinner("Processando o PDF..."):
        linhas_formatadas = extrair_linhas_pdf(pdf)

    if not linhas_formatadas:
        st.warning("Não foram encontradas linhas válidas no PDF.")
    else:
        st.success(f"{len(linhas_formatadas)} linhas extraídas com sucesso!")
        st.code("\n".join(linhas_formatadas[:10]), language="text")

        if csv:
            df_base = pd.read_csv(csv)
            df_novos = pd.DataFrame(linhas_formatadas, columns=["Materiais"])
            df_final = pd.concat([df_base, df_novos], ignore_index=True)
        else:
            df_final = pd.DataFrame(linhas_formatadas, columns=["Materiais"])

        csv_final = df_final.to_csv(index=False, header=False).encode("utf-8")

        st.download_button(
            label="📥 Baixar CSV Final",
            data=csv_final,
            file_name="materiais_formatado.csv",
            mime="text/csv"
        )
