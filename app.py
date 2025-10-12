from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

PATH_STATIC = Path(__file__).parent / 'static'
app = FastAPI()
app.mount('/static', StaticFiles(directory=PATH_STATIC), name='static')

@app.get('/{full_path:path}')
async def index(full_path: str):
	# 处理api路由与static路由
	if full_path.startswith("api/") or full_path.startswith("static/"):
		raise HTTPException(status_code=404, detail="Not found")
	
	# 其他请求返回index.html
	return FileResponse(PATH_STATIC / "index.html")

if __name__ == '__main__':
	uvicorn.run(
		app,
		host='127.0.0.1',
		port=8000
	)