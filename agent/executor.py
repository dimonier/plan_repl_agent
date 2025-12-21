import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pydantic import BaseModel
import subprocess

PERSISTENT_GLOBALS = {
    "__builtins__": __builtins__,
}

class CodeResponse(BaseModel):
    stdout: str
    stderr: str
    globals: dict = None

def execute_python(code: str):
    import os

    os.chdir('/app/work')
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, PERSISTENT_GLOBALS)
        
        return CodeResponse(
            stdout=stdout_capture.getvalue(),
            stderr="",
            globals=PERSISTENT_GLOBALS,
        )
    except Exception as e:
        return CodeResponse(
            stdout=stdout_capture.getvalue(),
            stderr=traceback.format_exc(),
            globals=PERSISTENT_GLOBALS,
        )


def execute_bash(code: str) -> CodeResponse:
    import os
    
    try:
        result = subprocess.run(
            ['bash', '-c', code],
            capture_output=True,
            text=True,
            cwd='/app/work',
            timeout=60,
        )
        return CodeResponse(
            stdout=result.stdout,
            stderr=result.stderr if result.returncode != 0 else "",
            globals=PERSISTENT_GLOBALS,
        )
    except subprocess.TimeoutExpired:
        return CodeResponse(
            stdout="",
            stderr="Command timed out after 60 seconds",
            globals=PERSISTENT_GLOBALS,
        )
    except Exception as e:
        return CodeResponse(
            stdout="",
            stderr=f"Bash execution error: {str(e)}",
            globals=PERSISTENT_GLOBALS,
        )