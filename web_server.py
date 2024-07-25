import os
import sys
import subprocess
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        search_string = query_params.get('search', [None])[0]

        if parsed_path.path == "/gitGrep" and search_string:
            self.execute_and_respond(f"git grep -i '{search_string}'")
        elif parsed_path.path == "/gitDiff":
            self.execute_and_respond("git diff")
        elif parsed_path.path == "/gitLsFiles" and search_string:
            self.execute_and_respond("git ls-files '*{}*'".format(search_string))
        else:
            # Handle other requests normally
            super().do_GET()

    def execute_and_respond(self, command):
        # Execute the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Send response
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(stdout)
        if stderr:
            self.wfile.write(b"\nErrors:\n")
            self.wfile.write(stderr)

    def guess_type(self, path):
        if path.endswith(('.js', '.html', '.njk', '.css', '.json', '.log', '.py', '.php', '.sql')):
            return 'text/plain; charset=utf-8'
        return SimpleHTTPRequestHandler.guess_type(self, path)

def run(server_class=HTTPServer, handler_class=CustomHandler, directory=None, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    if directory:
        os.chdir(directory)
    print(f'Server running at http://localhost:{port}/ serving {directory or os.getcwd()}')
    httpd.serve_forever()

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else None
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    run(directory=directory, port=port)