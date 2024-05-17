FROM python:3.12.3-slim-bookworm

WORKDIR /work

RUN apt update && apt install -y openssl

COPY /src/main.py main.py

CMD ["python", "main.py"]