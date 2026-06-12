import json
import http.server
import socketserver
from urllib.parse import urlparse

import open_taranis as T

def create_mcp_server(executor:T.Tools_Executor,
                      host: str = "localhost", 
                      port: int = 3000,
                      autres_infos=None
                    ) :
    assert type(executor) == T.Tools_Executor

    tools = T.functions_to_tools(
        [executor.tools_dict[name] for name in executor.tools_dict]
    )    

    mcp_tools = [
        {
            "name": t["function"]["name"],
            "description": t["function"]["description"],
            "inputSchema": t["function"]["parameters"]
        }
        for t in tools
    ]
    

    class MCPServer(http.server.BaseHTTPRequestHandler):
        
        def log_message(self, format, *args):
            # Silence les logs HTTP
            pass
        
        def do_POST(self):
            parsed = urlparse(self.path)
            
            if parsed.path != "/message":
                self.send_error(404)
                return
            
            # Lecture du body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                request = json.loads(body)
                response = self.handle_jsonrpc(request)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
        
        def handle_jsonrpc(self, request):
            """Route les méthodes JSON-RPC"""
            method = request.get('method')
            req_id = request.get('id')
            
            # Initialisation
            if method == 'initialize':
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {
                            "tools": {}  # On expose des tools, rien d'autre
                        },
                        "serverInfo": {
                            "name": "open_taranis_mcp",
                            "version": "1.0.0"
                        }
                    }
                }
            
            # Notification initialized (pas de réponse)
            elif method == 'notifications/initialized':
                return None  # Pas de réponse pour les notifications
            
            # Ping
            elif method == 'ping':
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {}
                }
            
            # Liste des outils
            elif method == 'tools/list':
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": mcp_tools
                    }
                }
            
            # Appel d'outil
            elif method == 'tools/call':
                params = request.get('params', {})
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                # Exécution
                try:
                    result = executor(
                        fname=tool_name,
                        args=arguments
                    )
                    
                    # Format MCP : content array avec type text
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": str(result) if not isinstance(result, str) else result
                                }
                            ],
                            "isError": False
                        }
                    }
                    
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error: {str(e)}"
                                }
                            ],
                            "isError": True
                        }
                    }
            
            # Méthode inconnue
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }
    
    return http.server.HTTPServer((host, port), MCPServer)