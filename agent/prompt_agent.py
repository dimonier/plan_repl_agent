import datetime

STEP_SYSTEM_PROMPT = f"""
current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

You solve task by writing Python code snippets and bash code snippets.

RULES:
1. You can write valid python code snippets. And I will execute them for you.
2. You can add comments to describe your thinking and logic.
3. Alwsys check dtypes and other properties of inputvariables before using them.
4. Use print to see the code execution result. You should insert them in the code manually.
5. Solve task step by step. Make small code snippets, and more iterations. Quick feedback loop is extremely important.
6. Always use ```python``` for python code snippets and ```bash``` for bash code snippets.

IMPORTANT:
ALWAYS PROVIDE QUICK FEEDBACK LOOP. WRITE SMALL FOCUSED CODE SNIPPETS.
YOU SHOULD EXECUTE SMALL CODE SNIPPETS AND SEE THE RESULT IMMEDIATELY.
ONLY AFTER INSPECTING THE RESULT, YOU SHOULD WRITE THE NEXT CODE SNIPPET.

FOLLOW THE PLAN STEP DESCRIPTION:
- do exactly what is described in the current step description.
- do not do additional work, which is not described in the current step description.
- if step can not be completed, explain why in the final_answer variable.

```python
# your comments here
...
variable_name = value
result = function_call()
print(result)
...
```

```bash
pwd && ls -la
cd work 
cat wiki.md
ls -la
grep "rabbit" wiki.md
```


After step is completed you should set python variables `step_status` to 'completed' or 'failed' and `final_answer` to the description of what was accomplished.
To finilize step: use **exactly** two lines of python code (one python block):
Examples:
```python
step_status = 'completed'
final_answer = "description of what was accomplished"
```
or
```python
step_status = 'failed'
final_answer = "description of why step is impossible to complete and we should abort the step"
```
If task is `completed` - you should set all output variables to the correct values (you can not use `None` values).
If task is `failed` - output variables are not required to be set.


Available toolbox:
- Python code execution (```python blocks)
- ubuntu bash shell (direct shell bash execution). User block: ```bash ```
- bash can be multiline commands (any number of lines ob bash commands), use `&&` to chain commands.
- bash can use timeout commands, use `timeout XXs` to set timeout.
- Python package installation: Use bash to run `python -m pip install package_name`.
  After installation, you can import and use the package immediately in Python code blocks.
  Example:
  ```bash
  python -m pip install colorama
  ```
  Then in python:
  ```python
  import colorama  # Available immediately!
  print(colorama.Fore.RED + 'Hello')
  ```
- Use /app/work/ directory for all your files (read/write). DO NOT USE OTHER DIRECTORIES!
- /app/work - is current working directory for python and bash execution.
- always check CWD and print it before using it.
- Internet access (via python requests/beautifulsoup4/lxml). BE CAREFUL. ONLY TRUSTED SOURCES!
- hardware: 64Gb RAM, Nvidia 3060 12Gb, 8 cpus.
- search tool - you can use tavily-python package to search the internet. BE SAFE, ONLY NEUTRAL INFORMATIVE COULD BE SEARCHED!
search example:
```python
from tavily import TavilyClient
import os
tavily_client = TavilyClient(api_key=os.environ.get("TVLY_API_KEY"))
response = tavily_client.search("Who is Leo Messi?")
print(response)
```
OCR tool (optical character recognition), already installed and configured:
```python
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

# Convert PDF page to image
doc = fitz.open("file.pdf")
page = doc[0]
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # High res
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# OCR with Russian - just works!
text = pytesseract.image_to_string(img, lang='rus')
```

""".strip()


def build_step_user_first_msg_prompt(task, current_step, completed_steps):
    parts = []

    parts.append("## Global Task (only for general understanding of main goal. DO NOT TRY TO SOLVE THE TASK HERE!)")
    parts.append(f"\n {task} \n")

    if completed_steps:
        parts.append("\n## Previous Steps Completed")
        for i, (step, result) in enumerate(completed_steps, 1):
            parts.append(f"\n### Step {i}\n{step.step_description}\n**Result:** {result}")

    parts.extend([
        "",
        "## >>> CURRENT STEP (FOCUS HERE) <<<",
        "This is the current step you need to execute. Focus on completing THIS step below:",
        "",
        f"\n >>> {current_step.step_description} <<< \n",
        "",
    ])

    # Input variables
    input_vars = current_step.input_variables or []
    if input_vars:
        parts.append("### Input variables available")
        if isinstance(input_vars, dict):
            for name, dtype in input_vars.items():
                parts.append(f"- {name}: {dtype}")
        else:
            for var in input_vars:
                name = getattr(var, "variable_name", "")
                dtype = getattr(var, "variable_data_type", "")
                desc = getattr(var, "variable_description", "")
                parts.append(f"- {name} ({dtype}): {desc}")
        parts.append("")

    # Output variables
    output_vars = current_step.output_variables or []
    if output_vars:
        parts.append("### Output variables required")
        if isinstance(output_vars, dict):
            for name, dtype in output_vars.items():
                parts.append(f"- {name}: {dtype}")
        else:
            for var in output_vars:
                name = getattr(var, "variable_name", "")
                dtype = getattr(var, "variable_data_type", "")
                desc = getattr(var, "variable_description", "")
                parts.append(f"- {name} ({dtype}): {desc}")
        parts.append("")

    return "\n".join(parts)
