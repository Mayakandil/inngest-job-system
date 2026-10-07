# Inngest Background Job System

A FastAPI application demonstrating background job processing with Inngest.

The project demonstrates asynchronous background jobs, job status polling, retries, input validation, and scheduled cron jobs.

## Tech Stack

- Python
- FastAPI
- Inngest
- Uvicorn
- Pydantic

## Setup

Clone the repository and enter the project directory.

Create a virtual environment:

    python3 -m venv venv

Activate it:

    source venv/bin/activate

Install the dependencies:

    pip install -r requirements.txt

## Run the Project

The application requires two terminals.

### Terminal 1 — FastAPI

    INNGEST_DEV=1 uvicorn main:app --reload --port 8000

The API will run at:

    http://localhost:8000

### Terminal 2 — Inngest Dev Server

    npx inngest-cli@latest dev -u http://localhost:8000/api/inngest

The Inngest dashboard will be available at:

    http://localhost:8288

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/reports` | Create a new background report job |
| GET | `/reports/{id}` | Get the current report status and result |
| GET/POST/PUT | `/api/inngest` | Inngest serve endpoint |

## Example

Create a report:

    curl -i -X POST http://localhost:8000/reports \
    -H "Content-Type: application/json" \
    -d '{"topic":"cats"}'

The API immediately returns `202 Accepted`:

    {
      "id": "<report-id>",
      "topic": "cats",
      "status": "pending"
    }

Check the report:

    curl http://localhost:8000/reports/<report-id>

Initially, the report may be:

    {
      "id": "<report-id>",
      "topic": "cats",
      "status": "pending"
    }

After the background job completes:

    {
      "id": "<report-id>",
      "topic": "cats",
      "status": "done",
      "result": "Report about cats"
    }

## Stage 2 — Background Jobs

`POST /reports` returns `202 Accepted` immediately while the slower report generation runs in the background.

Clients can poll `GET /reports/{id}` to observe the report transition from `pending` to `done`.

This demonstrates eventual consistency: the API accepts the request immediately, while the final result becomes available later.

## Stage 3 — Retries and Validation

The `make-report` function is configured with two retries.

When the topic is `fail`, the background job intentionally raises an error:

    The report oven is broken!

Inngest retries the failed job automatically. With two retries, the job can run up to three attempts before its final status becomes `Failed`.

Invalid input is different from a background failure. A request without a topic is rejected immediately with HTTP `400` because retrying cannot fix invalid client input, while a temporary background-job failure may succeed on retry.

## Stage 4 — Cron Heartbeat

The `heartbeat` function uses the following test schedule:

    * * * * *

This runs once every minute.

A cron expression contains five fields:

    minute hour day-of-month month day-of-week

To run every day at 08:00:

    0 8 * * *

To run every Sunday at 22:00:

    0 22 * * 0

Cron schedules should be checked against the server's timezone; servers commonly use UTC.

The heartbeat reports the number of reports currently in the `pending`, `done`, and `failed` states.

## Dashboard

The Inngest development dashboard shows background job runs, individual steps, retries, failures, and scheduled heartbeat runs.

![Inngest Dashboard](inngest-job-system/screenshots.png)
## Notes

Reports are stored in an in-memory Python dictionary for this assignment. Therefore, report data is lost whenever the FastAPI server restarts.

The one-minute heartbeat cron schedule is intended for local testing.