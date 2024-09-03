# lite-agent
## Install Dependencies
#### Need Python 3.10
```bash
pip3 install -r requirements.txt
```
## Setup Env
Complete the .env file with your own values
```bash
DASHSCOPE_API_KEY=your_dashscope_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
THREATBOOK_API=your_threatbook_api
```
## Run
### Development
```bash
fastapi dev app.py
```
### Production
```bash
unicorn main:app --port 8000 --workers 4 --log-level info
```
## Test
#### Test the API at http://localhost:8000/hello/Dustin
Get response like this:
```json
{"message": "Hello Dustin"}
```
#### Test the LLM with Neo4j at http://localhost:8000/llm/ask
Get request need a json body like this:
```json
{"query": "Who is the director of Casino?"}
```
Get response like this:
```json
{
	"code": 200,
	"status": "success",
	"query": "Who is the director of Casino?",
	"result": "Martin Scorsese is the director of Casino."
}
```

## Docs
Access the FastAPI Docs at http://localhost:8000/docs
