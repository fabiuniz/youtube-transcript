# pip install flask flask-cors yt-dlp youtube-transcript-api requests beautifulsoup4
from flask import Flask, request, jsonify, send_file ,render_template
from flask_cors import CORS
import subprocess
import os
import re
import time
import json
import requests
import io
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename
import threading
import uuid
import sys

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

class YouTubeTranscriptDownloader:
    def __init__(self, output_dir: str = "transcricoes", delay: int = 2):
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
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[^\w\s-]', '_', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        return filename.strip('_')

    def get_video_info(self, video_id: str) -> Dict:
        """Obtém informações básicas do vídeo."""
        try:
            cmd = ['yt-dlp', '--dump-json', '--no-download', f'https://youtube.com/watch?v={video_id}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'title': info.get('title', f'Video {video_id}'),
                    'duration': info.get('duration', 0),
                    'channel': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0)
                }
        except:
            pass
        
        return {
            'title': f'Video {video_id}',
            'duration': 0,
            'channel': 'Unknown',
            'view_count': 0
        }

    def download_with_ytdlp(self, url: str, video_id: str) -> Optional[str]:
        """Baixa legendas usando yt-dlp como fallback."""
        try:
            # Obtém informações do vídeo
            video_info = self.get_video_info(video_id)
            title = self.clean_filename(video_info['title'])
                
            # Tenta baixar legendas em português
            for lang in ['pt', 'pt-BR', 'en']:
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
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Procura pelo arquivo de legenda gerado
                    for file in self.output_dir.glob(f"*{video_id}*"):
                        if file.suffix in ['.vtt', '.srt']:
                            transcript = self.parse_subtitle_file(file)
                            file.unlink()  # Remove arquivo temporário
                            return transcript
            
            return None
            
        except Exception as e:
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
            return None

    def parse_vtt(self, content: str) -> str:
        """Converte conteúdo VTT para texto limpo."""
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('WEBVTT') or '-->' in line or line.startswith('NOTE'):
                continue
            if line.isdigit():
                continue
            
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
            if not line or line.isdigit() or '-->' in line:
                continue
            
            line = re.sub(r'<[^>]*>', '', line)
            if line:
                text_lines.append(line)
        
        return ' '.join(text_lines)

    def download_transcript_api(self, video_id: str) -> Optional[str]:
        """Baixa transcrição usando youtube-transcript-api."""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Estratégia 1: Tentar idiomas preferidos
            idiomas_preferidos = ['pt', 'pt-BR', 'en', 'en-US']
            
            for idioma in idiomas_preferidos:
                try:
                    transcript_data = YouTubeTranscriptApi.get_transcript(
                        video_id, 
                        languages=[idioma]
                    )
                    if transcript_data:
                        return self.process_transcript_data(transcript_data)
                except:
                    continue
            
            # Estratégia 2: Tentar primeira transcrição disponível
            for transcript in transcript_list:
                try:
                    transcript_data = transcript.fetch()
                    if transcript_data:
                        return self.process_transcript_data(transcript_data)
                except:
                    continue
            
            return None
        
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
            return None
        except Exception as e:
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
        
        return ' '.join(texto_completo).strip()

    def download_single_video(self, url: str) -> Dict:
        """Baixa transcrição de um único vídeo."""
        if not url:
            return {'success': False, 'message': 'URL não fornecida', 'url': url}
        
        video_id = self.extract_video_id(url)
        if not video_id:
            return {'success': False, 'message': 'ID do vídeo não encontrado', 'url': url}
        
        # Obtém informações do vídeo
        video_info = self.get_video_info(video_id)
        
        # Estratégia 1: youtube-transcript-api
        transcript = self.download_transcript_api(video_id)
        
        # Estratégia 2: yt-dlp se a primeira falhar
        if not transcript:
            transcript = self.download_with_ytdlp(url, video_id)
        
        if transcript:
            return {
                'success': True,
                'url': url,
                'video_id': video_id,
                'transcript': transcript,
                'size': len(transcript),
                'message': f'Sucesso - {len(transcript)} caracteres',
                'video_info': video_info
            }
        else:
            return {
                'success': False,
                'url': url,
                'video_id': video_id,
                'message': 'Nenhuma transcrição disponível',
                'video_info': video_info
            }

# Instância global do downloader
downloader = YouTubeTranscriptDownloader()

# Armazenamento temporário de resultados de processamento
processing_results = {}

def safe_print(text):
    """Função para imprimir texto de forma segura, lidando com problemas de encoding."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove caracteres que não podem ser codificados
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process-single', methods=['POST'])
def process_single_video():
    """Processa um único vídeo."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL é obrigatória'}), 400
        
        if 'youtube.com' not in url and 'youtu.be' not in url:
            return jsonify({'error': 'URL deve ser do YouTube'}), 400
        
        result = downloader.download_single_video(url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/process-multiple', methods=['POST'])
def process_multiple_videos():
    """Processa múltiplos vídeos."""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'Lista de URLs é obrigatória'}), 400
        
        # Filtra URLs válidas
        valid_urls = []
        for url in urls:
            url = url.strip()
            if url and not url.startswith('#') and ('youtube.com' in url or 'youtu.be' in url):
                valid_urls.append(url)
        
        if not valid_urls:
            return jsonify({'error': 'Nenhuma URL válida do YouTube encontrada'}), 400
        
        # Processa URLs
        results = []
        for i, url in enumerate(valid_urls):
            result = downloader.download_single_video(url)
            result['index'] = i
            results.append(result)
            
            # Delay entre requisições
            if i < len(valid_urls) - 1:
                time.sleep(downloader.delay)
        
        return jsonify({
            'results': results,
            'total': len(valid_urls),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success'])
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/process-file', methods=['POST'])
def process_file():
    """Processa arquivo com URLs."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Arquivo não encontrado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.lower().endswith('.txt'):
            return jsonify({'error': 'Apenas arquivos .txt são aceitos'}), 400
        
        # Lê conteúdo do arquivo
        content = file.read().decode('utf-8')
        lines = content.split('\n')
        
        # Extrai URLs válidas
        valid_urls = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and ('youtube.com' in line or 'youtu.be' in line):
                valid_urls.append(line)
        
        if not valid_urls:
            return jsonify({'error': 'Nenhuma URL válida encontrada no arquivo'}), 400
        
        # Processa URLs
        results = []
        for i, url in enumerate(valid_urls):
            result = downloader.download_single_video(url)
            result['index'] = i
            results.append(result)
            
            # Delay entre requisições
            if i < len(valid_urls) - 1:
                time.sleep(downloader.delay)
        
        return jsonify({
            'results': results,
            'total': len(valid_urls),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success'])
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/download-transcript/<video_id>')
def download_transcript(video_id):
    """Faz download de uma transcrição específica."""
    try:
        # Busca a transcrição nos resultados armazenados ou refaz o download
        transcript_data = None
        
        # Tenta reprocessar o vídeo se não encontrar nos resultados
        result = downloader.download_single_video(f'https://youtube.com/watch?v={video_id}')
        
        if not result['success']:
            return jsonify({'error': 'Transcrição não encontrada'}), 404
        
        transcript = result['transcript']
        video_info = result.get('video_info', {})
        filename = f"transcricao_{video_id}.txt"
        
        # Cria arquivo em memória
        file_content = io.BytesIO()
        file_content.write(transcript.encode('utf-8'))
        file_content.seek(0)
        
        return send_file(
            file_content,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao fazer download: {str(e)}'}), 500

@app.route('/api/download-all', methods=['POST'])
def download_all_transcripts():
    """Faz download de todas as transcrições em um arquivo ZIP."""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({'error': 'Nenhum resultado fornecido'}), 400
        
        # Filtra apenas resultados bem-sucedidos
        successful_results = [r for r in results if r.get('success') and r.get('transcript')]
        
        if not successful_results:
            return jsonify({'error': 'Nenhuma transcrição disponível'}), 400
        
        # Cria arquivo ZIP em memória
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for result in successful_results:
                video_id = result.get('video_id', 'unknown')
                transcript = result.get('transcript', '')
                video_info = result.get('video_info', {})
                
                filename = f"transcricao_{video_id}.txt"
                
                # Adiciona informações do vídeo no início
                content = f"# Transcrição do YouTube\n"
                content += f"# Vídeo ID: {video_id}\n"
                content += f"# Título: {video_info.get('title', 'N/A')}\n"
                content += f"# Canal: {video_info.get('channel', 'N/A')}\n"
                content += f"# URL: {result.get('url', 'N/A')}\n"
                content += f"# Caracteres: {len(transcript)}\n\n"
                content += transcript
                
                zip_file.writestr(filename, content.encode('utf-8'))
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name='transcricoes_youtube.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao criar arquivo ZIP: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Verifica se a API está funcionando."""
    return jsonify({
        'status': 'ok',
        'message': 'YouTube Transcript Downloader API está funcionando!',
        'dependencies': {
            'yt-dlp': 'ok' if os.system('yt-dlp --version > /dev/null 2>&1') == 0 else 'not found',
            'youtube-transcript-api': 'ok'
        }
    })

if __name__ == '__main__':
    safe_print(">> Iniciando YouTube Transcript Downloader API...")
    safe_print(">> API disponível em: http://localhost:5000")
    safe_print(">> Health check: http://localhost:5000/api/health")
    safe_print(">> Endpoints disponíveis:")
    safe_print("   - POST /api/process-single")
    safe_print("   - POST /api/process-multiple") 
    safe_print("   - POST /api/process-file")
    safe_print("   - GET /api/download-transcript/<video_id>")
    safe_print("   - POST /api/download-all")
    safe_print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)