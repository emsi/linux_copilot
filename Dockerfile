FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app
RUN ln -sf /data /app/data && ln -sf /client /app/client

WORKDIR /

CMD ["gunicorn", "app.main:app", "--bind", "[::]:80", "-k", "uvicorn.workers.UvicornWorker"]