ARG PYTHON_VERSION=3.13-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install PostgreSQL + OpenCV/YOLO system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxcb1 \
    libxrender-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /code

ENV SECRET_KEY "RZlOkYKLQN7fKo8v5zSYI1hLw77y031UvCJ9d09Hc7tMIprKiD"

# Set environment variables for headless YOLO
ENV MPLBACKEND=Agg
ENV QT_QPA_PLATFORM=offscreen
ENV OPENCV_VIDEOIO_DEBUG=0

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:8080 --workers 2 nutriscan.wsgi
