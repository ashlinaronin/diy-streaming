FROM python:3.11-slim
WORKDIR /app
COPY mock_slskd.py /app/mock_slskd.py
RUN pip install flask
EXPOSE 5030
CMD ["python", "mock_slskd.py"]
