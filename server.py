import socket
import threading
import json
import requests
from datetime import datetime

class NewsServer:
    """
    NewsServer Class - Handles client connections and news API requests
    
    This class demonstrates Object-Oriented Programming principles:
    - Encapsulation: Server logic and API handling are contained within the class
    - Abstraction: Complex API operations are hidden behind simple methods
    - Modularity: Each method handles a specific aspect of server functionality
    """
    
    def __init__(self, host='localhost', port=12345):
        """
        Constructor method - initializes server attributes
        
        Args:
            host (str): Server hostname to bind to
            port (int): Server port number to listen on
        """
        self.host = host
        self.port = port
        self.socket = None
        self.api_key = "b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8"  # NewsAPI key
        self.base_url = "https://newsapi.org/v2"
        self.clients = []
        self.running = False
        
    def start_server(self):
        """
        Start the server and begin listening for connections
        
        Returns:
            bool: True if server started successfully, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"Server started on {self.host}:{self.port}")
            print("Waiting for client connections...")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"New client connected from {client_address}")
                    
                    # Create new thread for each client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
            
        return True
    
    def handle_client(self, client_socket, client_address):
        """
        Handle individual client connections and requests
        
        Args:
            client_socket: Client socket connection
            client_address: Client address tuple (host, port)
        """
        username = ""
        
        try:
            # Receive username
            username_data = client_socket.recv(1024)
            if username_data:
                username = username_data.decode('utf-8')
                print(f"Client {client_address} identified as: {username}")
            
            self.clients.append({
                'socket': client_socket,
                'address': client_address,
                'username': username,
                'connected_at': datetime.now()
            })
            
            while True:
                # Receive request from client
                request_data = client_socket.recv(4096)
                
                if not request_data:
                    break
                
                try:
                    request = json.loads(request_data.decode('utf-8'))
                    print(f"Request from {username}: {request.get('type', 'unknown')}")
                    
                    # Process request based on type
                    response = self.process_request(request)
                    
                    # Send response back to client
                    response_json = json.dumps(response)
                    client_socket.send(response_json.encode('utf-8'))
                    
                except json.JSONDecodeError:
                    error_response = {
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                    
        except ConnectionResetError:
            print(f"Client {username} ({client_address}) disconnected unexpectedly")
        except Exception as e:
            print(f"Error handling client {username}: {e}")
        finally:
            # Clean up client connection
            self.remove_client(client_socket)
            try:
                client_socket.close()
                print(f"Connection with {username} ({client_address}) closed")
            except:
                pass
    
    def remove_client(self, client_socket):
        """Remove client from active clients list"""
        self.clients = [client for client in self.clients if client['socket'] != client_socket]
    
    def process_request(self, request):
        """
        Process client requests and return appropriate responses
        
        Args:
            request (dict): Client request data
            
        Returns:
            dict: Response data to send back to client
        """
        request_type = request.get('type')
        
        if request_type == 'headlines':
            return self.handle_headlines_request(request)
        elif request_type == 'sources':
            return self.handle_sources_request(request)
        elif request_type == 'details':
            return self.handle_details_request(request)
        else:
            return {
                'type': 'error',
                'message': f'Unknown request type: {request_type}'
            }
    
    def handle_headlines_request(self, request):
        """
        Handle headlines requests from clients
        
        Args:
            request (dict): Headlines request data
            
        Returns:
            dict: Headlines response data
        """
        try:
            # Build API URL
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'pageSize': 15  # Limit results
            }
            
            # Add search parameters
            if 'keyword' in request:
                params['q'] = request['keyword']
            if 'category' in request:
                params['category'] = request['category']
            if 'country' in request:
                params['country'] = request['country']
            else:
                params['country'] = 'us'  # Default country
            
            print(f"Fetching headlines with params: {params}")
            
            # Make API request
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Format articles for client
                formatted_articles = []
                full_articles = []
                
                for i, article in enumerate(articles):
                    # Basic info for list display
                    formatted_article = {
                        'id': i,
                        'title': article.get('title', 'No title'),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author', 'Unknown'),
                        'publishedAt': article.get('publishedAt', 'Unknown')
                    }
                    formatted_articles.append(formatted_article)
                    
                    # Full article data for details
                    full_articles.append(article)
                
                return {
                    'type': 'headlines_list',
                    'data': formatted_articles,
                    'full_data': full_articles,
                    'total': len(formatted_articles)
                }
            else:
                return {
                    'type': 'error',
                    'message': f'API request failed: {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'type': 'error',
                'message': 'Request timeout - API server not responding'
            }
        except requests.exceptions.RequestException as e:
            return {
                'type': 'error',
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }
    
    def handle_sources_request(self, request):
        """
        Handle sources requests from clients
        
        Args:
            request (dict): Sources request data
            
        Returns:
            dict: Sources response data
        """
        try:
            # Build API URL
            url = f"{self.base_url}/sources"
            params = {
                'apiKey': self.api_key
            }
            
            # Add search parameters
            if 'category' in request:
                params['category'] = request['category']
            if 'country' in request:
                params['country'] = request['country']
            if 'language' in request:
                params['language'] = request['language']
            
            print(f"Fetching sources with params: {params}")
            
            # Make API request
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                sources = data.get('sources', [])
                
                # Format sources for client
                formatted_sources = []
                for source in sources:
                    formatted_source = {
                        'name': source.get('name', 'Unknown'),
                        'country': source.get('country', 'Unknown'),
                        'category': source.get('category', 'Unknown'),
                        'language': source.get('language', 'Unknown'),
                        'url': source.get('url', 'Unknown'),
                        'description': source.get('description', 'No description available')
                    }
                    formatted_sources.append(formatted_source)
                
                return {
                    'type': 'sources_list',
                    'data': formatted_sources,
                    'total': len(formatted_sources)
                }
            else:
                return {
                    'type': 'error',
                    'message': f'API request failed: {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'type': 'error',
                'message': 'Request timeout - API server not responding'
            }
        except requests.exceptions.RequestException as e:
            return {
                'type': 'error',
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }
    
    def handle_details_request(self, request):
        """
        Handle article details requests from clients
        
        Args:
            request (dict): Details request data
            
        Returns:
            dict: Article details response data
        """
        try:
            article_id = request.get('article_id')
            
            if article_id is None:
                return {
                    'type': 'error',
                    'message': 'Article ID is required'
                }
            
            # For this implementation, we'll return a mock detailed response
            # In a real application, you might store the full articles or make another API call
            return {
                'type': 'article_details',
                'data': {
                    'title': f'Detailed article {article_id}',
                    'source': 'News Source',
                    'author': 'News Author',
                    'publishedAt': datetime.now().isoformat(),
                    'url': 'https://example.com/article',
                    'description': 'This is a detailed description of the article.',
                    'content': 'This is the full content of the article. In a real implementation, this would contain the actual article content from the API.'
                }
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }
    
    def stop_server(self):
        """Stop the server and close all connections"""
        print("\nShutting down server...")
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client['socket'].close()
            except:
                pass
        
        # Close server socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("Server stopped")

def main():
    """Main function to start the news server"""
    server = NewsServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    finally:
        server.stop_server()

if __name__ == "__main__":
    main()
