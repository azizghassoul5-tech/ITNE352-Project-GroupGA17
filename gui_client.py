import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import json
import socket
import threading

class NewsClient:
    """Simplified NewsClient for GUI"""
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.username = ""
        
    def connect(self):
        """Connect to the news server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Send username to server
            if self.username:
                self.socket.send(self.username.encode('utf-8'))
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def send_request(self, request_data):
        """Send request to server and return response"""
        try:
            request_json = json.dumps(request_data)
            self.socket.send(request_json.encode('utf-8'))
            
            # Receive response
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
                        return response
                    except json.JSONDecodeError:
                        continue
                        
                except socket.timeout:
                    break
                    
        except Exception as e:
            print(f"Request failed: {e}")
            return None

class NewsClientGUI:
    def __init__(self):
        self.client = None
        self.root = tk.Tk()
        self.root.title("News Service System - ITNE352 Project")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f8ff')
        
        # Configure styles
        self.setup_styles()
        
        # Data storage
        self.current_articles = []
        self.current_sources = []
        self.connected = False
        
    def setup_styles(self):
        """Setup custom styles for the GUI"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Title.TLabel', font=('Arial', 20, 'bold'), background='#f0f8ff')
        self.style.configure('Heading.TLabel', font=('Arial', 14, 'bold'), background='#f0f8ff')
        self.style.configure('Info.TLabel', font=('Arial', 10), background='#f0f8ff', foreground='#666')
        self.style.configure('Custom.TButton', font=('Arial', 11), padding=10)
        
    def show_connection_dialog(self):
        """Show connection setup dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Connection Setup")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#f0f8ff')
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 250, self.root.winfo_rooty() + 200))
        
        # Title
        ttk.Label(dialog, text="News Client Setup", style='Title.TLabel').pack(pady=20)
        
        # Username input
        ttk.Label(dialog, text="Enter your username:", style='Heading.TLabel').pack(pady=10)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(dialog, textvariable=username_var, font=('Arial', 12), width=20)
        username_entry.pack(pady=5)
        username_entry.focus()
        
        # Result variable
        self.connection_result = None
        
        def on_connect():
            username = username_var.get().strip()
            if not username:
                messagebox.showerror("Error", "Please enter a username")
                return
            
            self.connection_result = username
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#f0f8ff')
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Connect", command=on_connect, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=on_cancel, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=10)
        
        # Handle Enter key
        username_entry.bind('<Return>', lambda e: on_connect())
        
        dialog.wait_window()
        return self.connection_result
    
    def create_main_window(self):
        """Create the main application window"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="News Service System", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="ITNE352 Network Programming Project", 
                                  style='Info.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # Connection status
        if self.connected and self.client:
            status_text = f"Connected: {self.client.username}"
            status_label = ttk.Label(main_frame, text=status_text, style='Heading.TLabel')
            status_label.pack(pady=(0, 30))
        
        # Menu buttons frame
        button_frame = tk.Frame(main_frame, bg='#f0f8ff')
        button_frame.pack(expand=True)
        
        # Main menu buttons
        ttk.Button(button_frame, text="Search Headlines", 
                  command=self.show_headlines_menu, style='Custom.TButton', 
                  width=25).pack(pady=15)
        ttk.Button(button_frame, text="List of Sources", 
                  command=self.show_sources_menu, style='Custom.TButton', 
                  width=25).pack(pady=15)
        ttk.Button(button_frame, text="Quit", 
                  command=self.quit_app, style='Custom.TButton', 
                  width=25).pack(pady=15)
    
    def show_headlines_menu(self):
        """Show headlines menu"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text="Headlines Menu", style='Title.TLabel').pack(pady=(0, 30))
        
        # Menu buttons
        button_frame = tk.Frame(main_frame, bg='#f0f8ff')
        button_frame.pack(expand=True)
        
        ttk.Button(button_frame, text="Search for Keywords", 
                  command=self.search_by_keyword, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="Search by Category", 
                  command=self.search_by_category, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="Search by Country", 
                  command=self.search_by_country, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="List All Headlines", 
                  command=self.list_all_headlines, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="Back to Main Menu", 
                  command=self.create_main_window, style='Custom.TButton', 
                  width=30).pack(pady=20)
    
    def show_sources_menu(self):
        """Show sources menu"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text="Sources Menu", style='Title.TLabel').pack(pady=(0, 30))
        
        # Menu buttons
        button_frame = tk.Frame(main_frame, bg='#f0f8ff')
        button_frame.pack(expand=True)
        
        ttk.Button(button_frame, text="Search by Category", 
                  command=self.sources_by_category, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="Search by Country", 
                  command=self.sources_by_country, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="Search by Language", 
                  command=self.sources_by_language, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="List All Sources", 
                  command=self.list_all_sources, style='Custom.TButton', 
                  width=30).pack(pady=10)
        ttk.Button(button_frame, text="Back to Main Menu", 
                  command=self.create_main_window, style='Custom.TButton', 
                  width=30).pack(pady=20)
    
    def search_by_keyword(self):
        """Search headlines by keyword"""
        keyword = simpledialog.askstring("Keyword Search", "Enter keyword to search for:")
        if keyword and keyword.strip():
            request_data = {'type': 'headlines', 'keyword': keyword.strip()}
            self.send_request_and_display(request_data, 'headlines')
    
    def search_by_category(self):
        """Search headlines by category"""
        categories = ['business', 'general', 'health', 'science', 'sports', 'technology']
        category = self.show_selection_dialog("Select Category", categories)
        if category:
            request_data = {'type': 'headlines', 'category': category}
            self.send_request_and_display(request_data, 'headlines')
    
    def search_by_country(self):
        """Search headlines by country"""
        countries = ['au', 'ca', 'jp', 'ae', 'sa', 'kr', 'us', 'ma']
        country_names = ['Australia', 'Canada', 'Japan', 'UAE', 'Saudi Arabia', 'South Korea', 'USA', 'Morocco']
        
        selection = self.show_selection_dialog("Select Country", 
                                             [f"{name} ({code.upper()})" for name, code in zip(country_names, countries)])
        if selection:
            # Extract country code from selection
            country_code = selection.split('(')[1].split(')')[0].lower()
            request_data = {'type': 'headlines', 'country': country_code}
            self.send_request_and_display(request_data, 'headlines')
    
    def list_all_headlines(self):
        """List all headlines"""
        request_data = {'type': 'headlines', 'country': 'us'}  # Default country required
        self.send_request_and_display(request_data, 'headlines')
    
    def sources_by_category(self):
        """Search sources by category"""
        categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        category = self.show_selection_dialog("Select Category", categories)
        if category:
            request_data = {'type': 'sources', 'category': category}
            self.send_request_and_display(request_data, 'sources')
    
    def sources_by_country(self):
        """Search sources by country"""
        countries = ['us', 'gb', 'ca', 'au', 'de']
        country_names = ['USA', 'United Kingdom', 'Canada', 'Australia', 'Germany']
        
        selection = self.show_selection_dialog("Select Country", 
                                             [f"{name} ({code.upper()})" for name, code in zip(country_names, countries)])
        if selection:
            country_code = selection.split('(')[1].split(')')[0].lower()
            request_data = {'type': 'sources', 'country': country_code}
            self.send_request_and_display(request_data, 'sources')
    
    def sources_by_language(self):
        """Search sources by language"""
        languages = ['en', 'ar']
        language_names = ['English', 'Arabic']
        
        selection = self.show_selection_dialog("Select Language", 
                                             [f"{name} ({code})" for name, code in zip(language_names, languages)])
        if selection:
            language_code = selection.split('(')[1].split(')')[0]
            request_data = {'type': 'sources', 'language': language_code}
            self.send_request_and_display(request_data, 'sources')
    
    def list_all_sources(self):
        """List all sources"""
        request_data = {'type': 'sources'}
        self.send_request_and_display(request_data, 'sources')
    
    def show_selection_dialog(self, title, options):
        """Show selection dialog with radio buttons"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("350x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#f0f8ff')
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Title
        ttk.Label(dialog, text=title, style='Heading.TLabel').pack(pady=20)
        
        # Selection variable
        selected_var = tk.StringVar()
        
        # Create scrollable frame for options
        canvas = tk.Canvas(dialog, bg='#f0f8ff', height=250)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f8ff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add radio buttons
        for option in options:
            ttk.Radiobutton(scrollable_frame, text=option.title(), 
                           variable=selected_var, value=option).pack(pady=3, anchor='w')
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Result variable
        result = None
        
        def on_select():
            nonlocal result
            result = selected_var.get()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#f0f8ff')
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=10)
        
        dialog.wait_window()
        return result
    
    def send_request_and_display(self, request_data, request_type):
        """Send request to server and display results"""
        if not self.client:
            messagebox.showerror("Error", "Not connected to server")
            return
            
        try:
            response = self.client.send_request(request_data)
            
            if response:
                if response.get('type') == 'error':
                    messagebox.showerror("Server Error", response.get('message', 'Unknown error'))
                elif request_type == 'headlines':
                    self.display_headlines(response)
                elif request_type == 'sources':
                    self.display_sources(response)
            else:
                messagebox.showerror("Connection Error", "Failed to get response from server")
                
        except Exception as e:
            messagebox.showerror("Error", f"Request failed: {e}")
    
    def display_headlines(self, response):
        """Display headlines results"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text="Headlines Results", style='Title.TLabel').pack(pady=(0, 20))
        
        # Get articles
        articles = response.get('data', [])
        self.current_articles = response.get('full_data', [])
        
        if not articles:
            ttk.Label(main_frame, text="No headlines found", style='Heading.TLabel').pack(expand=True)
            ttk.Button(main_frame, text="Back", command=self.show_headlines_menu, 
                      style='Custom.TButton').pack(pady=20)
            return
        
        # Results frame with scrollbar
        results_frame = tk.Frame(main_frame, bg='#f0f8ff')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(results_frame, bg='#f0f8ff')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f8ff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display articles
        for i, article in enumerate(articles):
            article_frame = tk.Frame(scrollable_frame, relief=tk.RAISED, 
                                   borderwidth=1, bg='white', padx=10, pady=10)
            article_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Article title
            title_label = tk.Label(article_frame, text=f"{i}. {article['title']}", 
                                  font=('Arial', 12, 'bold'), bg='white', 
                                  wraplength=700, justify=tk.LEFT)
            title_label.pack(anchor=tk.W, pady=(0, 5))
            
            # Article info
            info_text = f"Source: {article['source']} | Author: {article['author']}"
            info_label = tk.Label(article_frame, text=info_text, 
                                 font=('Arial', 10), bg='white', fg='#666')
            info_label.pack(anchor=tk.W, pady=(0, 10))
            
            # Details button
            ttk.Button(article_frame, text="View Details", 
                      command=lambda idx=i: self.show_article_details(idx)).pack(anchor=tk.E)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bottom frame with info and back button
        bottom_frame = tk.Frame(main_frame, bg='#f0f8ff')
        bottom_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(bottom_frame, text=f"Total: {len(articles)} headlines", 
                 style='Info.TLabel').pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="Back to Headlines Menu", 
                  command=self.show_headlines_menu, style='Custom.TButton').pack(side=tk.RIGHT)
    
    def display_sources(self, response):
        """Display sources results"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text="Sources Results", style='Title.TLabel').pack(pady=(0, 20))
        
        # Get sources
        sources = response.get('data', [])
        self.current_sources = sources
        
        if not sources:
            ttk.Label(main_frame, text="No sources found", style='Heading.TLabel').pack(expand=True)
            ttk.Button(main_frame, text="Back", command=self.show_sources_menu, 
                      style='Custom.TButton').pack(pady=20)
            return
        
        # Results frame with scrollbar
        results_frame = tk.Frame(main_frame, bg='#f0f8ff')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(results_frame, bg='#f0f8ff')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f8ff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display sources
        for i, source in enumerate(sources):
            source_frame = tk.Frame(scrollable_frame, relief=tk.RAISED, 
                                  borderwidth=1, bg='white', padx=10, pady=10)
            source_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Source name
            name_label = tk.Label(source_frame, text=f"{i}. {source['name']}", 
                                 font=('Arial', 12, 'bold'), bg='white')
            name_label.pack(anchor=tk.W, pady=(0, 5))
            
            # Source info
            info_text = f"Country: {source['country']} | Category: {source['category']} | Language: {source['language']}"
            info_label = tk.Label(source_frame, text=info_text, 
                                 font=('Arial', 10), bg='white', fg='#666')
            info_label.pack(anchor=tk.W, pady=(0, 10))
            
            # Details button
            ttk.Button(source_frame, text="View Details", 
                      command=lambda src=source: self.show_source_details(src)).pack(anchor=tk.E)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bottom frame
        bottom_frame = tk.Frame(main_frame, bg='#f0f8ff')
        bottom_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(bottom_frame, text=f"Total: {len(sources)} sources", 
                 style='Info.TLabel').pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="Back to Sources Menu", 
                  command=self.show_sources_menu, style='Custom.TButton').pack(side=tk.RIGHT)
    
    def show_article_details(self, article_id):
        """Show detailed article information"""
        request_data = {'type': 'details', 'article_id': article_id}
        
        try:
            response = self.client.send_request(request_data)
            
            if response and response.get('type') == 'article_details':
                data = response['data']
                
                # Create details window
                details_window = tk.Toplevel(self.root)
                details_window.title("Article Details")
                details_window.geometry("700x600")
                details_window.configure(bg='#f0f8ff')
                
                # Center window
                details_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
                
                # Title
                ttk.Label(details_window, text="Article Details", style='Title.TLabel').pack(pady=20)
                
                # Scrollable text widget
                text_frame = tk.Frame(details_window, bg='#f0f8ff')
                text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                       font=('Arial', 11), bg='white')
                text_widget.pack(fill=tk.BOTH, expand=True)
                
                # Format article details
                details_text = f"""TITLE
{data.get('title', 'N/A')}

SOURCE
{data.get('source', 'N/A')}

AUTHOR
{data.get('author', 'N/A')}

PUBLISHED
{data.get('publishedAt', 'N/A')}

URL
{data.get('url', 'N/A')}

DESCRIPTION
{data.get('description', 'N/A')}

CONTENT
{data.get('content', 'N/A')}"""
                
                text_widget.insert(tk.END, details_text)
                text_widget.config(state=tk.DISABLED)
                
                # Close button
                ttk.Button(details_window, text="Close", 
                          command=details_window.destroy, style='Custom.TButton').pack(pady=20)
                
            else:
                messagebox.showerror("Error", "Failed to retrieve article details")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get article details: {e}")
    
    def show_source_details(self, source):
        """Show detailed source information"""
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title("Source Details")
        details_window.geometry("600x500")
        details_window.configure(bg='#f0f8ff')
        
        # Center window
        details_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Title
        ttk.Label(details_window, text="Source Details", style='Title.TLabel').pack(pady=20)
        
        # Details frame
        details_frame = tk.Frame(details_window, bg='white', relief=tk.RAISED, borderwidth=2)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Source information
        info_text = f"""NAME
{source.get('name', 'N/A')}

COUNTRY
{source.get('country', 'N/A').upper()}

CATEGORY
{source.get('category', 'N/A').title()}

LANGUAGE
{source.get('language', 'N/A').upper()}

URL
{source.get('url', 'N/A')}

DESCRIPTION
{source.get('description', 'N/A')}"""
        
        text_widget = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, 
                                               font=('Arial', 11), bg='white')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(details_window, text="Close", 
                  command=details_window.destroy, style='Custom.TButton').pack(pady=20)
    
    def quit_app(self):
        """Quit the application"""
        try:
            if self.client and self.client.socket:
                self.client.socket.close()
        except:
            pass
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        # Show connection dialog
        username = self.show_connection_dialog()
        
        if not username:
            return
        
        # Setup client
        self.client = NewsClient()
        self.client.username = username
        
        # Connect to server
        if self.client.connect():
            self.connected = True
            self.create_main_window()
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
            
            # Start GUI main loop
            self.root.mainloop()
        else:
            messagebox.showerror("Connection Error", "Failed to connect to server")

if __name__ == "__main__":
    app = NewsClientGUI()
    app.run()
