# ITNE352-Project-GroupGA17





 News Client–Server Application

a. Project Title

  News Client–Server Application Using TCP Sockets and NewsAPI

---

b. Project Description

This project implements a client–server news application using Python, TCP socket programming, and JSON-based communication. The system allows multiple clients to connect to a central server and request news data such as top headlines, available news sources, and article details.

The server communicates with the external NewsAPI service to fetch real-time news data, processes client requests, and sends structured responses back to the clients. Two types of clients are supported:

 A console-based client
 A GUI-based client developed using Tkinter

The project demonstrates key networking and software engineering concepts such as client–server architecture, multithreading, API integration, and modular design.

---

c. Semester

  First Semester – Academic Year 2025 / 2026

---

d. Group Information

  Group Name: Group GA17
  Course Code: ITNE352
  Section: 1

Group Members

| Student Name        | Student ID |
| ------------        | ---------- |
| Abdelaziz Ghassoul  | 202306788  |
| Mohammed Mulham     | 202303566  |

---

e. Table of Contents

1. Project Title
2. Project Description
3. Semester
4. Group Information
5. Requirements
6. How to Run the System
7. Scripts Description
8. Additional Concepts
9. Acknowledgments
10. Conclusion
11. Resources

---

f. Requirements




ITNE352-Project-Group GA17
├─ server.py
├─ client.py
├─ gui_client.py
├─ README.md




   Interacting with the Server

  Enter a username when prompted
  Choose one of the available options:

    View top headlines
    Search headlines by keyword/category/country
    List news sources
    View article or source details

All communication is handled transparently using JSON messages over TCP sockets.

---

h. The Scripts

   server.py

  Purpose: Acts as the central news server.

  Main Functionalities:

  Accepts multiple client connections
  Processes JSON requests
  Communicates with NewsAPI
  Sends structured responses to clients

  Key Libraries:

   python
import socket
import threading
import requests
import json
```

   Main Classes & Functions:

  NewsServer
  start_server()
  handle_client()
  process_request()

---

   client.py

  Purpose: Console-based client for interacting with the server.

  Main Functionalities:

  Displays text-based menus
  Sends user requests to server
  Receives and displays responses

  Key Concepts:

 TCP socket communication
 JSON serialization

---

  gui_client.py

  Purpose: Graphical client application using Tkinter.

  Main Functionalities:

 User-friendly GUI
 Displays headlines and sources in scrollable views
 Opens detailed views in separate windows

  Key Libraries:

  python
import tkinter as tk
from tkinter import ttk


  Main Classes:

  NewsClient
  NewsClientGUI

---


---

i. Additional Concepts

 Multithreading

The server uses **threading** to handle multiple clients simultaneously:

  python
threading.Thread(target=self.handle_client, args=(client_socket, address))


  JSON

All communication between client and server is structured using JSON:

   json
{
  "type": "headlines",
  "category": "technology"
}


GUI Event-Driven Programming

The GUI client responds to user actions such as button clicks and menu selections using Tkinter event handlers.

---

j. Acknowledgments

We would like to thank:

  Our course instructor for guidance and support
  The developers of NewsAPI for providing public news data
  Online documentation and Python community resources

---

k. Conclusion

This project successfully demonstrates a complete client–server system using Python. By combining socket programming, API integration, and GUI development, the project provides a practical implementation of networking concepts covered in the course. The modular design allows easy extension and future improvements.

