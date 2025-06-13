# pip install yt-dlp youtube-transcript-api requests beautifulsoup4
import subprocess
import os
import re
import time
import json
import requests
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
import xml.etree.ElementTree as ET

class YouTubeTranscriptDownloader:
    def __init__(self, output_dir: str = "transcricoes", delay: int = 5):
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrai o ID do vídeo de uma URL do YouTube."""
        if not url:
            return None
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

    def clean_filename(self, filename: str) -> str:
        """Remove caracteres inválidos do nome do arquivo."""
        # Remove caracteres especiais e substitui por underscore
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[^\w\s-]', '_', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        return filename.strip('_')

    def download_with_ytdlp(self, url: str, video_id: str) -> Optional[str]:
        """Baixa legendas usando yt-dlp como fallback."""
        print(f"🔄 Tentando yt-dlp para: {video_id}")
        
        try:
            # Primeiro tenta obter informações do vídeo
            info_cmd = [
                'yt-dlp', '--dump-json', '--no-download', url
            ]
            
            result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                title = self.clean_filename(video_info.get('title', video_id))
            else:
                title = video_id
                
            # Tenta baixar legendas em português
            for lang in ['pt', 'pt-BR']:
                output_template = str(self.output_dir / f"{title}_[{video_id}].%(ext)s")
                cmd = [
                    'yt-dlp',
                    '--write-auto-sub',
                    '--write-sub',
                    '--sub-lang', lang,
                    '--skip-download',
                    '--output', output_template,
                    url
                ]
                
                print(f"   Tentando idioma {lang} com yt-dlp...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Procura pelo arquivo de legenda gerado
                    for ext in ['.vtt', '.srt']:
                        subtitle_file = self.output_dir / f"{title}_[{video_id}].{lang}{ext}"
                        if subtitle_file.exists():
                            print(f"✅ Arquivo de legenda encontrado: {subtitle_file}")
                            return self.parse_subtitle_file(subtitle_file)
                    
                    # Se não encontrou com nome específico, procura por qualquer arquivo com o video_id
                    for file in self.output_dir.glob(f"*{video_id}*"):
                        if file.suffix in ['.vtt', '.srt']:
                            print(f"✅ Arquivo de legenda encontrado: {file}")
                            return self.parse_subtitle_file(file)
            
            print("❌ yt-dlp não conseguiu baixar legendas")
            return None
            
        except subprocess.TimeoutExpired:
            print("❌ yt-dlp timeout")
            return None
        except Exception as e:
            print(f"❌ Erro no yt-dlp: {str(e)[:100]}...")
            return None

    def parse_subtitle_file(self, file_path: Path) -> Optional[str]:
        """Converte arquivo de legenda (VTT/SRT) para texto limpo."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.suffix == '.vtt':
                return self.parse_vtt(content)
            elif file_path.suffix == '.srt':
                return self.parse_srt(content)
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo de legenda: {e}")
            return None

    def parse_vtt(self, content: str) -> str:
        """Converte conteúdo VTT para texto limpo."""
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Pula linhas vazias, headers e timestamps
            if not line or line.startswith('WEBVTT') or '-->' in line or line.startswith('NOTE'):
                continue
            # Pula números de sequência
            if line.isdigit():
                continue
            
            # Remove tags HTML/XML
            line = re.sub(r'<[^>]*>', '', line)
            if line:
                text_lines.append(line)
        
        return ' '.join(text_lines)

    def parse_srt(self, content: str) -> str:
        """Converte conteúdo SRT para texto limpo."""
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Pula linhas vazias, números e timestamps
            if not line or line.isdigit() or '-->' in line:
                continue
            
            # Remove tags HTML/XML
            line = re.sub(r'<[^>]*>', '', line)
            if line:
                text_lines.append(line)
        
        return ' '.join(text_lines)

    def download_transcript_api(self, video_id: str, proxy: Optional[str] = None) -> Optional[str]:
        """Baixa transcrição usando youtube-transcript-api."""
        print(f"🎯 Processando vídeo ID: {video_id}")
        
        proxies = None
        if proxy:
            proxies = {"http": proxy, "https": proxy}
        
        try:
            print("📋 Listando transcrições disponíveis...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
            
            transcripts_info = []
            for transcript in transcript_list:
                lang = transcript.language_code
                is_auto = transcript.is_generated
                tipo = "Auto" if is_auto else "Manual"
                transcripts_info.append(f"{lang} ({tipo})")
                print(f"   📄 Disponível: {lang} ({tipo})")
            
            if not transcripts_info:
                print("❌ Nenhuma transcrição encontrada")
                return None
            
            # Estratégia 1: Tentar idiomas preferidos diretamente
            idiomas_preferidos = ['pt', 'pt-BR', 'en', 'en-US']
            
            for idioma in idiomas_preferidos:
                try:
                    print(f"   Tentando idioma: {idioma}")
                    transcript_data = YouTubeTranscriptApi.get_transcript(
                        video_id, 
                        languages=[idioma], 
                        proxies=proxies
                    )
                    if transcript_data:
                        print(f"✅ Transcrição encontrada em {idioma}")
                        return self.process_transcript_data(transcript_data)
                except Exception as e:
                    print(f"   ❌ Falhou para {idioma}: {str(e)[:100]}...")
                    continue
            
            # Estratégia 2: Tentar cada transcrição disponível
            for transcript in transcript_list:
                lang = transcript.language_code
                try:
                    print(f"🔄 Tentando transcrição em {lang}...")
                    transcript_data = transcript.fetch()
                    if transcript_data:
                        print(f"✅ Sucesso! Transcrição obtida em {lang}")
                        return self.process_transcript_data(transcript_data)
                except Exception as e:
                    print(f"   ❌ Erro ao baixar {lang}: {str(e)[:100]}...")
                    
                    # Estratégia 3: Tentar tradução se disponível
                    if hasattr(transcript, 'is_translatable') and transcript.is_translatable:
                        for target_lang in ['pt', 'en']:
                            try:
                                print(f"   🔄 Tentando traduzir {lang} para {target_lang}...")
                                translated_transcript = transcript.translate(target_lang)
                                transcript_data = translated_transcript.fetch()
                                if transcript_data:
                                    print(f"✅ Sucesso! Transcrição traduzida para {target_lang}")
                                    return self.process_transcript_data(transcript_data)
                            except Exception as te:
                                print(f"   ❌ Falha ao traduzir {lang} para {target_lang}: {str(te)[:50]}...")
                    continue
            
            print("❌ Todas as estratégias da API falharam")
            return None
        
        except NoTranscriptFound:
            print("❌ Nenhuma transcrição encontrada para este vídeo")
            return None
        except TranscriptsDisabled:
            print("❌ Transcrições desabilitadas pelo criador do vídeo")
            return None
        except VideoUnavailable:
            print("❌ Vídeo não disponível (privado, removido ou restrito)")
            return None
        except Exception as e:
            print(f"❌ Erro inesperado: {type(e).__name__} - {str(e)[:100]}...")
            return None

    def process_transcript_data(self, transcript_data: List[Dict]) -> str:
        """Processa os dados da transcrição em texto limpo."""
        if not transcript_data:
            return ""
        
        texto_completo = []
        
        for entry in transcript_data:
            if isinstance(entry, dict) and 'text' in entry:
                texto = entry['text'].strip()
                if texto:
                    texto = re.sub(r'[\n\r\t]+', ' ', texto)
                    texto = re.sub(r'\s+', ' ', texto)
                    texto_completo.append(texto)
        
        resultado = ' '.join(texto_completo).strip()
        return resultado

    def save_transcript(self, text: str, output_file: Path) -> bool:
        """Salva a transcrição em arquivo."""
        if not text:
            print("❌ Transcrição vazia, não salvando")
            return False
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"💾 Transcrição salva em: {output_file}")
            print(f"📊 Tamanho: {len(text)} caracteres")
            print(f"📝 Preview: {text[:200]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return False

    def download_single_video(self, url: str) -> Optional[str]:
        """Baixa transcrição de um único vídeo usando múltiplas estratégias."""
        if not url:
            print("❌ URL não fornecida")
            return None
        
        video_id = self.extract_video_id(url)
        if not video_id:
            print(f"❌ Não foi possível extrair ID do vídeo de: {url}")
            return None
        
        output_file = self.output_dir / f"transcricao_{video_id}.txt"
        
        # Estratégia 1: Tentar youtube-transcript-api
        print("🔄 Método 1: Usando youtube-transcript-api")
        transcript = self.download_transcript_api(video_id)
        
        if transcript:
            if self.save_transcript(transcript, output_file):
                return transcript
        
        # Estratégia 2: Tentar yt-dlp
        print("🔄 Método 2: Usando yt-dlp")
        transcript = self.download_with_ytdlp(url, video_id)
        
        if transcript:
            if self.save_transcript(transcript, output_file):
                return transcript
        
        print("❌ Todas as estratégias falharam para este vídeo")
        return None

    def load_urls_from_file(self, filename: str = "urls.txt") -> List[str]:
        """Carrega URLs de um arquivo de texto."""
        urls = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for linha_num, linha in enumerate(f, 1):
                    linha = linha.strip()
                    
                    if not linha or linha.startswith('#'):
                        continue
                    
                    if 'youtube.com' in linha or 'youtu.be' in linha:
                        urls.append(linha)
                    else:
                        print(f"⚠️  Linha {linha_num} ignorada (não parece URL do YouTube): {linha}")
            
            print(f"📂 Carregadas {len(urls)} URLs do arquivo '{filename}'")
            return urls
            
        except FileNotFoundError:
            print(f"❌ Arquivo '{filename}' não encontrado")
            return []
        except Exception as e:
            print(f"❌ Erro ao ler arquivo '{filename}': {e}")
            return []

    def process_urls_from_file(self, filename: str = "urls.txt") -> List[Tuple[str, bool, str]]:
        """Processa todas as URLs de um arquivo."""
        urls = self.load_urls_from_file(filename)
        
        if not urls:
            print("❌ Nenhuma URL válida encontrada no arquivo")
            return []
        
        print(f"🚀 Iniciando processamento de {len(urls)} URLs")
        print("=" * 70)
        
        resultados = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n🎬 PROCESSANDO {i}/{len(urls)}")
            print(f"URL: {url}")
            print("-" * 50)
            
            transcript = self.download_single_video(url)
            
            if transcript:
                resultados.append((url, True, f"Sucesso - {len(transcript)} chars"))
                print(f"✅ SUCESSO!")
            else:
                resultados.append((url, False, "Falha ao obter transcrição"))
                print(f"❌ FALHOU")
            
            if i < len(urls):
                print(f"⏳ Aguardando {self.delay} segundos...")
                time.sleep(self.delay)
        
        self.print_summary(resultados)
        return resultados

    def print_summary(self, resultados: List[Tuple[str, bool, str]]):
        """Imprime resumo dos resultados."""
        print(f"\n{'='*70}")
        print("📊 RESUMO FINAL")
        print("=" * 70)
        
        sucessos = sum(1 for _, sucesso, _ in resultados if sucesso)
        total = len(resultados)
        
        print(f"Total processado: {total}")
        print(f"Sucessos: {sucessos}")
        print(f"Falhas: {total - sucessos}")
        if total > 0:
            print(f"Taxa de sucesso: {(sucessos/total)*100:.1f}%")
        
        print(f"\n📁 Arquivos salvos na pasta: {self.output_dir}")
        
        print("\n📋 Detalhes por URL:")
        for url, sucesso, detalhe in resultados:
            status = "✅" if sucesso else "❌"
            print(f"{status} {url}")
            print(f"   → {detalhe}")

def main():
    print("🎯 YOUTUBE TRANSCRIPT DOWNLOADER APRIMORADO")
    print("=" * 50)
    
    # Cria instância do downloader
    downloader = YouTubeTranscriptDownloader(output_dir="transcricoes", delay=5)
    
    # Processa URLs do arquivo
    resultados = downloader.process_urls_from_file("urls.txt")
    
    return resultados

if __name__ == "__main__":
    main()