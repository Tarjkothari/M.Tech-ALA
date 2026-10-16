# Distributed Chat System (Flask + RabbitMQ + Redis + Docker)

Run from this folder (Docker Desktop must be running):

    docker compose up --build -d
    docker compose ps

Send and read messages (Windows PowerShell: use curl.exe, or Git Bash / Postman):

    curl -X POST http://localhost:5000/messages -H "Content-Type: application/json" -d '{"user":"Alice","text":"Hello from Alice"}'
    curl http://localhost:5000/messages

RabbitMQ UI: http://localhost:15672  (guest / guest)

Scale workers:

    docker compose up -d --scale chat-worker=3
    docker compose logs -f chat-worker

Fault tolerance:

    docker compose stop chat-worker
    (POST a message -> still 202)
    docker compose start chat-worker
    curl http://localhost:5000/messages

Stop everything: docker compose down
Note: the worker retries until RabbitMQ is ready; the very first API request
right after startup can fail with 503 - wait ~15 seconds and retry.
