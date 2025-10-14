from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import api
from pathlib import Path
import uvicorn
from utils import dbengine

PATH_ROOT = Path(__file__).parent
PATH_STATIC = PATH_ROOT / 'static'
app = FastAPI(title='AI教师后端API', version='0.0.1', description='这是后端提供的所有API接口，若有未尽之处还请提出。')
app.mount('/static', StaticFiles(directory=PATH_STATIC), name='static')
app.include_router(api.router)

@app.get('/{full_path:path}', summary='前端入口', description='''\
除了对`/api`和`/static`开头的url发送的请求，其它所有请求都将响应`/static/index.html`。\n
对于`/api`和`/static`开头的链接，在没有对应API或静态资源时，会响应404。
''')
def index(full_path: str):
	# 处理api路由与static路由
	if full_path.startswith("api/") or full_path.startswith("static/"):
		raise HTTPException(status_code=404, detail="Not found")
	
	# 其他请求返回index.html
	return FileResponse(PATH_STATIC / "index.html")

if __name__ == '__main__':
	uvicorn.run(
		'app:app',
		host='127.0.0.1',
		port=8000,
		reload=True
	)