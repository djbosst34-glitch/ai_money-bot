FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install requests schedule
CMD ["python", "bot.py"]
