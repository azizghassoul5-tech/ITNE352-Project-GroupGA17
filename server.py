import socket
import threading
import json
import requests
from datetime import datetime

class NewsServer:
    """
    NewsServer Class - Handles client connections and news API requests
    
    This class demonstrates Object-Oriented Programming principles:
    - Encapsulation: Data and methods are bundled together
    - Abstraction: Complex API interactions are hidden behind simple methods
    - Modularity: Each method has a specific responsibility
    """
    
    def __init__(self, host='localhost', port=12345):
        """
        Constructor method - initializes server attributes
        
        Args:
            host (str): Server hostname
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.api_key = "371b1937a3be4636a32f883166aa87d1"  
        self.base_url = "https://newsapi.org/v2"
        self.group_id = "group1"
        
    def start_server(self):
        """
        Main server method - creates socket and handles incoming connections
        Uses threading to handle multiple clients simultaneously
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(3)
        
        print(f" Server listening on {self.host}:{self.port}")
        
        while True:
            try:
                client_socket, address = server_socket.accept()
                print(f" New connection from {address}")
                
                # Create thread for each client (multithreading)
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True  # Daemon thread for clean shutdown
                client_thread.start()
                
            except Exception as e:
                print(f" Error accepting connection: {e}")
    
    def handle_client(self, client_socket, address):
        """
        Handle individual client connections
        
        Args:
            client_socket: Socket object for client communication
            address: Client address tuple (host, port)
        """
        client_name = ""
        try:
            # Receive client name
            client_name = client_socket.recv(1024).decode('utf-8')
            print(f" Connection established with {address}: {client_name}")
            
            while True:
                request = client_socket.recv(4096).decode('utf-8')
                if not request:
                    break
                
                try:
                    request_data = json.loads(request)
                    print(f" Request from {client_name}: {request_data}")
                    
                    response = self.process_request(request_data, client_name)
                    response_json = json.dumps(response).encode('utf-8')
                    client_socket.send(response_json)
                    
                except json.JSONDecodeError:
                    error_response = {'type': 'error', 'message': 'Invalid JSON format'}
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                    
        except ConnectionResetError:
            print(f" Client {client_name} disconnected unexpectedly")
        except Exception as e:
            print(f" Error handling client {client_name}: {e}")
        finally:
            print(f" Client {client_name} disconnected")
            try:
                client_socket.close()
            except:
                pass
    
    def process_request(self, request_data, client_name):
        """
        Process different types of client requests
        
        Args:
            request_data (dict): Parsed JSON request from client
            client_name (str): Name of the requesting client
            
        Returns:
            dict: Response data to send back to client
        """
        request_type = request_data.get('type')
        
        print(f" Processing {request_type} request for {client_name}")
        
        if request_type == 'headlines':
            return self.get_headlines(request_data, client_name)
        elif request_type == 'sources':
            return self.get_sources(request_data, client_name)
        elif request_type == 'details':
            return self.get_details(request_data, client_name)
        else:
            return {'type': 'error', 'message': 'Unknown request type'}
            
    def get_headlines(self, request_data, client_name):
        """
        Fetch headlines from NewsAPI with filtering options
        
        Args:
            request_data (dict): Request parameters (keyword, category, country)
            client_name (str): Client identifier for file naming
            
        Returns:
            dict: Headlines response with article list
        """
        try:
            url = f"{self.base_url}/top-headlines"
            params = {'apiKey': self.api_key, 'pageSize': 15}
            
            # Add filters based on request
            filters_applied = []
            if request_data.get('keyword'):
                params['q'] = request_data['keyword']
                filters_applied.append(f"keyword: {request_data['keyword']}")
            if request_data.get('category'):
                params['category'] = request_data['category']
                filters_applied.append(f"category: {request_data['category']}")
            if request_data.get('country'):
                params['country'] = request_data['country']
                filters_applied.append(f"country: {request_data['country']}")
            else:
                params['country'] = 'us'
                filters_applied.append("country: us (default)")
            
            print(f" Fetching headlines with filters: {', '.join(filters_applied)}")
                
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Enhanced error handling for API responses
            if data.get('status') == 'error':
                error_msg = data.get('message', 'Unknown API error')
                print(f" API Error: {error_msg}")
                return {'type': 'error', 'message': f'API Error: {error_msg}'}
            
            # Save to file with correct naming format
            filename = f"{client_name}_headlines_{self.group_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f" Headlines saved to {filename}")
                
            # Process and return simplified list
            articles = data.get('articles', [])[:15]
            print(f" Retrieved {len(articles)} headlines for {client_name}")
            
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
        except requests.RequestException as e:
            print(f" Network error: {e}")
            return {'type': 'error', 'message': 'Network error occurred'}
        except Exception as e:
            print(f" Error getting headlines: {e}")
            return {'type': 'error', 'message': 'Failed to retrieve headlines'}
    
    def get_sources(self, request_data, client_name):
        """
        Fetch news sources from NewsAPI with filtering options
        
        Args:
            request_data (dict): Request parameters (category, country, language)
            client_name (str): Client identifier for file naming
            
        Returns:
            dict: Sources response with source list
        """
        try:
            url = f"{self.base_url}/sources"
            params = {'apiKey': self.api_key}
            
            # Add filters based on request
            filters_applied = []
            if request_data.get('category'):
                params['category'] = request_data['category']
                filters_applied.append(f"category: {request_data['category']}")
            if request_data.get('country'):
                params['country'] = request_data['country']
                filters_applied.append(f"country: {request_data['country']}")
            if request_data.get('language'):
                params['language'] = request_data['language']
                filters_applied.append(f"language: {request_data['language']}")
            
            if filters_applied:
                print(f" Fetching sources with filters: {', '.join(filters_applied)}")
            else:
                print(f" Fetching all sources")
                
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Enhanced error handling for API responses
            if data.get('status') == 'error':
                error_msg = data.get('message', 'Unknown API error')
                print(f" API Error: {error_msg}")
                return {'type': 'error', 'message': f'API Error: {error_msg}'}
            
            # Save to file with correct naming format
            filename = f"{client_name}_sources_{self.group_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f" Sources saved to {filename}")
                
            # Process and return simplified list
            sources = data.get('sources', [])[:15]
            print(f" Retrieved {len(sources)} sources for {client_name}")
            
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
        except requests.RequestException as e:
            print(f" Network error: {e}")
            return {'type': 'error', 'message': 'Network error occurred'}
        except Exception as e:
            print(f" Error getting sources: {e}")
            return {'type': 'error', 'message': 'Failed to retrieve sources'}
    
    def get_details(self, request_data, client_name):
        """
        Get detailed information for a specific article
        
        Args:
            request_data (dict): Request with article_id
            client_name (str): Client identifier for file access
            
        Returns:
            dict: Article details response
        """
        try:
            article_id = request_data.get('article_id', 0)
            print(f" Fetching details for article {article_id} for {client_name}")
            
            # Load the stored headlines data
            filename = f"{client_name}_headlines_{self.group_id}.json"
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    articles = data.get('articles', [])
                    
                    if 0 <= article_id < len(articles):
                        article = articles[article_id]
                        print(f" Article details retrieved for {client_name}")
                        
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
                    else:
                        print(f" Invalid article ID: {article_id}")
                        
            except FileNotFoundError:
                print(f" Headlines file not found for {client_name}")
            
            return {
                'type': 'error',
                'message': 'Article not found or data unavailable'
            }
        except Exception as e:
            print(f" Error getting article details: {e}")
            return {'type': 'error', 'message': 'Failed to retrieve article details'}

if __name__ == "__main__":
    print(" Starting News Server...")
    server = NewsServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n Server shutdown requested")
    except Exception as e:
        print(f" Server error: {e}")

