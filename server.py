import socket
import threading
import json
import requests
from datetime import datetime

class NewsServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.api_key = "371b1937a3be4636a32f883166aa87d1"  
        self.base_url = "https://newsapi.org/v2"
        self.group_id = "group1"  # Add missing group_id
        
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(3)
        
        print(f"Server listening on {self.host}:{self.port}")
        
        while True:
            try:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket, address):
        client_name = ""
        try:
            # Receive client name
            client_name = client_socket.recv(1024).decode('utf-8')
            print(f"New connection from {address}: {client_name}")
            
            while True:
                request = client_socket.recv(4096).decode('utf-8')  # Increased buffer
                if not request:
                    break
                
                request_data = json.loads(request)
                print(f"Request from {client_name}: {request_data}")
                
                response = self.process_request(request_data, client_name)
                response_json = json.dumps(response).encode('utf-8')
                client_socket.send(response_json)
                
        except Exception as e:
            print(f"Error handling client {client_name}: {e}")
        finally:
            print(f"Client {client_name} disconnected")
            client_socket.close()
    
    def process_request(self, request_data, client_name):
        request_type = request_data.get('type')
        
        if request_type == 'headlines':
            return self.get_headlines(request_data, client_name)
        elif request_type == 'sources':
            return self.get_sources(request_data, client_name)
        elif request_type == 'details':
            return self.get_details(request_data, client_name)
            
    def get_headlines(self, request_data, client_name):
        try:
            url = f"{self.base_url}/top-headlines"
            params = {'apiKey': self.api_key, 'pageSize': 15}
            
            # Add filters based on request
            if request_data.get('keyword'):
                params['q'] = request_data['keyword']
            if request_data.get('category'):
                params['category'] = request_data['category']
            if request_data.get('country'):
                params['country'] = request_data['country']
            else:
                # Default to US if no country specified (NewsAPI requirement)
                params['country'] = 'us'
                
            response = requests.get(url, params=params)
            data = response.json()
            
            # Save to file with correct naming format
            filename = f"{client_name}_headlines_{self.group_id}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Process and return simplified list
            articles = data.get('articles', [])[:15]
            return {
                'type': 'headlines_list',
                'data': [
                    {
                        'id': i,
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author', 'Unknown'),
                        'title': article.get('title', 'No title')
                    }
                    for i, article in enumerate(articles)
                ],
                'full_data': articles
            }
        except Exception as e:
            print(f"Error getting headlines: {e}")
            return {'type': 'error', 'message': 'Failed to retrieve headlines'}
    
    def get_sources(self, request_data, client_name):
        try:
            url = f"{self.base_url}/sources"
            params = {'apiKey': self.api_key}
            
            # Add filters based on request
            if request_data.get('category'):
                params['category'] = request_data['category']
            if request_data.get('country'):
                params['country'] = request_data['country']
            if request_data.get('language'):
                params['language'] = request_data['language']
                
            response = requests.get(url, params=params)
            data = response.json()
            
            # Save to file with correct naming format
            filename = f"{client_name}_sources_{self.group_id}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Process and return simplified list
            sources = data.get('sources', [])[:15]
            return {
                'type': 'sources_list',
                'data': [
                    {
                        'id': source.get('id'),
                        'name': source.get('name'),
                        'description': source.get('description'),
                        'category': source.get('category'),
                        'country': source.get('country'),
                        'language': source.get('language'),
                        'url': source.get('url')
                    }
                    for source in sources
                ]
            }
        except Exception as e:
            print(f"Error getting sources: {e}")
            return {'type': 'error', 'message': 'Failed to retrieve sources'}
    
    def get_details(self, request_data, client_name):
        try:
            article_id = request_data.get('article_id', 0)
            
            # Load the stored headlines data
            filename = f"{client_name}_headlines_{self.group_id}.json"
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    articles = data.get('articles', [])
                    
                    if 0 <= article_id < len(articles):
                        article = articles[article_id]
                        return {
                            'type': 'article_details',
                            'data': {
                                'source': article.get('source', {}).get('name', 'Unknown'),
                                'author': article.get('author', 'Unknown'),
                                'title': article.get('title', 'No title'),
                                'url': article.get('url', 'No URL'),
                                'description': article.get('description', 'No description'),
                                'publishedAt': article.get('publishedAt', 'Unknown date'),
                                'content': article.get('content', 'No content available')
                            }
                        }
            except FileNotFoundError:
                pass
            
            return {
                'type': 'error',
                'message': 'Article not found or data unavailable'
            }
        except Exception as e:
            print(f"Error getting article details: {e}")
            return {'type': 'error', 'message': 'Failed to retrieve article details'}

if __name__ == "__main__":
    server = NewsServer()
    server.start_server()

