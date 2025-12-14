# 🚀 Como Usar o RAG Contratos

## 🌐 Opção 1: Interface Web (RECOMENDADO)

### No seu PC (Local)

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure a API Key:**
```bash
# Crie um arquivo .env
echo "ANTHROPIC_API_KEY=sua_chave_aqui" > .env
```

3. **Inicie a aplicação:**
```bash
streamlit run app.py
```

4. **Abra no navegador:**
   - Automaticamente abre em: `http://localhost:8501`
   - Se não abrir, copie e cole o link no navegador

5. **Use a interface:**
   - 📤 Upload de PDFs
   - 🔍 Busca semântica
   - 📊 Exportar CSV/JSON
   - 📈 Análise e comparação

---

## ☁️ Opção 2: Hospedar Online (Grátis)

### Streamlit Cloud (Mais Fácil)

1. **Faça fork/clone do repositório no GitHub**

2. **Acesse:** https://streamlit.io/cloud

3. **Clique em "New app"**

4. **Configure:**
   - Repository: seu repositório
   - Branch: main
   - Main file path: `app.py`

5. **Adicione a API Key nos Secrets:**
   - Settings → Secrets
   - Adicione:
   ```toml
   ANTHROPIC_API_KEY = "sua_chave_aqui"
   ```

6. **Deploy!** ✅
   - Você receberá uma URL pública
   - Ex: `https://seu-app.streamlit.app`

### Render.com (Alternativa)

1. **Crie conta em:** https://render.com

2. **Novo Web Service:**
   - Conecte seu repositório GitHub
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

3. **Adicione variável de ambiente:**
   - `ANTHROPIC_API_KEY` = sua chave

4. **Deploy!** ✅

### Hugging Face Spaces (Alternativa)

1. **Acesse:** https://huggingface.co/spaces

2. **Crie novo Space:**
   - SDK: Streamlit
   - Upload o código

3. **Adicione Secret:**
   - Settings → Repository secrets
   - `ANTHROPIC_API_KEY` = sua chave

4. **Deploy!** ✅

---

## 💻 Opção 3: Linha de Comando (Python)

### Uso Interativo

```bash
python pipeline_contratos.py
```

Você verá um menu:
```
1. Processar todos os contratos
2. Processar contrato específico
3. Exportar para CSV
4. Busca semântica (interativa)
5. Demo de busca
6. Listar contratos
7. Gerar resumo
0. Sair
```

### Uso Programático

```python
from pipeline_contratos import ContractPipeline

# Inicializar
pipeline = ContractPipeline()

# Processar PDF
result = pipeline.process_single_contract("contratos/meu_contrato.pdf")

# Buscar
answer = pipeline.search.ask_question("Qual é a renda mensal?")
print(answer)

# Exportar
pipeline.export_to_csv()
```

---

## 📋 Comparação das Opções

| Opção | Dificuldade | Vantagens | Melhor para |
|-------|-------------|-----------|-------------|
| **Interface Web Local** | ⭐ Fácil | Interface bonita, fácil de usar | Uso pessoal no PC |
| **Streamlit Cloud** | ⭐ Muito Fácil | Online grátis, compartilhável | Compartilhar com equipe |
| **Render/HF** | ⭐⭐ Médio | Mais controle | Uso profissional |
| **Linha de Comando** | ⭐⭐⭐ Difícil | Automação, scripts | Desenvolvedores |

---

## 🎯 Recomendação

### Para você usar sozinho:
```bash
streamlit run app.py
```
✅ Simples, rápido, interface bonita

### Para compartilhar com outros:
👉 **Streamlit Cloud** (grátis e fácil)

### Para produção/empresa:
👉 **Render.com** ou servidor próprio

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "API Key não configurada"
1. Crie arquivo `.env`
2. Adicione: `ANTHROPIC_API_KEY=sua_chave`

### "Porta em uso" (Streamlit)
```bash
streamlit run app.py --server.port 8502
```

### "PDF não processa"
- Verifique se o PDF não está protegido/criptografado
- Tente converter para PDF não protegido

---

## 📱 Acesso Remoto

### Opção A: ngrok (para testar remotamente)

1. **Instale ngrok:** https://ngrok.com/download

2. **Execute o Streamlit:**
```bash
streamlit run app.py
```

3. **Em outro terminal:**
```bash
ngrok http 8501
```

4. **Use a URL fornecida** (ex: `https://abc123.ngrok.io`)
   - Funciona em qualquer lugar!
   - Temporário (fecha quando você para)

### Opção B: Tailscale (VPN)

1. **Instale Tailscale** no seu PC
2. **Execute o Streamlit** normalmente
3. **Acesse de qualquer dispositivo** na mesma rede Tailscale

---

## 🎬 Vídeo Tutorial (Passos)

### 1️⃣ Instalação
```bash
git clone <seu-repositorio>
cd rag_contratos
pip install -r requirements.txt
```

### 2️⃣ Configuração
```bash
# Criar .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### 3️⃣ Executar
```bash
streamlit run app.py
```

### 4️⃣ Usar
1. Abra `http://localhost:8501`
2. Configure API Key na barra lateral
3. Clique "Inicializar Sistema"
4. Upload de PDF na aba "Upload & Processar"
5. Faça perguntas na aba "Busca Semântica"
6. Exporte dados na aba "Exportar Dados"

---

## 💡 Dicas

1. **Primeira vez?** Use a interface web (Streamlit)
2. **Quer compartilhar?** Deploy no Streamlit Cloud
3. **Quer automatizar?** Use o pipeline Python
4. **Problemas?** Veja a documentação completa em `PIPELINE_USAGE.md`

---

## 🔗 Links Úteis

- 📚 [Documentação Completa](PIPELINE_USAGE.md)
- 🚀 [Guia Rápido](QUICK_START.md)
- 🌐 [Streamlit Cloud](https://streamlit.io/cloud)
- 🤖 [Claude API](https://console.anthropic.com/)

---

## ✅ Checklist Rápido

- [ ] Instalei as dependências
- [ ] Configurei a API Key
- [ ] Executei `streamlit run app.py`
- [ ] Abri no navegador
- [ ] Fiz upload de um PDF
- [ ] Testei uma busca
- [ ] Exportei dados

**Se todos os itens estão ✅, você está pronto!** 🎉
