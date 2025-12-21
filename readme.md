# planning agent with repl

# how to run:

```bash
git clone https://github.com/Grigory-T/plan_repl_agent
cd plan_repl_agent
docker compose build && docker compose up -d
```

then create .env file with OPENROUTER_API_KEY

```bash
# write some task in runner.py
# use e.g. task_sample variable
python3 runner.py
```


# files and folders overivew
/agent - main code  
/lib - technical folder for agent, realted to `pip install` functionality  
/logs - all steps with detaild thinking process. shows agent logic. logs based on .txt files  
/work - agent working directory, for file operations  
/runner.py - use to start agent


# important notes:
- agent runs in docker
- agent can execute python and bash commands (take into account security issues)
- agent can pip install
- agent cannot apt-get


