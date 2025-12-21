import requests
import time
import sys
from typing import Optional
import sys

BASE_URL = "http://localhost:8000"


def run_task(task: str) -> dict:
    response = requests.post(f"{BASE_URL}/run", json={"task": task})
    response.raise_for_status()
    return response.json()


def list_tasks() -> dict:
    response = requests.get(f"{BASE_URL}/tasks")
    response.raise_for_status()
    return response.json()


def reset() -> dict:
    response = requests.get(f"{BASE_URL}/reset")
    response.raise_for_status()
    return response.json()


task_sample = """

https://erc.timetoact-group.at/assets/erc3.html

this is llm agent competition website
analyze the `Ultimate Leaderboard` section
consider 10 first places, with highest scores
write your conclusions about the architecture of the best llm agents (in report.md file, CWD)
what do they have in common and what unique features agents implement
any other interesting observations you can make

""".strip()

run_task(task_sample)
time.sleep(0.5)
print(list_tasks())
















# ниже еще ряд задачек на которых тестировал агента, не все он выполняет успешно, но результаты интересные



task1 = """

Твоя задача - скачать все отчеты по компании "ПАО «ИК РУСС-ИНВЕСТ»" с сайта (можно в CWD).
Нам нужно классифицировать каждый такой отчет:
- сканы (картинки)
- OCR текст (исходный скан, но со слоем текста)
- digital pdf (pdf с текстом, изначально цифровой)

Разработай критерии классификации (подумай хорошенько, возможно неочевидные критерии нужны). И примени их.
После получения результата, оцени его общую адекватность. Если что-то не так, то исправь.

Результат запиши в файл result.md в CWD. Должна быть таблица, количество строк - количество pdf по "ПАО «ИК РУСС-ИНВЕСТ»".

сайт:
https://rspp.ru/tables/non-financial-reports-library/

""".strip()


task2 = """

Твоя задача - получить список всех участников выставки на сайте с указанием стендов, названия компаний, залов, стран компаний и прочая полезная информация. Сильно детально не надо, т.е. информация о продуктах - не загружай.
Будь внимателен, там есть сложные моменты связанные с парсингом. Надо разобраться как устроен сайт.
Сначала изучи детально строение сайта и как информация хранится на нем. Посмотри как лучше парсить html или ajax запросы делать.
Обязательно убедись, что мы нашли всех участников выставки, на всех страницах. НЕ ПРОПУСТИ НИЧЕГО.

В результатне надо получить таблицу. Каждая строчка - один участник. Вся информация про участника - в столбцах.
Таблицу запиши в csv файл.

сайт выставки:
https://exhibitors-itegroup.exhibitoronlinemanual.com/yugagro-2025/ru/Exhibitor

используй только папку: exebition

""".strip()



task3 = """

We have file: `employee_skills.md` (see CWD, ./employee/employee_skills.md)
We need to segment all employees into three groups:
- technical specialists
- managers and project leads
- executives and board members
If direct information is not available, try to infer this from the context or from indirect logic.
Use some heuristics to segment employees.

You should work only in ./employee folder.

""".strip()


task4 = """

Нам надо рассчитать примерный расход бензина (АИ92) на транспортировку 2 тонн металла.
Мы используем грузовую Газель.
Расход надо посчитать не по прямой, а по реальному транспортному расстоянию.
Нужна оценка стоимости бензина в рублях, столько будет это стоить в одну сторону.
Сохрани расчеты и результат в файл.

Пункт отправления: г. Химки.
Пункт назначения: г.Тверь. (резина уже поменяна).

используй только папку: fuel

""".strip()


task5 = """

dev_functions.py - useful utility functions, you can use them to complete the task.
main.py, store_agent.py - these two files contain full example of code, how to start and execute the task. pay attention.

ERC3_API_KEY is in env already. Do not worry about it.
erc3 lib already installed. Do not worry about it.

you can use CWD (/apt/work/ folder) - to store files and data, if needed.

YOU TASK - solve the task number 1 from the competition site: `Buy ALL GPUs, gpu_race`

other rules:
- **solve the task yourself, your are LLM agent**.
- call api helper functions from erc3 library in chat and see results immediately.
- DO NOT use openai api or openrouter api.

""".strip()



task_32b = """

create hometask.py
write some clojure code init
save file to CWD

""".strip()



task_fm = """

we have python l:list[str]
len(l) == 1000
len(set(l)) == 1000
we have function f(s1, s2) -> float: from 0 to 1, similarity score of two strings.
we need to delete minimal number of strings from l, so that no two strings in l have similarity score > 0.5
propose algorithm to solve this problem.

""".strip()




sometask = """

We've got this question about the room assignment. We, as a company, we're going to the trip, not the business trip, like a rest in the countryside house. And we need to assign pairs of persons. We have approximately 1,000 people, and each one states with whom he wants to stay. And each... we have only men in our company, just men. So anybody can pair up, and it's okay. But each person stated with whom he wants to stay. It could be 0 or M candidates, options. So we have a big table with the desire, with the... what people want. For example, the person A wants to be with F, D and G, something like this. But with 1,000 persons. So we need to optimize it somehow. Propose how we can optimize and pair persons appropriately. If some information or inputs are missing, just think of the common sense options. But you need to propose some kind of approach algorithm to assign. And each... it's very important. There is an infinite number of homes, and each home can contain exactly two persons. So 1,000, for example, it's... even a number of persons. We basically need to pair them up like 5,000 homes. But how can we do it optimally? Taking into account the information they expressed, and their desire, and their position, their desired adoption.

""".strip()


test = """

you task is to try out tool FTA (Flat Table Analysis) and state you opinion about it (in report.md file, CWD)
download any table to test, any table with interesting relations between columns

# FTA code example:
!pip install flattableanalysis
from flattableanalysis.flat_table_analysis import FlatTableAnalysis
df = pd.DataFrame(YOUR_DATA)
fta = FlatTableAnalysis(df)  # create analysis object
fta.get_candidate_keys(2)  # check 2-cols candidates
fta.show_fd_graph()[0]  # see graph of functional dependencies (all pairs of columns)

you can use CWD folder to store files and data, if needed.

""".strip()



