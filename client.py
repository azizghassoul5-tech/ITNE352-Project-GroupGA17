import socket
import json

class NewsClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.username = ""
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            if not self.username:  # Only ask for username if not already set
                self.username = input("Enter your username: ")
            self.socket.send(self.username.encode('utf-8'))
            
            print(f"Connected to server as {self.username}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def send_request(self, request_data):
        try:
            self.socket.send(json.dumps(request_data).encode('utf-8'))
            
            # Receive response in chunks to handle large data
            response_data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                try:
                    # Try to parse complete JSON
                    response = json.loads(response_data.decode('utf-8'))
                    return response
                except json.JSONDecodeError:
                    # Continue receiving if JSON is incomplete
                    continue
                
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def display_main_menu(self):
        print("\n=== MAIN MENU ===")
        print("1. Search headlines")
        print("2. List of sources")
        print("3. Quit")
        return input("Select option: ")
    
    def display_headlines_menu(self):
        print("\n=== HEADLINES MENU ===")
        print("1. Search for keywords")
        print("2. Search by category")
        print("3. Search by country")
        print("4. List all new headlines")
        print("5. Back to main menu")
        return input("Select option: ")
    
    def display_sources_menu(self):
        print("\n=== SOURCES MENU ===")
        print("1. Search by category")
        print("2. Search by country")
        print("3. Search by language")
        print("4. List all")
        print("5. Back to main menu")
        return input("Select option: ")
    
    def handle_headlines_request(self, option):
        request_data = {'type': 'headlines'}
        
        if option == '1':
            keyword = input("Enter keyword: ")
            request_data['keyword'] = keyword
        elif option == '2':
            print("Categories: business, general, health, science, sports, technology")
            category = input("Enter category: ")
            request_data['category'] = category
        elif option == '3':
            print("Countries: au, ca, jp, ae, sa, kr, us, ma")
            country = input("Enter country code: ")
            request_data['country'] = country
        elif option == '4':
            pass  # No additional parameters needed
            
        response = self.send_request(request_data)
        if response:
            self.display_headlines_list(response)
    
    def display_headlines_list(self, response):
        print("\n=== HEADLINES ===")
        articles = response.get('data', [])
        
        for article in articles:
            print(f"{article['id']}. {article['title']}")
            print(f"   Source: {article['source']}, Author: {article['author']}")
            print()
        
        choice = input("Enter article number for details (or 'back'): ")
        if choice.isdigit():
            article_id = int(choice)
            if 0 <= article_id < len(articles):
                self.request_article_details(article_id, response.get('full_data', []))
    
    def handle_sources_request(self, sources_type):
        request_data = {'type': 'sources'}
        
        if sources_type == '1':  # By category
            print("\nAvailable categories:")
            categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat.title()}")
            
            choice = input("Select category (1-7): ")
            if choice.isdigit() and 1 <= int(choice) <= 7:
                request_data['category'] = categories[int(choice)-1]
                
        elif sources_type == '2':  # By country
            print("\nAvailable countries:")
            countries = {'1': 'us', '2': 'gb', '3': 'ca', '4': 'au', '5': 'de'}
            for key, value in countries.items():
                print(f"{key}. {value.upper()}")
            
            choice = input("Select country (1-5): ")
            if choice in countries:
                request_data['country'] = countries[choice]
                
        elif sources_type == '3':  # By language
            print("\nAvailable languages:")
            languages = {'1': 'en', '2': 'ar'}  # Only en and ar as per assignment
            for key, value in languages.items():
                print(f"{key}. {value}")
            
            choice = input("Select language (1-2): ")
            if choice in languages:
                request_data['language'] = languages[choice]
        elif sources_type == '4':
            # List all sources - no additional parameters needed
            pass
        
        response = self.send_request(request_data)
        
        if response and response.get('type') == 'sources_list':
            print(f"\n--- News Sources ---")
            for i, source in enumerate(response['data']):
                print(f"{i}. {source['name']}")
            print()
            
            choice = input("Enter source number for details (or 'back'): ")
            if choice.isdigit():
                source_id = int(choice)
                if 0 <= source_id < len(response['data']):
                    source = response['data'][source_id]
                    print(f"\n--- Source Details ---")
                    print(f"Name: {source['name']}")
                    print(f"Country: {source['country']}")
                    print(f"Description: {source['description']}")
                    print(f"URL: {source['url']}")
                    print(f"Category: {source['category']}")
                    print(f"Language: {source['language']}")
        elif response and response.get('type') == 'error':
            print(f"Error: {response['message']}")
        else:
            print("Failed to retrieve sources.")

    def request_article_details(self, article_id, full_data=None):
        request_data = {
            'type': 'details',
            'article_id': article_id
        }
        
        response = self.send_request(request_data)
        
        if response and response.get('type') == 'article_details':
            data = response['data']
            print(f"\n--- Article Details ---")
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Source: {data.get('source', 'N/A')}")
            print(f"Author: {data.get('author', 'N/A')}")
            print(f"URL: {data.get('url', 'N/A')}")
            print(f"Description: {data.get('description', 'N/A')}")
            print(f"Published: {data.get('publishedAt', 'N/A')}")
            if data.get('content'):
                print(f"Content: {data.get('content', 'N/A')}")
        elif response and response.get('type') == 'error':
            print(f"Error: {response['message']}")
        else:
            print("Failed to retrieve article details.")

    def run(self):
        if not self.connect():
            return
            
        try:
            while True:
                choice = self.display_main_menu()
                
                if choice == '1':
                    while True:
                        headlines_choice = self.display_headlines_menu()
                        if headlines_choice == '5':
                            break
                        elif headlines_choice in ['1', '2', '3', '4']:
                            self.handle_headlines_request(headlines_choice)
                        
                elif choice == '2':
                    while True:
                        sources_choice = self.display_sources_menu()
                        if sources_choice == '5':
                            break
                        elif sources_choice in ['1', '2', '3', '4']:
                            self.handle_sources_request(sources_choice)
                            
                elif choice == '3':
                    print("Goodbye!")
                    break
                    
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    client = NewsClient()
    client.run()
