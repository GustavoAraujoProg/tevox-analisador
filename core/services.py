import google.generativeai as genai
import os
import time
from google.api_core import exceptions

# --- CONFIGURAÇÃO INICIAL ---
MINHA_CHAVE_API = os.getenv('GOOGLE_API_KEY')

if MINHA_CHAVE_API:
    genai.configure(api_key=MINHA_CHAVE_API)
else:
    print("🚨 ERRO: Chave API não encontrada nas variáveis de ambiente!")

# --- A VACINA ANTI-ERRO 429 (RETRY LOGIC) ---
def gerar_resposta_com_retry(model, conteudo, tentativas=3):
    """
    Tenta falar com o Google. Se der erro de limite (429), espera e tenta de novo.
    """
    for i in range(tentativas):
        try:
            # Tenta gerar a resposta
            return model.generate_content(conteudo)
        
        except exceptions.ResourceExhausted:
            # Se cair aqui, é porque o limite estourou. Vamos esperar.
            tempo_espera = 10 * (i + 1) # Espera 10s, depois 20s, depois 30s...
            print(f"⚠️ Limite do Google atingido (429). Esperando {tempo_espera} segundos para tentar de novo...")
            time.sleep(tempo_espera)
            continue # Volta para o início do loop e tenta de novo
            
        except Exception as e:
            # Outros erros a gente não trata com espera
            print(f"❌ Erro inesperado na IA: {str(e)}")
            return None

    return None # Se falhar todas as vezes

# --- FUNÇÃO DO PDF (JÁ USANDO A VACINA) ---
def analisar_processo_com_ia(caminho_pdf):
    try:
        generation_config = {
            "temperature": 0.4,
            "response_mime_type": "application/json"
        }

        model = genai.GenerativeModel('gemini-2.0-flash', generation_config=generation_config)
        
        print(f"📤 Enviando PDF para o Google (Modo Seguro)...")
        sample_file = genai.upload_file(path=caminho_pdf, display_name="Processo Juridico")
        
        prompt = """
        Atue como um Especialista Jurídico Sênior. 
        Analise o PDF e retorne um JSON rico e detalhado com:
        {
            "resumo": "História completa e cronológica dos fatos...",
            "pontos_fortes": ["Argumento 1", "Argumento 2"],
            "riscos": {
                "valor_envolvido": "R$ Valor",
                "probabilidade_de_perda": "Alta/Média/Baixa",
                "riscos_processuais": ["Risco 1"]
            },
            "estrategia": "Tese de defesa detalhada...",
            "timeline": [{"data": "DD/MM/AAAA", "evento": "Evento", "descricao": "Detalhe"}]
        }
        """

        # AQUI CHAMAMOS A VACINA EM VEZ DE CHAMAR DIRETO
        response = gerar_resposta_com_retry(model, [sample_file, prompt])
        
        if response:
            return response.text
        else:
            return '{"resumo": "O Google está sobrecarregado no momento. Tente em 1 minuto.", "timeline": []}'

    except Exception as e:
        print(f"❌ Erro Geral: {str(e)}")
        return '{"resumo": "Erro técnico.", "timeline": []}'

# --- NOVA FUNÇÃO PARA O CHAT (USE ESSA NO SEU VIEWS.PY) ---
def perguntar_ao_chat_ia(historico):
    """
    Função específica para o Chat, também protegida contra travamentos.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Chama a vacina passando o histórico da conversa
        response = gerar_resposta_com_retry(model, historico)
        
        if response:
            return response.text
        else:
            return "O sistema está com alto tráfego. Aguarde alguns segundos e pergunte novamente."
            
    except Exception as e:
        return f"Erro no chat: {str(e)}"