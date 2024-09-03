FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y pkg-config libmariadb-dev libmariadb-dev-compat gcc
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .

CMD ["python", "-m", "lite_agent.main"]
