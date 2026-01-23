import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ProcessoAnalise
# AQUI ESTA A MAGICA: Importamos a nova função do chat que tem a vacina anti-erro
from .services import analisar_processo_com_ia, perguntar_ao_chat_ia
import google.generativeai as genai

def home(request):
    if request.method == 'POST' and request.FILES.get('arquivo_pdf'):
        pdf = request.FILES['arquivo_pdf']
        processo = ProcessoAnalise.objects.create(arquivo_pdf=pdf)
        
        try:
            print("--- 🤖 Iniciando Análise IA ---")
            # Essa função já está blindada no services.py
            resultado_texto = analisar_processo_com_ia(processo.arquivo_pdf.path)
            
            # --- DEBUG: MOSTRA O QUE CHEGOU NO TERMINAL ---
            print(f"📥 RESPOSTA DA IA:\n{resultado_texto[:500]}...") 
            # -----------------------------------------------

            if resultado_texto:
                # Limpeza de segurança para garantir que é JSON
                texto_limpo = resultado_texto.replace('```json', '').replace('```', '')
                
                inicio = texto_limpo.find('{')
                fim = texto_limpo.rfind('}') + 1
                
                if inicio != -1 and fim != -1:
                    json_str = texto_limpo[inicio:fim]
                    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
                    
                    dados = json.loads(json_str)
                    
                    # Salva os dados
                    processo.resumo_ia = dados.get('resumo', '')
                    
                    p_fortes = dados.get('pontos_fortes', '')
                    processo.pontos_fortes = "\n".join(p_fortes) if isinstance(p_fortes, list) else str(p_fortes)

                    processo.sugestao_estrategica = dados.get('estrategia', '')

                    timeline_data = dados.get('timeline', [])
                    processo.timeline = json.dumps(timeline_data, ensure_ascii=False)

                    # Formatação visual dos riscos
                    riscos_raw = dados.get('riscos', '')
                    if isinstance(riscos_raw, dict):
                        html_riscos = ""
                        if 'valor_envolvido' in riscos_raw:
                            html_riscos += f"<div class='mb-3'><strong>💰 Valor:</strong> {riscos_raw['valor_envolvido']}</div>"
                        if 'probabilidade_de_perda' in riscos_raw:
                            prob = riscos_raw['probabilidade_de_perda']
                            cor = "text-rose-600" if "Alta" in prob else "text-orange-500"
                            html_riscos += f"<div class='mb-3'><strong>📉 Risco:</strong> <span class='{cor} font-bold'>{prob}</span></div>"
                        if 'riscos_processuais' in riscos_raw and isinstance(riscos_raw['riscos_processuais'], list):
                            html_riscos += "<div class='mt-4'><strong>⚠️ Pontos Críticos:</strong><ul class='list-disc pl-5 mt-2 space-y-1 text-slate-600'>"
                            for r in riscos_raw['riscos_processuais']:
                                html_riscos += f"<li>{r}</li>"
                            html_riscos += "</ul></div>"
                        processo.pontos_fracos = html_riscos
                    else:
                        processo.pontos_fracos = str(riscos_raw)
                    
                    processo.processado = True 
                    processo.save()
                    print("✅ Sucesso: Dados salvos no banco!")
                else:
                    print("❌ Erro: Chaves {} não encontradas no texto.")
                    raise Exception("IA retornou texto inválido (sem JSON).")

        except Exception as e:
            print(f"❌ ERRO FATAL NA VIEW: {e}")
            processo.resumo_ia = f"Ocorreu um erro ao processar: {str(e)}. Veja o terminal para detalhes."
            processo.processado = True 
            processo.save()

        return redirect('resultado', id=processo.id)
        
    return render(request, 'core/home.html')

def resultado(request, id):
    processo = get_object_or_404(ProcessoAnalise, id=id)
    
    timeline_lista = []
    if processo.timeline:
        try:
            timeline_lista = json.loads(processo.timeline)
        except:
            pass

    return render(request, 'core/result.html', {'processo': processo, 'timeline': timeline_lista})

# --- API CHAT BLINDADA ---
@csrf_exempt
def api_chat_processo(request, id):
    if request.method == 'POST':
        try:
            processo = get_object_or_404(ProcessoAnalise, id=id)
            dados = json.loads(request.body)
            pergunta = dados.get('pergunta')
            
            # Monta o contexto para a IA
            contexto = f"""
            ATUE COMO UM ASSISTENTE JURÍDICO DA DRA. EDUARDA.
            DADOS DO PROCESSO:
            - Resumo: {processo.resumo_ia}
            - Estratégia Adotada: {processo.sugestao_estrategica}
            
            PERGUNTA DO USUÁRIO: "{pergunta}"
            
            Responda de forma direta, profissional e baseada APENAS nos dados acima.
            """
            
            # --- MUDANÇA AQUI: Usamos a função do services.py que tem Retry (Anti-429) ---
            resposta_texto = perguntar_ao_chat_ia(contexto)
            # -----------------------------------------------------------------------------
            
            return JsonResponse({'resposta': resposta_texto})
            
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)
            
    return JsonResponse({'erro': 'Método inválido'}, status=400)