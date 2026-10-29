import streamlit as st
import json
from datetime import datetime
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from PIL import Image

# Configuração da página Streamlit
st.set_page_config(page_title="NaParede JP - Emissão", page_icon="🖼️", layout="wide")

# --- ESTILIZAÇÃO CSS (Dark Theme + Dourado Premium) ---
st.markdown("""
    <style>
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }
        header {visibility: hidden;}
        
        .main-title {
            color: #D4AF37;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 10px;
            text-align: center;
        }
        .sub-title {
            color: #888888;
            font-size: 14px;
            text-align: center;
            margin-bottom: 30px;
        }
        .card-title {
            color: #D4AF37;
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 15px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .custom-card {
            background-color: #1C1C1C;
            border: 1px solid #2A2A2A;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .card-divider {
            border-bottom: 1px solid #2A2A2A;
            margin-bottom: 20px;
            margin-top: -5px;
        }
        .stTextInput label, .stSelectbox label, .stNumberInput label {
            color: #888888 !important;
            font-size: 12px !important;
            font-weight: bold !important;
            margin-bottom: 2px !important;
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>select, .stNumberInput>div>div>input {
            background-color: #121212 !important;
            color: #E0E0E0 !important;
            border: 1px solid #2A2A2A !important;
            border-radius: 6px !important;
            padding: 10px !important;
            font-size: 13px !important;
        }
        .stNumberInput button { display: none !important; }
        .stTextArea textarea {
            background-color: #121212 !important;
            color: #E0E0E0 !important;
            border: 1px solid #2A2A2A !important;
            border-radius: 6px !important;
            min-height: 80px;
        }
        .stButton>button[kind="secondary"] {
            background-color: #121212 !important;
            color: #D4AF37 !important;
            border: 1px solid #D4AF37 !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            width: 100% !important;
        }
        .stButton>button[kind="primary"] {
            background-color: #D4AF37 !important;
            color: #111111 !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            width: 100% !important;
            padding: 15px !important;
        }
        .total-panel {
            background-color: #D4AF37;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .total-panel-title {
            color: #634F12;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .total-panel-value {
            color: #111111;
            font-size: 32px;
            font-weight: bold;
            margin: 5px 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- PROCURA DA LOGO ---
logo_path = None
lista_tentativas = ["LOGO NAPAREDE.jpg", "LOGO NAPAREDE_2.jpg", "logo.png", "logo.jpg"]
for nome in lista_tentativas:
    if os.path.exists(nome):
        logo_path = nome
        break

# --- INICIALIZAÇÃO DE ESTADO ---
if 'itens_pedido' not in st.session_state:
    st.session_state.itens_pedido = []
if 'cliente' not in st.session_state:
    st.session_state.cliente = ""
if 'telefone' not in st.session_state:
    st.session_state.telefone = ""
if 'pagto' not in st.session_state:
    st.session_state.pagto = "PIX (À Vista)"
if 'entrega' not in st.session_state:
    st.session_state.entrega = datetime.now().strftime("%d/%m/%Y")
if 'obs' not in st.session_state:
    st.session_state.obs = ""
if 'titulo_item' not in st.session_state:
    st.session_state.titulo_item = ""
if 'preco_item' not in st.session_state:
    st.session_state.preco_item = 0.00
if 'qtd_item' not in st.session_state:
    st.session_state.qtd_item = 1

def adicionar_ao_carrinho(titulo, medida, moldura, vidro, qtd, preco):
    if titulo and preco > 0:
        total_item = qtd * preco
        num_item = len(st.session_state.itens_pedido) + 1
        st.session_state.itens_pedido.append({
            "num": num_item, "titulo": titulo, "medida": medida,
            "moldura": moldura, "vidro": vidro, "qtd": qtd,
            "unitario": preco, "total": total_item
        })
        st.session_state.titulo_item = ""
        st.session_state.preco_item = 0.0
        st.session_state.qtd_item = 1

def remover_ultimo_item():
    if st.session_state.itens_pedido:
        st.session_state.itens_pedido.pop()

def gerar_pdf(cliente, fone, pagto, entrega, obs, itens, total_geral, logo):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    cor_texto, cor_subtexto = HexColor("#2C3E50"), HexColor("#7F8C8D")    
    cor_fundo_head, cor_linha = HexColor("#F8F9F9"), HexColor("#D4AF37")       

    c.setFillColor(cor_fundo_head)
    c.rect(0, height - 3.5*cm, width, 3.5*cm, fill=1, stroke=0)
    
    if logo and os.path.exists(logo):
        try:
            c.drawImage(logo, 2*cm, height - 3.1*cm, width=3*cm, height=2.8*cm, preserveAspectRatio=True, anchor='c')
        except Exception:
            pass
            
    c.setFillColor(cor_texto)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(5.5*cm, height - 1.5*cm, "NaParede JP - Quadros Decorativos / CNPJ 44.078.974/0001-63")
    c.setFont("Helvetica", 10)
    c.drawString(5.5*cm, height - 2*cm, "Quadros Decorativos & Gráfica - João Pessoa")
    c.setFillColor(cor_subtexto)
    c.drawString(5.5*cm, height - 2.5*cm, "Contato: (83) 98739-1975 | Instagram: @naparedejp")
    
    c.setStrokeColor(cor_linha)
    c.setLineWidth(2)
    c.line(0, height - 3.5*cm, width, height - 3.5*cm)

    y = height - 5*cm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(cor_texto)
    c.drawString(2*cm, y, "RECIBO DE VENDA E ENCOMENDA")
    c.setFont("Helvetica", 10)
    c.setFillColor(cor_subtexto)
    c.drawString(width - 6.5*cm, y, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    y -= 1*cm
    c.setFillColor(HexColor("#F2F4F4"))
    c.rect(2*cm, y - 2*cm, width - 4*cm, 2*cm, fill=1, stroke=0)
    c.setFillColor(cor_texto)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2.3*cm, y - 0.6*cm, f"CLIENTE: {cliente}")
    c.drawString(11*cm, y - 0.6*cm, f"WHATSAPP: {fone}")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*cm, y - 1.4*cm, f"Pagamento: {pagto}")
    c.drawString(11*cm, y - 1.4*cm, f"Previsão Entrega: {entrega}")

    y -= 3.5*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "DETALHES DA ENCOMENDA")
    y -= 0.2*cm
    c.setStrokeColor(HexColor("#BDC3C7"))
    c.setLineWidth(1)
    c.line(2*cm, y, width - 2*cm, y)
    y -= 0.8*cm

    for item in itens:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(cor_texto)
        c.drawString(2*cm, y, f"{item['qtd']}x   {item['titulo']}")
        valor_tot = f"R$ {item['total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        c.drawRightString(width - 2*cm, y, valor_tot)
        y -= 0.5*cm
        c.setFont("Helvetica", 9)
        c.setFillColor(cor_subtexto)
        c.drawString(2.8*cm, y, f"Medida: {item['medida']} | Moldura: {item['moldura']} | Vidro: {item['vidro']}")
        y -= 0.6*cm
        c.setStrokeColor(HexColor("#E5E8E8"))
        c.line(2*cm, y, width - 2*cm, y)
        y -= 0.6*cm
        if y < 7*cm:
            c.showPage()
            y = height - 2*cm

    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(cor_texto)
    c.drawRightString(width - 5.5*cm, y, "TOTAL DO PEDIDO:")
    c.setFillColor(HexColor("#27AE60")) 
    c.drawRightString(width - 2*cm, y, f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if obs:
        y -= 2*cm
        c.setFillColor(cor_texto)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y, "OBSERVAÇÕES DO PEDIDO:")
        y -= 0.6*cm
        c.setFont("Helvetica", 9)
        c.setFillColor(cor_subtexto)
        for linha in obs.split('\n'):
            c.drawString(2*cm, y, linha)
            y -= 0.5*cm

    y_sig = 3.5*cm
    c.setStrokeColor(cor_texto)
    c.setLineWidth(1)
    c.line(width/2.0 - 4.5*cm, y_sig, width/2.0 + 4.5*cm, y_sig)
    c.setFillColor(cor_texto)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width/2.0, y_sig - 0.5*cm, "MARTA BEATRIZ ARAUJO SANTOS PACIFICO")
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(cor_subtexto)
    c.drawCentredString(width/2.0, y_sig - 1.5*cm, "Agradecemos pela confiança em nossa loja!")
    c.save()
    buffer.seek(0)
    return buffer

# Interface Visual
if logo_path:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(logo_path, use_column_width=True)
else:
    st.warning("⚠️ Logo não encontrada na pasta. O recibo sairá sem logo.")
    uploaded_file = st.file_uploader("Enviar Logo da Loja:", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        with open("LOGO NAPAREDE.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Logo guardada com sucesso! Atualizando...")
        st.rerun()

st.markdown('<div class="main-title">NaParede JP</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Emissão de Recibos / Mobile</div>', unsafe_allow_html=True)

# Card 1: Cliente
st.markdown('<div class="custom-card"><div class="card-title">👤 1. Cliente & Condições</div><div class="card-divider"></div>', unsafe_allow_html=True)
st.session_state.cliente = st.text_input("Nome do Cliente *", value=st.session_state.cliente, placeholder="Ex: Rodrigo Fontes")
st.session_state.telefone = st.text_input("Telefone / WhatsApp *", value=st.session_state.telefone, placeholder="(83) 99654-1234")
col_p1, col_p2 = st.columns(2)
with col_p1:
    lista_pagto = ["PIX (À Vista)", "Cartão de Crédito", "Cartão de Débito", "50% Sinal + 50% Entrega", "Dinheiro"]
    st.session_state.pagto = st.selectbox("Pagamento", lista_pagto, index=lista_pagto.index(st.session_state.pagto) if st.session_state.pagto in lista_pagto else 0)
with col_p2:
    st.session_state.entrega = st.text_input("Entrega", value=st.session_state.entrega)
st.markdown('</div>', unsafe_allow_html=True)

# Card 2: Especificações
st.markdown('<div class="custom-card"><div class="card-title">🖼️ 2. Especificações do Quadro</div><div class="card-divider"></div>', unsafe_allow_html=True)
t_item = st.text_input("Título da Obra / Imagem *", value=st.session_state.titulo_item)
m_item = st.selectbox("Medidas (cm)", ["30x42 cm (A3)", "40x60 cm", "50x70 cm", "60x90 cm", "70x100 cm", "100x150 cm", "Sob Medida"], index=3)
mold_item = st.selectbox("Tipo de Moldura", ["Filete Preto", "Filete Branco", "Caixa Alta Preto", "Caixa Alta Carvalho", "Chanfrada", "Sem Moldura (Canvas)"], index=2)
v_item = st.selectbox("Acabamento / Vidro", ["Vidro Comum 2mm", "Vidro Antirreflexo", "Acrílico 2mm", "Canvas (Sem Vidro)"])
col_q, col_v = st.columns(2)
with col_q:
    q_item = st.number_input("Qtd", min_value=1, value=st.session_state.qtd_item, step=1)
with col_v:
    p_item = st.number_input("Valor (R$)*", min_value=0.0, value=st.session_state.preco_item, format="%.2f")

if st.button("➕ Adicionar ao Carrinho", use_container_width=True, type="secondary"):
    adicionar_ao_carrinho(t_item, m_item, mold_item, v_item, q_item, p_item)
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Card 3: Itens
st.markdown('<div class="custom-card"><div class="card-title">📋 Itens Inclusos no Pedido</div><div class="card-divider"></div>', unsafe_allow_html=True)
if not st.session_state.itens_pedido:
    st.markdown("<div style='text-align:center; color:#888; font-size:12px;'>O carrinho está vazio.</div>", unsafe_allow_html=True)
else:
    for item in st.session_state.itens_pedido:
        u_str = f"R$ {item['unitario']:,.2f}".replace(".", ",")
        t_str = f"R$ {item['total']:,.2f}".replace(".", ",")
        st.markdown(f"**{item['qtd']}x {item['titulo']}**")
        st.markdown(f"<span style='color:#888; font-size:12px;'>{item['medida']} | {item['moldura']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#D4AF37; font-weight:bold;'>Total: {t_str}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='border:0; border-top: 1px solid #2A2A2A; margin: 10px 0;'>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.itens_pedido:
    if st.button("🗑️ Remover Último Item", use_container_width=True):
        remover_ultimo_item()
        st.rerun()

# Card 4: Observações e Totais
st.markdown('<div class="custom-card"><div class="card-title">📝 Observações do Pedido</div>', unsafe_allow_html=True)
st.session_state.obs = st.text_area("", value=st.session_state.obs, label_visibility="collapsed", placeholder="Notas sobre o pedido...")
st.markdown('</div>', unsafe_allow_html=True)

total_final = sum(i["total"] for i in st.session_state.itens_pedido)
tot_str = f"R$ {total_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.markdown(f"""
<div class="total-panel">
    <div class="total-panel-title">VALOR TOTAL DO PEDIDO</div>
    <div class="total-panel-value">{tot_str}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.cliente and st.session_state.itens_pedido:
    pdf_data = gerar_pdf(st.session_state.cliente, st.session_state.telefone, st.session_state.pagto, st.session_state.entrega, st.session_state.obs, st.session_state.itens_pedido, total_final, logo_path)
    
    st.download_button(
        label="💾 SALVAR RECIBO PDF", 
        data=pdf_data, 
        file_name=f"Recibo_{st.session_state.cliente.replace(' ','_')}.pdf", 
        mime="application/pdf", 
        type="primary",
        use_container_width=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("✍️ Assinar digitalmente (Gov.br)", "https://assinador.iti.br/assinatura/index.xhtml", use_container_width=True)
else:
    st.info("⚠️ Adicione itens e preencha o nome do cliente para liberar o botão do PDF.")
