import subprocess
import json
import sys
import os
import logging

logger = logging.getLogger("healthsphere.mcp_client")

class MCPClient:
    def __init__(self):
        self.process = None

    def start(self):
        """Start the MCP server subprocess and perform initialization."""
        try:
            python_exe = sys.executable
            # Ensure workspace directory is in the PYTHONPATH so python can import Capstone
            env = os.environ.copy()
            cwd = os.getcwd()
            # If the current working directory doesn't have backend, look upwards
            if not os.path.exists(os.path.join(cwd, "backend")):
                # Fallback to parent path of backend
                cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

            env["PYTHONPATH"] = cwd + os.pathsep + env.get("PYTHONPATH", "")
            
            server_path = os.path.join(cwd, "backend", "app", "mcp", "server.py")
            logger.info(f"Launching MCP Server subprocess: {python_exe} {server_path}")

            self.process = subprocess.Popen(
                [python_exe, server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, # Capture log outputs to stderr to not pollute stdout
                text=True,
                bufsize=1,
                env=env
            )

            # Send initialization handshake
            init_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"clientInfo": {"name": "HealthSphereClient", "version": "1.0"}}
            }
            self._write(init_req)
            init_resp = self._read()
            logger.info("MCP Handshake complete.")
            return init_resp
        except Exception as e:
            logger.error(f"Failed to start MCP Server process: {e}")
            self.process = None
            raise e

    def _write(self, msg: dict):
        if not self.process or self.process.stdin is None:
            raise RuntimeError("MCP process not running.")
        self.process.stdin.write(json.dumps(msg) + "\n")
        self.process.stdin.flush()

    def _read(self) -> dict:
        if not self.process or self.process.stdout is None:
            raise RuntimeError("MCP process not running.")
        line = self.process.stdout.readline()
        if not line:
            return {}
        try:
            return json.loads(line)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from MCP server: {e} (Line: {line})")
            return {"error": {"message": f"Parse error: {str(e)}"}}

    def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool via the MCP server using standard JSON-RPC tools/call."""
        # Auto-start if not running
        if not self.process or self.process.poll() is not None:
            self.start()

        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        try:
            self._write(req)
            resp = self._read()
        except Exception as e:
            logger.error(f"Failed standard communication with MCP server: {e}")
            # Try to restart once
            self.start()
            self._write(req)
            resp = self._read()

        if "error" in resp:
            raise RuntimeError(f"MCP server returned error: {resp['error'].get('message', 'Unknown error')}")

        content_list = resp.get("result", {}).get("content", [])
        if content_list:
            return content_list[0].get("text", "")
        return ""

    def stop(self):
        """Safely terminate the subprocess."""
        if self.process:
            logger.info("Stopping MCP server subprocess...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

# Global Client Instance
mcp_client = MCPClient()
