from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional, List
import zipfile

import tempfile
from collections.abc import Iterable

from ..config import _get_default_api_token, _get_default_base_url
from ..http import HttpClient, _parse_api_response_json
from ..models import JobSummary, JobDetails, job_summary_from_api
from .base import BaseJobClient


class MaxSAT(BaseJobClient):

    _SUBMIT_PATH = '/jobs/maxsat'
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        from_filepath: str = None
    ):
        if api_token is None:
            api_token = _get_default_api_token()
        if base_url is None:
            base_url = _get_default_base_url()
        
        if api_token is None:
            raise ValueError(
                "API token is required. Set OPTICLIENT_API_TOKEN env var "
                "or pass api_token=..."
            )
        self._http = HttpClient(
            base_url=base_url,
            api_token=api_token,
            timeout=timeout,
        )
        super().__init__(http=self._http)

        if from_filepath != None:
            if not isinstance(from_filepath, str):
                raise TypeError("from_filepath must be a string to the .wcnf file to initialize the solver with")
            if not from_filepath.endswith(".wcnf"):
                raise TypeError("from_filepath must be a .wcnf file to initialize the solver with")
            self.filepath = from_filepath
        else:
            self.filepath = None
            self.clauses = []
            self.objective = {}
            self.highestAtom = 0

    def addClause(self, clause: Iterable[int]):
        if self.filepath != None:
            raise TypeError("method not callable after solver initialization from file")
        self.clauses.append([lit for lit in clause])
        for lit in clause:
            if abs(lit)>self.highestAtom:
                self.highestAtom=abs(lit)

    def setObjective(self, objective: dict[int, int]):
        if self.filepath != None:
            raise TypeError("method not callable after solver initialization from file")
        self.objective={}
        for lit, coeff in objective.items():
            if abs(lit)>self.highestAtom:
                self.highestAtom=abs(lit)
            if coeff >0:
                self.objective[lit]=coeff
            elif coeff <0:
                self.objective[-lit]=-coeff

    def optimize(self):
        if self.filepath != None:
            filepathToSolve=self.filepath
            solution = self._solve_instance(filepathToSolve)
        else:
            with tempfile.NamedTemporaryFile(mode="w", delete=True) as f:
                f.write("\n".join("h "+" ".join([str(lit) for lit in clause])+" 0" for clause in self.clauses))
                for lit, coeff in self.objective.items():
                    f.write("\n"+str(coeff)+" "+str(lit)+"0")
                filepathToSolve=f.name
                solution = self._solve_instance(filepathToSolve)
        return solution

    def _wait(
        self,
        job_id: str,
        poll_interval: float = 2.0,
        timeout: Optional[float] = None,
    ) -> JobDetails:
        """
        Wait for job to complete.
        """
        return self._wait_for_completion(
            job_id=job_id,
            poll_interval=poll_interval,
            timeout=timeout,
        )
    
    def _get(self, job_id: str) -> JobDetails:
        """
        Get maxsat job details.
        """
        return self._get_job(job_id)
    
    def _submit(
        self,
        file_path: str | Path,
        description: Optional[str] = None,
    ) -> JobSummary:
        """
        Submit a maxsat job.

        Validates that the file exists and looks like an Excel file.
        Later we can add content validation here.
        """
        path = Path(file_path)

        # if not path.is_file():
        #     raise ValueError(f"Input file does not exist: {path}")

        # allowed_ext = {".wcnf"}
        # if path.suffix.lower() not in allowed_ext:
        #     raise ValueError(
        #         f"Expected a WCNF file with one of extensions {sorted(allowed_ext)}, "
        #         f"got {path.suffix!r}"
        #     )

        fields = {}
        if description is not None:
            fields["description"] = description

        with path.open("rb") as f:
            files = {
                "file": (path.name, f, "text/plain"),
            }
            resp = self._http._post(
                self._SUBMIT_PATH,
                files=files,
                data=fields,
            )

        data = _parse_api_response_json(resp)
        return job_summary_from_api(data)
    
    def _parse_solution_from_zip_bytes(self, zip_bytes: bytes) -> List[str]:
        """
        Read output/solution.txt from the given ZIP bytes

        Returns:
            model solution as strings.
        """
        try:
            with zipfile.ZipFile(BytesIO(zip_bytes)) as z:
                try:
                    with z.open("output/solution.txt") as f:
                        text = f.read().decode("utf-8")
                        result = [int(lit) for lit in text.split(" ")]
                except KeyError:
                    raise RuntimeError("Missing expected file 'solution/jobs.txt' in result ZIP")
        except zipfile.BadZipFile:
            raise RuntimeError("Result is not a valid ZIP file")

        return result
    
    def _solve_instance(
        self,
        filepathToSolve: str | Path,
        description: Optional[str] = None,
        poll_interval: float = 2.0,
        timeout: Optional[float] = None,
    ) -> List[str]:
        """
        Returns:
            List[str]: schedule of jobs in execution order.
        """
        summary = self._submit(file_path=filepathToSolve, description=description)
        job_id = summary.id

        # Ensure the job is completed (or error) before fetching results.
        self._wait(
            job_id=job_id,
            poll_interval=poll_interval,
            timeout=timeout,
        )

        # Download ZIP into memory only.
        resp = self._http._get(f"/jobs/{job_id}/result")
        if resp.status_code != 200:
            snippet = resp.text[:200]
            raise RuntimeError(
                f"Failed to download result for job {job_id} "
                f"(status={resp.status_code}): {snippet!r}"
            )

        zip_bytes = resp.content

        # Parse schedule from ZIP bytes.
        solution = self._parse_solution_from_zip_bytes(zip_bytes)
        return solution

