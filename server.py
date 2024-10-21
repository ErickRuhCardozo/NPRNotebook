import os
import sqlite3
import uvicorn
from fastapi import FastAPI


def factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def main():
    app = FastAPI()

    @app.get('/closures')
    async def closures():
        conn = sqlite3.connect(os.path.expanduser(r'~\closures.db3'))
        conn.row_factory = factory
        cur = conn.execute('SELECT * FROM closures')
        return cur.fetchall() or {'empty': True}
    
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()