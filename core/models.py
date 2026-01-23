from django.db import models
import uuid

class ProcessoAnalise(models.Model):
    # Usar UUID deixa o link mais seguro e profissional (não fica id=1, id=2)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # O arquivo PDF
    arquivo_pdf = models.FileField(upload_to='processos_pdfs/')
    
    # Dados de controle
    data_upload = models.DateTimeField(auto_now_add=True)
    processado = models.BooleanField(default=False) # Para saber se a IA já terminou
    
    # Onde vamos guardar o que a IA leu (O "Ouro")
    # TextField aguenta textos gigantes
    resumo_ia = models.TextField(blank=True, null=True, verbose_name="Resumo Geral")
    pontos_fortes = models.TextField(blank=True, null=True)
    pontos_fracos = models.TextField(blank=True, null=True)
    sugestao_estrategica = models.TextField(blank=True, null=True)
    timeline = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Processo {str(self.id)[:8]} - {self.data_upload.strftime('%d/%m/%Y')}"

    class Meta:
        ordering = ['-data_upload'] # Mostra sempre o mais recente primeiro