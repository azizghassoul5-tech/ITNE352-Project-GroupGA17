import socket
import json

class NewsClient:
    """
    NewsClient Class - Handles server communication and user interface
    
    This class demonstrates Object-Oriented Programming principles:
    - Encapsulation: Network operations and UI logic are contained within the class
    - Abstraction: Complex socket operations are hidden behind simple methods
    - Modularity: Each method handles a specific aspect of client functionality
    """
    
    def __init__(self, host='localhost', port=12345):
        """
        Constructor method - initializes client attributes
        
        Args:
            host (str): Server hostname to connect to
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.socket = None
        self.username = ""
        
    def connect(self):
        """
        Establish connection to the news server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            if not self.username:
                self.username = input("Enter your username: ")
            self.socket.send(self.username.encode('utf-8'))
            
            print(f" Connected to server as {self.username}")
            return True
            
        except ConnectionRefusedError:
            print(" Connection refused. Is the server running?")
            return False
        except Exception as e:
            print(f" Connection failed: {e}")
            return False
    
    def send_request(self, request_data):
        """
        Send request to server and receive response
        
        Args:
            request_data (dict): Request data to send
            
        Returns:
            dict: Server response or None if failed
        """
        try:
            request_json = json.dumps(request_data)
            print(f" Sending request: {request_data.get('type', 'unknown')}")
            
            self.socket.send(request_json.encode('utf-8'))
            
            # Receive response in chunks to handle large data
            response_data = b""
            while True:
                try:
                    chunk = self.socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    
                    # Try to parse complete JSON
                    try:
                        response = json.loads(response_data.decode('utf-8'))
                        print(f" Received response: {response.get('type', 'unknown')}")
                        return response
                    except json.JSONDecodeError:
                        # Continue receiving if JSON is incomplete
                        continue
                        
                except socket.timeout:
                    print(" Request timeout")
                    break
                    
        except ConnectionResetError:
            print(" Connection lost")
            return None
        except Exception as e:
            print(f" Request failed: {e}")
            return None
    
    def display_main_menu(self):
        """Display main menu with enhanced formatting"""
        print("\n" + "="*50)
        print("  NEWS SERVICE SYSTEM - MAIN MENU")
        print("="*50)
        print("1.  Search headlines")
        print("2.  List of sources")
        print("3.  Quit")
        print("="*50)
        return input("Select option (1-3): ").strip()
    
    def display_headlines_menu(self):
        """Display headlines menu with enhanced formatting"""
        print("\n" + "="*50)
        print(" HEADLINES MENU")
        print("="*50)
        print("1.  Search for keywords")
        print("2.  Search by category")
        print("3.  Search by country")
        print("4.  List all new headlines")
        print("5.   Back to main menu")
        print("="*50)
        return input("Select option (1-5): ").strip()
    
    def display_sources_menu(self):
        """Display sources menu with enhanced formatting"""
        print("\n" + "="*50)
        print(" SOURCES MENU")
        print("="*50)
        print("1.  Search by category")
        print("2.  Search by country")
        print("3.   Search by language")
        print("4.  List all")
        print("5.   Back to main menu")
        print("="*50)
        return input("Select option (1-5): ").strip()
    
    def handle_headlines_request(self, option):
        """Handle headlines requests with enhanced user interaction"""
        request_data = {'type': 'headlines'}
        
        if option == '1':
            print("\n KEYWORD SEARCH")
            keyword = input("Enter keyword: ").strip()
            if keyword:
                request_data['keyword'] = keyword
            else:
                print(" No keyword entered")
                return
                
        elif option == '2':
            print("\n CATEGORY SEARCH")
            print("Available categories:")
            categories = ['business', 'general', 'health', 'science', 'sports', 'technology']
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat.title()}")
            
            try:
                choice = int(input("Select category (1-6): "))
                if 1 <= choice <= 6:
                    request_data['category'] = categories[choice-1]
                    print(f" Selected: {categories[choice-1].title()}")
                else:
                    print(" Invalid selection")
                    return
            except ValueError:
                print(" Invalid input")
                return
                
        elif option == '3':
            print("\n COUNTRY SEARCH")
            print("Available countries:")
            countries = {'1': 'au', '2': 'ca', '3': 'jp', '4': 'ae', '5': 'sa', '6': 'kr', '7': 'us', '8': 'ma'}
            for key, value in countries.items():
                print(f"  {key}. {value.upper()}")
            
            choice = input("Select country (1-8): ").strip()
            if choice in countries:
                request_data['country'] = countries[choice]
                print(f" Selected: {countries[choice].upper()}")
            else:
                print(" Invalid selection")
                return
                
        elif option == '4':
            print("\n LISTING ALL HEADLINES")
            
        response = self.send_request(request_data)
        if response:
            if response.get('type') == 'error':
                print(f" Error: {response.get('message', 'Unknown error')}")
            else:
                self.display_headlines_list(response)
    
    def display_headlines_list(self, response):
        """Display headlines with enhanced formatting"""
        print("\n" + "="*80)
        print(" HEADLINES RESULTS")
        print("="*80)
        
        articles = response.get('data', [])
        
        if not articles:
            print(" No headlines found")
            return
        
        for article in articles:
            print(f"\n{article['id']}. 📄 {article['title']}")
            print(f"    Source: {article['source']} |   Author: {article['author']}")
            print("-" * 80)
        
        print(f"\n Total: {len(articles)} headlines")
        print("="*80)
        
        while True:
            choice = input("\nEnter article number for details (or 'back' to return): ").strip().lower()
            
            if choice == 'back':
                break
            
            try:
                article_id = int(choice)
                if 0 <= article_id < len(articles):
                    self.request_article_details(article_id, response.get('full_data', []))
                    break
                else:
                    print(f" Invalid article number. Please enter 0-{len(articles)-1}")
            except ValueError:
                print(" Please enter a valid number or 'back'")
    
    def handle_sources_request(self, sources_type):
        """Handle sources requests with enhanced user interaction"""
        request_data = {'type': 'sources'}
        
        if sources_type == '1':  # By category
            print("\n CATEGORY SEARCH")
            categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat.title()}")
            
            try:
                choice = int(input("Select category (1-7): "))
                if 1 <= choice <= 7:
                    request_data['category'] = categories[choice-1]
                    print(f" Selected: {categories[choice-1].title()}")
                else:
                    print(" Invalid selection")
                    return
            except ValueError:
                print(" Invalid input")
                return
                
        elif sources_type == '2':  # By country
            print("\n COUNTRY SEARCH")
            countries = {'1': 'us', '2': 'gb', '3': 'ca', '4': 'au', '5': 'de'}
            for key, value in countries.items():
                print(f"  {key}. {value.upper()}")
            
            choice = input("Select country (1-5): ").strip()
            if choice in countries:
                request_data['country'] = countries[choice]
                print(f" Selected: {countries[choice].upper()}")
            else:
                print(" Invalid selection")
                return
                
        elif sources_type == '3':  # By language
            print("\n  LANGUAGE SEARCH")
            languages = {'1': 'en', '2': 'ar'}
            for key, value in languages.items():
                lang_name = 'English' if value == 'en' else 'Arabic'
                print(f"  {key}. {lang_name} ({value})")
            
            choice = input("Select language (1-2): ").strip()
            if choice in languages:
                request_data['language'] = languages[choice]
                lang_name = 'English' if languages[choice] == 'en' else 'Arabic'
                print(f" Selected: {lang_name}")
            else:
                print(" Invalid selection")
                return
                
        elif sources_type == '4':
            print("\n LISTING ALL SOURCES")
        
        response = self.send_request(request_data)
        
        if response and response.get('type') == 'sources_list':
            self.display_sources_list(response)
        elif response and response.get('type') == 'error':
            print(f" Error: {response['message']}")
        else:
            print(" Failed to retrieve sources.")
    
    def display_sources_list(self, response):
        """Display sources with enhanced formatting"""
        print("\n" + "="*80)
        print(" NEWS SOURCES")
        print("="*80)
        
        sources = response.get('data', [])
        
        if not sources:
            print(" No sources found")
            return
        
        for i, source in enumerate(sources):
            print(f"\n{i}.  {source['name']}")
            print(f"    {source['country']} |  {source['category']} |   {source['language']}")
            print("-" * 80)
        
        print(f"\n Total: {len(sources)} sources")
        print("="*80)
        
        while True:
            choice = input("\nEnter source number for details (or 'back' to return): ").strip().lower()
            
            if choice == 'back':
                break
            
            try:
                source_id = int(choice)
                if 0 <= source_id < len(sources):
                    self.display_source_details(sources[source_id])
                    break
                else:
                    print(f" Invalid source number. Please enter 0-{len(sources)-1}")
            except ValueError:
                print(" Please enter a valid number or 'back'")
    
    def display_source_details(self, source):
        """Display detailed source information"""
        print("\n" + "="*80)
        print(" SOURCE DETAILS")
        print("="*80)
        print(f" Name: {source['name']}")
        print(f" Country: {source['country']}")
        print(f" Category: {source['category']}")
        print(f"  Language: {source['language']}")
        print(f" URL: {source['url']}")
        print(f" Description: {source['description']}")
        print("="*80)

    def request_article_details(self, article_id, full_data=None):
        """Request and display article details"""
        request_data = {
            'type': 'details',
            'article_id': article_id
        }
        
        response = self.send_request(request_data)
        
        if response and response.get('type') == 'article_details':
            data = response['data']
            print("\n" + "="*80)
            print(" ARTICLE DETAILS")
            print("="*80)
            print(f" Title: {data.get('title', 'N/A')}")
            print(f" Source: {data.get('source', 'N/A')}")
            print(f"  Author: {data.get('author', 'N/A')}")
            print(f" Published: {data.get('publishedAt', 'N/A')}")
            print(f" URL: {data.get('url', 'N/A')}")
            print(f"\n Description:")
            print(f"   {data.get('description', 'N/A')}")
            if data.get('content'):
                print(f"\n Content:")
                print(f"   {data.get('content', 'N/A')}")
            print("="*80)
        elif response and response.get('type') == 'error':
            print(f" Error: {response['message']}")
        else:
            print(" Failed to retrieve article details.")

    def run(self):
        """
        Main client execution method - handles the complete user interaction flow
        Demonstrates the main program logic using class methods
        """
        print(" Starting News Client...")
        
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
                        else:
                            print(" Invalid option. Please select 1-5.")
                        
                elif choice == '2':
                    while True:
                        sources_choice = self.display_sources_menu()
                        if sources_choice == '5':
                            break
                        elif sources_choice in ['1', '2', '3', '4']:
                            self.handle_sources_request(sources_choice)
                        else:
                            print(" Invalid option. Please select 1-5.")
                            
                elif choice == '3':
                    print(" Goodbye!")
                    break
                else:
                    print(" Invalid option. Please select 1-3.")
                    
        except KeyboardInterrupt:
            print("\n Client shutdown requested")
        finally:
            if self.socket:
                try:
                    self.socket.close()
                    print(" Connection closed")
                except:
                    pass

if __name__ == "__main__":
    client = NewsClient()
    client.run()
