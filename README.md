# opticlient

A lightweight Python client for interacting with the SaaS optimization API.  
This package provides a clean interface for submitting optimization jobs, polling their status, and retrieving results.

Currently supported tools:

- **Single Machine Scheduling (sms)** — submit an Excel instance and obtain an ordered job schedule.

More tools will be added in future versions.

---

## Installation

```bash
pip install opticlient
```

## Installation
The Opti API requires an **API key**, which you obtain from the Opti web dashboard.

You can provide it in either of two ways:

#### Option 1 - Environment variable (recommended)
```bash
export OPTICLIENT_API_TOKEN="YOUR_API_KEY"
```

#### Option 2 - Pass directly in code
```bash
from opticlient import OptiClient

client = OptiClient(api_token="YOUR_API_KEY")
```

## Base URL Configuration
By default, the client uses the production API URL baked into the library.

To target a different server (e.g., local development)

#### Option 1 - Environment variable
```bash
export OPTICLIENT_BASE_URL="http://localhost:8000"
```

#### Option 2 - Pass directly in code
```bash
client = OptiClient(
    api_token="YOUR_API_KEY",
    base_url="http://localhost:8000",
)
```

## Quick Start: Single Machine Scheduling (SMS)

The SMS tool takes an Excel file describing a scheduling instance and returns an ordered sequence of jobs.

#### Basic usage
```bash
from opticlient import OptiClient

client = OptiClient()  # reads token/base URL from environment if available

schedule = client.sms.run(
    file_path="instance.xlsx",
    description="Test run",
)

print("Job schedule:")
for job in schedule:
    print(job)
```

#### What ```sms.run()``` does

```client.sms.run()``` is a high-level wrapper that:

1. Validates your Excel file.
2. Submits it to the API.
3. Polls until the job completes.
4. Downloads the result ZIP in memory.
5. Parses output/jobs.txt and returns a simple Python list[str] representing the scheduled job order.

## Versioning
This package follows semantic versioning:

* 0.x — early releases, API may change
* 1.0+ — stable API

## License
MIT License
See ```LICENSE``` for details