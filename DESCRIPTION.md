# opticlient

A lightweight Python client for interacting with the SaaS optimization API.  
This package provides a clean interface for submitting optimization jobs, polling their status, and retrieving results.

Currently supported tools:
- **MaxSAT** - solves a .wcnf instance in the format of "maxsat evaluation" - post 2022
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

You can provide it in either of three ways:

#### Option 1 - .env file (recommended)
```bash
# create a .env file and set the api token in it
OPTICLIENT_API_TOKEN="YOUR_API_KEY"
```

#### Option 2 - Environment variable
```bash
export OPTICLIENT_API_TOKEN="YOUR_API_KEY"
```

#### Option 3 - Pass directly in code
```bash
from opticlient import MaxSAT, OptiClient

solver = MaxSAT(api_token="YOUR_API_KEY")
client = OptiClient(api_token="YOUR_API_KEY")
```

### Basic usage: MaxSAT
```bash
# use case for maxsat
from opticlient import MaxSAT

# solving from a file
solver = MaxSAT("filename.wcnf")  # reads token/base URL from environment if available
x = solver.optimize()
print("solution:", x)

# solving without a file
solver = MaxSAT()  # reads token/base URL from environment if available
solver.addClause([1,2])
solver.addClause([-1,2])
solver.setObjective({2 : -1 })
x = solver.optimize()
print("solution:", x)
```

#### Sample .wcnf File format
```
c Example WCNF file (post-2023 MaxSAT Evaluation format)
c Offset: 0

h 1 -2 3 0
h -1 4 0

5 2 -3 0
3 -4 0
1 5 0
```

### Basic usage: Single Machine Scheduling
The SMS tool takes an Excel file describing a scheduling instance and returns an ordered sequence of jobs. You can download the sample Excel file from https://cad-eta.vercel.app or see below.
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



#### Sample Excel File format
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