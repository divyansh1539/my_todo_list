# import json
# from http.server import BaseHTTPRequestHandler, HTTPServer

# tasks = []
# next_id = 1  

# class SimpleHandler(BaseHTTPRequestHandler):
#     def _set_headers(self, content_type="application/json"):
#         self.send_response(200)
#         self.send_header("Content-type", content_type)
#         self.send_header("Access-Control-Allow-Origin", "*")
#         self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
#         self.send_header("Access-Control-Allow-Headers", "Content-Type")
#         self.end_headers()

#     def do_OPTIONS(self):
#         self._set_headers()

#     def do_GET(self):
#         if self.path == "/tasks":
#             self._set_headers()
#             self.wfile.write(json.dumps({"tasks": tasks}).encode())
#         else:
#             self._set_headers("text/html")
#             try:
#                 with open("todos.html", "rb") as f:
#                     self.wfile.write(f.read())
#             except FileNotFoundError:
#                 self.wfile.write(b"File not found.")

#     def do_POST(self):
#         global next_id
#         if self.path == "/add":
#             content_length = int(self.headers["Content-Length"])
#             post_data = self.rfile.read(content_length)
#             data = json.loads(post_data)

#             tasks.append({
#                 "id": next_id,
#                 "username": data.get("username", ""),
#                 "todo": data.get("todo", "")
#             })
#             next_id += 1

#             self._set_headers()
#             self.wfile.write(json.dumps({"tasks": tasks}).encode())

#     def do_DELETE(self):
#         global tasks
#         if self.path.startswith("/delete/"):
#             try:
#                 task_id = int(self.path.split("/")[-1])
#                 before_count = len(tasks)
#                 tasks = [t for t in tasks if t["id"] != task_id]
#                 if len(tasks) == before_count:
#                     self.send_error(404, "Task not found")
#                     return
#                 self._set_headers()
#                 self.wfile.write(json.dumps({"tasks": tasks}).encode())
#             except ValueError:
#                 self.send_error(400, "Invalid task ID")


# def run():
#     server = HTTPServer(("localhost", 8000), SimpleHandler)
#     print("Server running on http://localhost:8000")
#     server.serve_forever()

# if __name__ == "__main__":
#     run()

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
from dotenv import load_dotenv
import os

# MySQL connection
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),  # default fallback
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    todo TEXT
)
""")
conn.commit()

tasks = []

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        global tasks
        if self.path == "/tasks": 
            # Fetch tasks from MySQL
            cursor.execute("SELECT id, username, todo FROM tasks")
            rows = cursor.fetchall()
            tasks = [{"id": r[0], "username": r[1], "todo": r[2]} for r in rows]

            self._set_headers()
            self.wfile.write(json.dumps({"tasks": tasks}).encode())
        else:
            self._set_headers("text/html")
            try:
                with open("todos.html", "rb") as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"File not found.")

    def do_POST(self):
        if self.path == "/add":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            username = data.get("username", "")
            todo = data.get("todo", "")

            # Insert into MySQL
            cursor.execute("INSERT INTO tasks (username, todo) VALUES (%s, %s)", (username, todo))
            conn.commit()
            task_id = cursor.lastrowid

            tasks.append({
                "id": task_id,
                "username": username,
                "todo": todo
            })

            self._set_headers()
            self.wfile.write(json.dumps({"tasks": tasks}).encode())

    def do_DELETE(self):
        global tasks
        if self.path.startswith("/delete/"):
            try:
                task_id = int(self.path.split("/")[-1])
                
                # Delete from MySQL
                cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
                conn.commit()
                
                before_count = len(tasks)
                tasks = [t for t in tasks if t["id"] != task_id]
                if len(tasks) == before_count:
                    self.send_error(404, "Task not found")
                    return
                self._set_headers()
                self.wfile.write(json.dumps({"tasks": tasks}).encode())
            except ValueError:
                self.send_error(400, "Invalid task ID")


def run():
    server = HTTPServer(("localhost", 8000), SimpleHandler)
    print("Server running on http://localhost:8000")
    server.serve_forever()

if __name__ == "__main__":
    run() 