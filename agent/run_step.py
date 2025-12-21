import ast
from pathlib import Path
from typeguard import check_type

from .utils import llm, LLM_MODEL_AGENT, check_assigned_variables, format_step_variables
from .prompt_agent import STEP_SYSTEM_PROMPT, build_step_user_first_msg_prompt
from .executor import execute_python, execute_bash, PERSISTENT_GLOBALS
from .log import _append_step_log, _append_reasoning

MAX_ITERATIONS_PER_STEP = 30

def run_step(task, current_step, completed_steps, log_dir=None, step_index=0) -> str:
    step_folder = Path(log_dir) / f"step_{step_index}" if log_dir else None
    messages_log = step_folder / "messages.txt" if step_folder else None
    reasoning_log = step_folder / "reasoning.txt" if step_folder else None

    system_prompt = STEP_SYSTEM_PROMPT
    user_prompt = build_step_user_first_msg_prompt(
        task=task,
        current_step=current_step,
        completed_steps=completed_steps,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    _append_step_log(messages_log, "system", system_prompt)
    _append_step_log(messages_log, "user", user_prompt)

    for _ in range(MAX_ITERATIONS_PER_STEP):
        llm_response, llm_response_blocks, reasoning = llm(messages, model=LLM_MODEL_AGENT)

        if not llm_response_blocks:
            continue
        
        _append_reasoning(reasoning_log, reasoning)

        if all(block.block_type == "text" for block in llm_response_blocks):
            messages.append({"role": "assistant", "content": llm_response})
            _append_step_log(messages_log, "assistant", llm_response)
            user_msg = ("No valid code to execute. Use \n```python\n...\n```\nor \n```bash\n...\n```\nblocks to write code.\n"
                        "If step is completed you should set python variables `step_status: str` - 'completed' or 'failed' and `final_answer: str` - description of results.\n"
                        )
            messages.append({"role": "user", "content": user_msg})
            _append_step_log(messages_log, "user", user_msg)
            continue

        pending_text = []
        python_blocks = []
        pair_idx = 0  # numbering for code/result pairs in logs

        for block in llm_response_blocks:
            if block.block_type == "text":
                pending_text.append(block.block_text)
                continue

            if block.block_type not in ("python", "bash"):
                continue

            code_type = block.block_type
            code = block.block_text

            assistant_msg = "".join(pending_text) + f"```{code_type}\n{code}\n```"
            pending_text = []
            messages.append({"role": "assistant", "content": assistant_msg})
            _append_step_log(messages_log, f"assistant {pair_idx}", assistant_msg)

            if code_type == "python":
                code_response = execute_python(code)
                python_blocks.append(code)
            elif code_type == "bash":
                code_response = execute_bash(code)
            else:
                user_msg = f"Unknown code type: {code_type}"
                messages.append({"role": "user", "content": user_msg})
                _append_step_log(messages_log, "user", user_msg)
                continue

            result_parts = []
            if code_response.stdout:
                result_parts.append(f"\n**STDOUT:**\n{code_response.stdout}")
            if code_response.stderr:
                result_parts.append(f"**STDERR:**\n{code_response.stderr}")
            block_result = "Code execution result:\n" + "\n\n".join(result_parts) if result_parts else "Code execution result: (no output)"

            messages.append({"role": "user", "content": block_result})
            _append_step_log(messages_log, f"user {pair_idx}", block_result)
            pair_idx += 1

        # If only text blocks existed, surface them once
        if pending_text and not python_blocks and not any(b.block_type == "bash" for b in llm_response_blocks):
            text_msg = "".join(pending_text)
            messages.append({"role": "assistant", "content": text_msg})
            _append_step_log(messages_log, "assistant", text_msg)

        # Was final_answer or step_status assigned in any python block?
        vars_assigned = any(check_assigned_variables(b) for b in python_blocks)
        final_answer = PERSISTENT_GLOBALS.get('final_answer', '')
        step_status = PERSISTENT_GLOBALS.get('step_status', '')

        # True only if exactly one python block exists AND it assigns both step_status and final_answer (order doesn't matter)
        twoline_oneblock_code = False
        if len(llm_response_blocks) == 1 and llm_response_blocks[0].block_type == "python" and len(ast.parse(llm_response_blocks[0].block_text).body) == 2:
            try:
                tree = ast.parse(python_blocks[0])
                targets = set()
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for t in node.targets:
                            if isinstance(t, ast.Name):
                                targets.add(t.id)
                            elif isinstance(t, (ast.Tuple, ast.List)):
                                for elt in t.elts:
                                    if isinstance(elt, ast.Name):
                                        targets.add(elt.id)
                if "final_answer" in targets and "step_status" in targets:
                    twoline_oneblock_code = True
            except Exception:
                pass

        if vars_assigned and final_answer and step_status and not twoline_oneblock_code:
            are_you_sure_msg = (
                'Make sure that the step is completed correctly and you understand the result.\n'
                'Analyze all the information above, facts and code execution results. You should base you descision on the information above.\n'
                f'The current step target was: >>>{current_step.step_description}<<<\n'
                f'The current step output variables (should be set if task is `completed`, `None` or empty containers ([], {{}} etc.) **is not allowed**):{format_step_variables(current_step.output_variables)}\n\n'

                'If you are sure you want to finilize step: use **exactly** two lines of code\n'
                "\n```python\nstep_status = 'completed' OR 'failed'\nfinal_answer = ...result description...\n```\n"

                'Do not include other codes blocks. Only one python code block with two assignments.'
            )
            messages.append({"role": "user", "content": are_you_sure_msg})
            _append_step_log(messages_log, "user", are_you_sure_msg)
            continue

        if vars_assigned and final_answer and step_status and twoline_oneblock_code:
            if step_status == 'failed':
                return final_answer

            error_msg = ""
            for var in current_step.output_variables:
                name = var.variable_name
                dtype_str = var.variable_data_type
                value = PERSISTENT_GLOBALS.get(name, None)
                if value is None:
                    error_msg += f'Missing variable: {name}\n'
                else:
                    if dtype_str == 'object':
                        continue
                    try:
                        glbs = dict(PERSISTENT_GLOBALS)
                        if 'pd' in glbs and 'pandas' not in glbs:
                            glbs['pandas'] = glbs['pd']
                        if 'np' in glbs and 'numpy' not in glbs:
                            glbs['numpy'] = glbs['np']
                        
                        dtype = eval(dtype_str, glbs)
                        check_type(value, dtype)
                    except Exception as e:
                        error_msg += (f'Error: {name} is {type(value).__name__} but expected literal python type: {dtype_str}\n'
                                        f'make sure that the variable {dtype_str} class exists verbatim in current python environment.\n'
                                        f'name of the class should be verbatim {dtype_str}, so re-import it if needed\n'
                                        f'examples of different imports: import pandas as pd VS import pandas; import numpy as np VS import numpy; etc\n'
                                        )
            if not error_msg:
                return final_answer
            
            messages.append({"role": "user", "content": error_msg})
            _append_step_log(messages_log, "user", error_msg)

    return "Max iterations reached without a final answer."
