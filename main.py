import requests
import feedparser
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time
import os
from dotenv import load_dotenv

load_dotenv()


class AINewsCollector:
    def __init__(self):
        self.sources = [
            {
                'name': 'NewsAPI - IA General',
                'type': 'newsapi',
                'url': 'https://newsapi.org/v2/everything',
                'params': {
                    'q': 'artificial intelligence AI machine learning',
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 20
                },
                'api_key': os.getenv('TU_API_KEY_NEWSAPI')  # Obtener de https://newsapi.org/register
            },
            {
                'name': 'Reddit r/artificial',
                'type': 'reddit',
                'url': 'https://www.reddit.com/r/artificial/.json',
                'params': {'limit': 15}
            },
            {
                'name': 'Reddit r/MachineLearning', 
                'type': 'reddit',
                'url': 'https://www.reddit.com/r/MachineLearning/.json',
                'params': {'limit': 15}
            },
            {
                'name': 'Google News - IA Español',
                'type': 'rss',
                'url': 'https://news.google.com/rss/search',
                'params': {
                    'q': 'inteligencia artificial',
                    'hl': 'es-419',
                    'gl': 'ES'
                }
            }
        ]
    
    def calculate_relevance_score(self, title: str, content: str = "") -> int:
        """Calcula puntaje de relevancia para noticias de IA"""
        text = (title + ' ' + content).lower()
        keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'gpt', 'openai', 'chatgpt', 'inteligencia artificial',
            'aprendizaje automático', 'red neuronal', 'modelo de lenguaje'
        ]
        
        return sum(1 for keyword in keywords if keyword in text)

    def fetch_newsapi(self, source: Dict) -> List[Dict]:
        """Obtiene noticias de NewsAPI"""
        try:
            params = source['params'].copy()
            params['apiKey'] = source['api_key']
            
            response = requests.get(source['url'], params=params, timeout=10)
            response.raise_for_status()
            
            articles = []
            for article in response.json().get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'content': article.get('description', '') or article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'image': article.get('urlToImage', ''),
                    'publishedAt': datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ') if article.get('publishedAt') else datetime.now(),
                    'category': 'IA',
                    'score': self.calculate_relevance_score(article.get('title', ''), article.get('description', ''))
                })
            return articles
        except Exception as e:
            print(f"Error con NewsAPI: {e}")
            return []

    def fetch_reddit(self, source: Dict) -> List[Dict]:
        """Obtiene noticias de Reddit"""
        try:
            headers = {'User-Agent': 'AINewsCollector/1.0'}
            response = requests.get(source['url'], params=source['params'], headers=headers, timeout=10)
            response.raise_for_status()
            
            articles = []
            for post in response.json().get('data', {}).get('children', []):
                data = post['data']
                articles.append({
                    'title': data.get('title', ''),
                    'content': data.get('selftext', 'Ver enlace para más detalles'),
                    'url': f"https://reddit.com{data.get('permalink', '')}",
                    'source': f"Reddit - {data.get('subreddit', '')}",
                    'publishedAt': datetime.fromtimestamp(data.get('created_utc', 0)),
                    'upvotes': data.get('ups', 0),
                    'comments': data.get('num_comments', 0),
                    'category': 'IA Comunidad',
                    'score': data.get('ups', 0) + (data.get('num_comments', 0) * 0.5)
                })
            return articles
        except Exception as e:
            print(f"Error con Reddit: {e}")
            return []

    def fetch_rss(self, source: Dict) -> List[Dict]:
        """Obtiene noticias de fuentes RSS"""
        try:
            # Construir URL para RSS
            params = '&'.join([f"{k}={v}" for k, v in source['params'].items()])
            rss_url = f"{source['url']}?{params}"
            
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries[:15]:  # Limitar a 15 entradas
                articles.append({
                    'title': entry.get('title', ''),
                    'content': entry.get('description', ''),
                    'url': entry.get('link', ''),
                    'source': source['name'],
                    'publishedAt': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'category': 'IA Noticias',
                    'score': self.calculate_relevance_score(entry.get('title', ''), entry.get('description', ''))
                })
            return articles
        except Exception as e:
            print(f"Error con RSS {source['name']}: {e}")
            return []

    def fetch_all_news(self) -> List[Dict]:
        """Obtiene noticias de todas las fuentes"""
        topic = input("Ingresa el tema a buscar: ")
        print(f"🔍 Buscando noticias sobre '{topic}'...\n")
        
        # Actualizar el tema en las fuentes que lo usan
        for source in self.sources:
            if 'q' in source['params']:
                source['params']['q'] = topic
        
        all_articles = []
        
        for source in self.sources:
            try:
                print(f"📡 Conectando con: {source['name']}")
                
                if source['type'] == 'newsapi':
                    articles = self.fetch_newsapi(source)
                elif source['type'] == 'reddit':
                    articles = self.fetch_reddit(source)
                elif source['type'] == 'rss':
                    articles = self.fetch_rss(source)
                else:
                    continue
                
                all_articles.extend(articles)
                print(f"✅ Obtenidas {len(articles)} noticias de {source['name']}\n")
                time.sleep(1)  # Respeta rate limiting
                
            except Exception as e:
                print(f"❌ Error con {source['name']}: {e}")
        
        return self.process_and_display_news(all_articles)

    def process_and_display_news(self, articles: List[Dict]) -> List[Dict]:
        """Procesa y muestra las noticias"""
        # Filtrar y ordenar
        processed_news = [
            article for article in articles
            if article['title'] and len(article['title']) > 10
            and 'subscription' not in article['title'].lower()
            and 'paywall' not in article['title'].lower()
        ]
        
        # Ordenar por score y fecha
        processed_news.sort(key=lambda x: (-x['score'], x['publishedAt']), reverse=True)
        processed_news = processed_news[:30]  # Top 30 noticias
        
        # Agregar ID incremental
        for i, article in enumerate(processed_news, 1):
            article['new_id'] = i
        
        # Mostrar resultados
        print("=" * 80)
        print("📊 RESUMEN DE NOTICIAS DE INTELIGENCIA ARTIFICIAL")
        print("=" * 80)
        
        for i, article in enumerate(processed_news, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   📅 {article['publishedAt'].strftime('%d/%m/%Y %H:%M')}")
            print(f"   📍 Fuente: {article['source']}")
            print(f"   ⭐ Relevancia: {article['score']:.1f}")
            print(f"   🔗 Enlace: {article['url']}")
            content_preview = article['content'][:150] + '...' if article['content'] and len(article['content']) > 150 else article['content']
            print(f"   📝 Contenido: {content_preview}")
            print('-' * 80)
        
        print(f"\n🎯 Total de noticias encontradas: {len(processed_news)}")
        print("💡 Puedes copiar los enlaces para revisar y publicar manualmente")
        print("=" * 80)
        
        # Generar nombre de archivo con fecha y hora
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M')
        filename = f'result_{timestamp}.json'
        
        # Guardar en JSON para uso posterior
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(processed_news, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Noticias guardadas en '{filename}'")
        
        return processed_news

# Ejecutar el colector
if __name__ == "__main__":
    collector = AINewsCollector()
    collector.fetch_all_news()