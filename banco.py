import streamlit as st
import json
import os

st.title("Sistema Bancário")

ARQUIVO = "usuarios.json"

# criar arquivo se não existir
if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump({}, f)

# carregar usuarios
try:
    with open(ARQUIVO, "r") as f:
        usuarios = json.load(f)

except json.JSONDecodeError:
    # se o JSON estiver quebrado, recria o arquivo
    usuarios = {}
    with open(ARQUIVO, "w") as f:
        json.dump(usuarios, f)

# CORRIGE usuarios antigos que tinham só senha
corrigido = False

for u in usuarios:
    if isinstance(usuarios[u], str):
        usuarios[u] = {
            "senha": usuarios[u],
            "saldo": 0
        }
        corrigido = True

if corrigido:
    with open(ARQUIVO, "w") as f:
        json.dump(usuarios, f)
        
# estados
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None


# TELA INICIAL
if st.session_state.pagina == "inicio":
    st.header("Bem-vindo")

    if st.button("Login"):
        st.session_state.pagina = "login"

    if st.button("Criar conta"):
        st.session_state.pagina = "cadastro"


# LOGIN
elif st.session_state.pagina == "login":
    st.header("Login")

    matricula = st.text_input("Matrícula")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if matricula in usuarios and usuarios[matricula]["senha"] == senha:
            st.session_state.usuario_logado = matricula
            st.session_state.pagina = "conta"
            st.rerun()
        else:
            st.error("Matrícula ou senha incorreta")

    if st.button("Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()


# CADASTRO
elif st.session_state.pagina == "cadastro":
    st.header("Criar conta")

    nova_matricula = st.text_input("Crie sua matrícula")
    nova_senha = st.text_input("Crie sua senha", type="password")

    if st.button("Cadastrar"):

        if nova_matricula.lower() == "mestre":
            st.error("Esse usuário é reservado pelo sistema")

        elif nova_matricula in usuarios:
            st.error("Essa matrícula já existe")

        else:
            usuarios[nova_matricula] = {
                "senha": nova_senha,
                "saldo": 0
            }

            with open(ARQUIVO, "w") as f:
                json.dump(usuarios, f)

            st.success("Conta criada!")

    if st.button("Voltar"):
        st.session_state.pagina = "inicio"

# CONTA
usuario = st.session_state.usuario_logado

if usuario is None:
    
    st.stop()

saldo = usuarios[usuario]["saldo"]
# CONTA
usuario = st.session_state.usuario_logado
saldo = usuarios[usuario]["saldo"]

st.header("Sua conta")

st.write("Matrícula:", usuario)

if usuario == "mestre":
    st.write("Saldo: ∞")
else:
    st.write("Saldo: R$", saldo)

st.divider()

# MENU DA CONTA
if usuario == "mestre":
    opcao_conta = st.radio(
        "Escolha uma opção:",
        ["Transferir", "Retirar dinheiro", "Trocar senha"]
    )
else:
    opcao_conta = st.radio(
        "Escolha uma opção:",
        ["Transferir", "Trocar senha"]
    )

# TRANSFERÊNCIA
if opcao_conta == "Transferir":

    destino = st.text_input("Matrícula do destinatário")
    valor = st.number_input("Valor", min_value=0)

    if st.button("Transferir"):
        if destino not in usuarios:
            st.error("Usuário não existe")

        elif destino == usuario:
            st.error("Você não pode transferir para si mesmo")

        else:

            if usuario == "mestre":
                usuarios[destino]["saldo"] += valor

            else:
                if valor > usuarios[usuario]["saldo"]:
                    st.error("Saldo insuficiente")
                    st.stop()

                usuarios[usuario]["saldo"] -= valor
                usuarios[destino]["saldo"] += valor

            with open(ARQUIVO, "w") as f:
                json.dump(usuarios, f)

            st.success("Transferência realizada!")

# RETIRAR DINHEIRO (SÓ MESTRE)
elif opcao_conta == "Retirar dinheiro":

    destino = st.text_input("Usuário que perderá dinheiro")
    valor = st.number_input("Valor para retirar", min_value=0)

    if st.button("Retirar"):

        if destino not in usuarios:
            st.error("Usuário não existe")

        elif destino == "mestre":
            st.error("Não é possível retirar do mestre")

        else:
            if valor > usuarios[destino]["saldo"]:
                usuarios[destino]["saldo"] = 0
            else:
                usuarios[destino]["saldo"] -= valor

            with open(ARQUIVO, "w") as f:
                json.dump(usuarios, f)

            st.success("Dinheiro removido com sucesso!")

# TROCAR SENHA
elif opcao_conta == "Trocar senha":

    nova = st.text_input("Nova senha", type="password")

    if st.button("Alterar senha"):
        usuarios[usuario]["senha"] = nova

        with open(ARQUIVO, "w") as f:
            json.dump(usuarios, f)

        st.success("Senha alterada!")

# SAIR
if st.button("Sair"):
    st.session_state.usuario_logado = None
    st.session_state.pagina = "inicio"
