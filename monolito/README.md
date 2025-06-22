<!-- 
  Tags: DadosIA
  Label: ⬇️ Extraindo legenda do youTube
  Description: Extraindo legenda do youTube usando pynthon 
  path_hook: hookfigma.hook3
-->

# 🎯 YouTube Transcript Downloader

Um poderoso downloader de transcrições do YouTube com interface web e linha de comando, desenvolvido em Python e HTML/JavaScript. Este projeto oferece múltiplas estratégias para baixar transcrições de vídeos do YouTube, incluindo legendas automáticas e manuais.

## ✨ Características

### 🚀 Funcionalidades Principais
- **Múltiplas Estratégias**: Utiliza `youtube-transcript-api` e `yt-dlp` para máxima compatibilidade
- **Interface Web**: Interface moderna e responsiva para uso fácil
- **Linha de Comando**: Script Python para automação e processamento em lote
- **Processamento em Lote**: Suporte para múltiplas URLs simultâneas
- **Idiomas Múltiplos**: Suporte para português, inglês e outros idiomas
- **Tradução Automática**: Traduz transcrições quando disponível
- **Fallback Inteligente**: Se uma estratégia falha, tenta automaticamente a próxima
- **Logs Detalhados**: Sistema completo de logging para acompanhar o progresso
- **Export Flexível**: Salva transcrições em arquivos .txt organizados

### 🌐 Interface Web
- **Design Moderno**: Interface responsiva com gradientes e animações
- **Três Modos de Uso**:
  - Vídeo único
  - Múltiplos vídeos (inserção manual)
  - Upload de arquivo .txt
- **Progresso em Tempo Real**: Barra de progresso e logs ao vivo
- **Estatísticas Completas**: Resumo detalhado dos resultados
- **Download Individual**: Baixe cada transcrição separadamente

## 📦 Instalação

### Pré-requisitos
- Python 3.7+
- pip (gerenciador de pacotes Python)
- yt-dlp (instalado automaticamente)

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/youtube-transcript-downloader.git
cd youtube-transcript-downloader
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Instale o yt-dlp (se não instalado)
```bash
pip install yt-dlp
```

### Arquivo requirements.txt
```txt
yt-dlp>=2023.12.30
youtube-transcript-api>=0.6.2
requests>=2.31.0
beautifulsoup4>=4.12.2
pathlib
```

## 🚀 Como Usar

### 🖥️ Interface Web

1. **Abra o arquivo HTML**:
   ```bash
   # Abra o arquivo youtube_transcript_web.html no seu navegador
   # Ou use um servidor local:
   python -m http.server 8000
   # Depois acesse: http://localhost:8000
   ```

2. **Escolha o modo de uso**:
   - **Vídeo Único**: Cole a URL de um vídeo
   - **Múltiplos Vídeos**: Cole várias URLs (uma por linha)
   - **Upload de Arquivo**: Envie um arquivo .txt com URLs

3. **Clique em "Baixar Transcrições"** e acompanhe o progresso

### 🐍 Linha de Comando

#### Uso Básico
```bash
python youtube_transcript_downloader.py
```

#### Processamento de Arquivo
1. Crie um arquivo `urls.txt` com as URLs:
```txt
https://www.youtube.com/watch?v=VIDEO_ID1
https://youtu.be/VIDEO_ID2
# Comentários começam com #
https://www.youtube.com/watch?v=VIDEO_ID3
```

2. Execute o script:
```bash
python youtube_transcript_downloader.py
```

#### Configuração Personalizada
```python
from youtube_transcript_downloader import YouTubeTranscriptDownloader

# Configuração personalizada
downloader = YouTubeTranscriptDownloader(
    output_dir="minhas_transcricoes",  # Pasta de saída
    delay=3  # Delay entre downloads (segundos)
)

# Download de vídeo único
transcript = downloader.download_single_video("https://www.youtube.com/watch?v=VIDEO_ID")

# Processamento de arquivo
results = downloader.process_urls_from_file("minhas_urls.txt")
```

## 📁 Estrutura do Projeto

```
youtube-transcript-downloader/
│
├── youtube_transcript_downloader.py    # Script principal Python
├── youtube_transcript_web.html         # Interface web
├── requirements.txt                    # Dependências Python
├── README.md                          # Este arquivo
├── urls.txt                           # Arquivo de URLs (exemplo)
│
├── transcricoes/                      # Pasta de saída (criada automaticamente)
│   ├── transcricao_VIDEO_ID1.txt
│   ├── transcricao_VIDEO_ID2.txt
│   └── ...
│
└── docs/                             # Documentação adicional
    ├── examples.md                   # Exemplos de uso
    └── troubleshooting.md           # Solução de problemas
```

## 🔧 Configuração Avançada

### Configuração de Proxy
```python
# Para usar com proxy
downloader = YouTubeTranscriptDownloader()
transcript = downloader.download_transcript_api(
    video_id, 
    proxy="http://proxy:8080"
)
```

### Personalização de Idiomas
```python
# Modificar ordem de preferência de idiomas
# No arquivo youtube_transcript_downloader.py, linha ~180:
idiomas_preferidos = ['pt-BR', 'pt', 'en-US', 'en', 'es', 'fr']
```

### Configuração de Timeout
```python
# Modificar timeout para vídeos longos
# No método download_with_ytdlp, linha ~80:
result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # 2 minutos
```

## 📊 Formatos Suportados

### URLs Aceitas
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://youtube.com/watch?v=VIDEO_ID`

### Tipos de Transcrição
- **Legendas Automáticas**: Geradas pelo YouTube
- **Legendas Manuais**: Criadas pelo autor do vídeo
- **Legendas da Comunidade**: Criadas por usuários
- **Traduções**: Transcrições traduzidas automaticamente

### Idiomas Suportados
- Português (pt, pt-BR) - **Prioridade**
- Inglês (en, en-US)
- Espanhol (es)
- Francês (fr)
- Alemão (de)
- E muitos outros...

## 🎯 Exemplos de Uso

### Exemplo 1: Download Simples
```python
from youtube_transcript_downloader import YouTubeTranscriptDownloader

downloader = YouTubeTranscriptDownloader()
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
transcript = downloader.download_single_video(url)

if transcript:
    print(f"Transcrição baixada com sucesso!")
    print(f"Primeiros 100 caracteres: {transcript[:100]}...")
```

### Exemplo 2: Processamento em Lote
```python
urls = [
    "https://www.youtube.com/watch?v=VIDEO1",
    "https://www.youtube.com/watch?v=VIDEO2",
    "https://youtu.be/VIDEO3"
]

# Salva URLs em arquivo
with open("meus_videos.txt", "w") as f:
    f.write("\n".join(urls))

# Processa arquivo
downloader = YouTubeTranscriptDownloader(delay=2)
results = downloader.process_urls_from_file("meus_videos.txt")

# Exibe estatísticas
successful = sum(1 for _, success, _ in results if success)
print(f"Sucessos: {successful}/{len(results)}")
```

### Exemplo 3: Integração com Pandas
```python
import pandas as pd
from youtube_transcript_downloader import YouTubeTranscriptDownloader

# DataFrame com URLs
df = pd.DataFrame({
    'title': ['Vídeo 1', 'Vídeo 2', 'Vídeo 3'],
    'url': [
        'https://www.youtube.com/watch?v=ID1',
        'https://www.youtube.com/watch?v=ID2',
        'https://www.youtube.com/watch?v=ID3'
    ]
})

downloader = YouTubeTranscriptDownloader()

# Adiciona coluna de transcrição
df['transcript'] = df['url'].apply(downloader.download_single_video)
df['has_transcript'] = df['transcript'].notna()

# Salva resultados
df.to_csv('resultados_transcricoes.csv', index=False)
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. "Nenhuma transcrição encontrada"
```bash
❌ Nenhuma transcrição encontrada para este vídeo
```
**Soluções**:
- Verifique se o vídeo tem legendas habilitadas
- Tente com um vídeo diferente
- O vídeo pode estar em um idioma não suportado

#### 2. "yt-dlp não encontrado"
```bash
❌ Erro no yt-dlp: comando não encontrado
```
**Soluções**:
```bash
pip install yt-dlp
# ou
pip install --upgrade yt-dlp
```

#### 3. "Timeout" em vídeos longos
```bash
❌ yt-dlp timeout
```
**Soluções**:
- Aumente o timeout no código
- Verifique sua conexão com a internet
- Tente novamente mais tarde

#### 4. Erro de codificação de caracteres
```bash
❌ Erro ao salvar arquivo: 'charmap' codec can't encode
```
**Soluções**:
- O código já trata UTF-8, mas verifique se seu sistema suporta
- Use Python 3.7+ para melhor suporte a Unicode

### Logs Detalhados

Para debug avançado, modifique o código para logging detalhado:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Adicione logs personalizados onde necessário
logging.debug(f"Tentando baixar: {video_id}")
```

## 🤝 Contribuindo

### Como Contribuir
1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/nova-feature`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. **Push** para a branch (`git push origin feature/nova-feature`)
5. Abra um **Pull Request**

### Diretrizes de Contribuição
- Mantenha o código limpo e documentado
- Adicione testes para novas funcionalidades
- Siga as convenções de nomenclatura Python (PEP 8)
- Atualize a documentação quando necessário

### Relatando Bugs
Use o template de issue do GitHub:
```markdown
**Descrição do Bug**
Descrição clara do problema

**Para Reproduzir**
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer

**Screenshots**
Se aplicável, adicione screenshots

**Ambiente**
- OS: [Windows/Mac/Linux]
- Python: [versão]
- Navegador: [se usando interface web]
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2024 YouTube Transcript Downloader

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Agradecimentos

- **youtube-transcript-api** - API principal para download de transcrições
- **yt-dlp** - Ferramenta robusta para download de mídia do YouTube
- **Beautiful Soup** - Parsing HTML para processamento de legendas
- **Requests** - Biblioteca HTTP para Python

## 📞 Suporte

### Documentação Adicional
- [Exemplos Avançados](docs/examples.md)
- [Guia de Troubleshooting](docs/troubleshooting.md)
- [API Reference](docs/api.md)

### Contato
- **Issues**: Use o sistema de issues do GitHub
- **Discussões**: Use o tab "Discussions" do GitHub
- **Email**: [seu-email@exemplo.com]

### Status do Projeto
![Manutenção](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![Versão](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Licença](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)

---

## 📈 Roadmap

### Versão 1.1.0
- [ ] Suporte para playlists completas
- [ ] Download de metadados dos vídeos
- [ ] Export para formatos CSV/JSON
- [ ] Interface web com temas escuro/claro

### Versão 1.2.0
- [ ] API REST para integração
- [ ] Suporte para outros sites de vídeo
- [ ] Processamento paralelo para maior velocidade
- [ ] Sistema de cache para evitar re-downloads

### Versão 2.0.0
- [ ] Interface desktop com Tkinter/PyQt
- [ ] Suporte para legendas com timestamps
- [ ] Análise de sentimento das transcrições
- [ ] Integração com serviços de IA para resumos

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!**

*Última atualização: Dezembro 2024*

## 👨‍💻 Autor

[Fabiano Rocha/Fabiuniz](https://github.com/SeuUsuarioGitHub)

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
