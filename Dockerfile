FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=7860
EXPOSE 7860
# One worker on purpose: running jobs are kept in this process's memory.
CMD gunicorn -w 1 --threads 8 -b 0.0.0.0:${PORT} app:app
