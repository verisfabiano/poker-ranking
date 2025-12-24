from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import markdown2
from pathlib import Path
import os


@login_required
def documentacao_ranking(request):
    """Exibe a documentação do sistema de ranking em HTML"""
    
    # Encontrar o arquivo markdown na raiz do projeto
    base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    doc_path = base_path / 'COMO_FUNCIONA_RANKING.md'
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Converter markdown para HTML
        html_content = markdown2.markdown(markdown_content, extras=['tables', 'fenced-code-blocks'])
    except FileNotFoundError:
        html_content = "<p>Documentação não encontrada.</p>"
    
    return render(request, 'documentacao_ranking.html', {
        'conteudo': html_content
    })
