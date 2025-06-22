<!-- 
  Tags: DadosIA
  Label: Extraindo legenda do youTube
  Description: Extraindo legenda do youTube usando pynthon 
  path_hook: hookfigma.hook3
-->

# YouTube Transcript Downloader

Um downloader robusto e profissional de transcrições do YouTube com múltiplas estratégias de fallback e processamento em lote.

## 🚀 Características

- **Múltiplas estratégias de download**: Utiliza tanto `youtube-transcript-api` quanto `yt-dlp` para máxima compatibilidade
- **Processamento em lote**: Processa múltiplas URLs a partir de um arquivo de texto
- **Suporte multilíngue**: Prioriza português, mas funciona com qualquer idioma disponível
- **Tradução automática**: Traduz transcrições quando necessário
- **Limpeza inteligente**: Processa e limpa automaticamente os arquivos de legenda
- **Relatórios detalhados**: Fornece feedback completo sobre o processo de download
- **Controle de taxa**: Implementa delays entre downloads para evitar rate limiting

## 📋 Pré-requisitos

- Python 3.7+
- Conexão com a internet
- yt-dlp instalado no sistema (para estratégia de fallback)

## 🔧 Instalação

1. Clone ou baixe o arquivo `youtube_transcript_downloader.py`

2. Instale as dependências necessárias:
```bash
pip install yt-dlp youtube-transcript-api requests beautifulsoup4
```

3. Certifique-se de que o `yt-dlp` está instalado globalmente:
```bash
# Via pip
pip install yt-dlp

# Via conda
conda install -c conda-forge yt-dlp

# Via winget (Windows)
winget install yt-dlp

# Via homebrew (macOS)
brew install yt-dlp
```

## 📝 Uso

### Processamento em Lote

1. Crie um arquivo `urls.txt` no mesmo diretório do script
2. Adicione uma URL do YouTube por linha:
```
https://www.youtube.com/watch?v=VIDEO_ID1
https://youtu.be/VIDEO_ID2
https://www.youtube.com/watch?v=VIDEO_ID3
# Comentários são ignorados
```

3. Execute o script:
```bash
python youtube_transcript_downloader.py
```

### Uso Programático

```python
from youtube_transcript_downloader import YouTubeTranscriptDownloader

# Criar instância
downloader = YouTubeTranscriptDownloader(
    output_dir="transcricoes",  # Diretório de saída
    delay=5                     # Delay entre downloads (segundos)
)

# Download de vídeo único
transcript = downloader.download_single_video("https://www.youtube.com/watch?v=VIDEO_ID")

# Processamento em lote
resultados = downloader.process_urls_from_file("urls.txt")
```

## 📁 Estrutura de Saída

O script cria uma pasta `transcricoes/` com os seguintes arquivos:

```
transcricoes/
├── transcricao_VIDEO_ID1.txt
├── transcricao_VIDEO_ID2.txt
└── titulo_video_[VIDEO_ID3].vtt
```

## 🔄 Estratégias de Download

O downloader utiliza uma abordagem em cascata:

### 1. YouTube Transcript API
- **Prioridade**: Idiomas em português (pt, pt-BR)
- **Fallback**: Inglês (en, en-US)
- **Tradução**: Automática quando disponível
- **Tipos**: Transcrições manuais e automáticas

### 2. yt-dlp
- **Legendas**: Baixa arquivos VTT/SRT
- **Idiomas**: pt, pt-BR
- **Processamento**: Converte para texto limpo
- **Compatibilidade**: Funciona com vídeos que bloqueiam a API

## 📊 Relatórios

O script fornece relatórios detalhados incluindo:

- Status de cada download
- Estatísticas de sucesso/falha
- Tamanho das transcrições
- Preview do conteúdo
- Tempo total de processamento

### Exemplo de Saída:
```
🎯 YOUTUBE TRANSCRIPT DOWNLOADER APRIMORADO
==================================================
📂 Carregadas 3 URLs do arquivo 'urls.txt'
🚀 Iniciando processamento de 3 URLs

🎬 PROCESSANDO 1/3
--------------------------------------------------
🎯 Processando vídeo ID: dQw4w9WgXcQ
📋 Listando transcrições disponíveis...
   📄 Disponível: en (Auto)
✅ Transcrição encontrada em en
💾 Transcrição salva em: transcricoes/transcricao_dQw4w9WgXcQ.txt
📊 Tamanho: 1247 caracteres
✅ SUCESSO!

======================================================================
📊 RESUMO FINAL
======================================================================
Total processado: 3
Sucessos: 2
Falhas: 1
Taxa de sucesso: 66.7%
```

## ⚙️ Configuração

### Parâmetros do Constructor

```python
YouTubeTranscriptDownloader(
    output_dir="transcricoes",  # Diretório de saída
    delay=5                     # Delay entre downloads em segundos
)
```

### Formatos Suportados

- **URLs**: `youtube.com/watch?v=`, `youtu.be/`, `youtube.com/embed/`
- **Legendas**: VTT, SRT
- **Idiomas**: Todos os idiomas suportados pelo YouTube
- **Codificação**: UTF-8

## 🛠️ Tratamento de Erros

O script trata automaticamente:

- **Vídeos privados/removidos**: Reporta erro específico
- **Transcrições desabilitadas**: Tenta yt-dlp como fallback
- **Rate limiting**: Implementa delays configuráveis
- **Timeout**: Limites de tempo para evitar travamentos
- **Caracteres especiais**: Limpeza automática de nomes de arquivo

## 🔍 Troubleshooting

### Erro: "No transcript found"
- O vídeo pode não ter legendas/transcrições
- Tente executar novamente após alguns minutos
- Verifique se o vídeo está público

### Erro: "yt-dlp not found"
```bash
# Instale yt-dlp
pip install yt-dlp
# ou adicione ao PATH do sistema
```

### Erro: "Permission denied"
- Verifique permissões da pasta de saída
- Execute como administrador se necessário

### Rate Limiting
- Aumente o valor do `delay`
- Use proxy se necessário (implementação disponível)

## 📄 Formatos de Arquivo URLs

O arquivo `urls.txt` suporta:

```
# Comentários começam com #
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ

# URLs com parâmetros adicionais também funcionam
https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s

# Linhas vazias são ignoradas

https://www.youtube.com/embed/dQw4w9WgXcQ
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Downloader principal
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - API de transcrições
- Comunidade Python pelo suporte contínuo

---

**Nota**: Este software é destinado apenas para uso educacional e pessoal. Respeite os termos de serviço do YouTube e os direitos autorais dos criadores de conteúdo.

## 👨‍💻 Autor

[Fabiano Rocha/Fabiuniz](https://github.com/SeuUsuarioGitHub)

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
