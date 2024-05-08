FROM alpine:latest

RUN apk update && \
    apk add --no-cache python3 py3-pip python3-dev && \
    python3 -m venv /venv

# Thiết lập biến môi trường để sử dụng môi trường ảo
ENV PATH="/venv/bin:$PATH"
ENV KEY="facebook_api"
ENV DATABASE_URL="sqlite:///facebook.db"
ENV SQLALCHEMY_DATABASE_URI="sqlite:///facebook.db"
ENV JWT_SECRET_KEY="facebook-dev"
ENV SECRET_KEY="facebook-secret"

WORKDIR /app
COPY . /app

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
