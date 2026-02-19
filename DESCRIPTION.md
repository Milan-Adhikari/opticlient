# opticlient

A lightweight Python client for interacting with the SaaS optimization API.  
This package provides a clean interface for submitting optimization jobs, polling their status, and retrieving results.

Currently supported tools:
- **MAXSAT** - solves a .wcnf instance in the format of "maxsat evaluation" - post 2022
- **Single Machine Scheduling (sms)** — submit an Excel instance and obtain an ordered job schedule.

More tools will be added in future versions.

For details visit: https://github.com/Milan-Adhikari/opticlient 

---

## Installation

```bash
pip install opticlient
```

## Quick Usage Guide
opticlient requires an **API key**, which you obtain from the website https://cad-eta.vercel.app

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

## Quick Start: Single Machine Scheduling (SMS)

The SMS tool takes an Excel file describing a scheduling instance and returns an ordered sequence of jobs. You can download the sample Excel file from https://cad-eta.vercel.app or see below.

#### Basic usage
```bash
# use case for maxsat
from opticlient import OptiClient

client = OptiClient()  # reads token/base URL from environment if available
# set the file path first (!!! necessary)
client.maxsatSolver.set_file("test.wcnf")
solution = client.maxsatSolver.optimize()

print("Solution:", solution)
```
```bash
# use case for single machine scheduling problem
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

## Sample .wcnf File format
c Example WCNF file (post-2023 MaxSAT Evaluation format)
c Offset: 0

h 1 -2 3 0
h -1 4 0

5 2 -3 0
3 -4 0
1 5 0

## Sample Excel File format
| Job   | Job1 | Job2 | Job3 | Job4 |
|-------|------|------|------|------|
| Job1  |   0  |   2  |   1  |   1  |
| Job2  |   3  |   0  |   1  |   1  |
| Job3  |   5  |   4  |   1  |   2  |
| Job4  |   2  |   2  |   1  |   0  |

## Versioning
This package follows semantic versioning:

* 0.x — early releases, API may change
* 1.0+ — stable API