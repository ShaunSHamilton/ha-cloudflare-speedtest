"""Small asynchronous speed-test client for Cloudflare endpoints."""

from __future__ import annotations

import asyncio
import itertools
import time
from dataclasses import dataclass
from datetime import UTC, datetime

from aiohttp import ClientSession

from .const import DOWNLOAD_BYTES, STREAMS, TEST_HOST, UPLOAD_BYTES


@dataclass(frozen=True, slots=True)
class SpeedTestResult:
    """Measurements from one completed test."""

    timestamp: datetime
    download_mbps: float
    upload_mbps: float
    latency_ms: float
    jitter_ms: float
    download_bytes: int
    upload_bytes: int
    server: str
    error: str | None = None

    @property
    def total_bytes(self) -> int:
        """Return bytes transferred by test payloads."""
        return self.download_bytes + self.upload_bytes


class CloudflareSpeedTest:
    """Measure connection using Cloudflare speed-test endpoints."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_run(self) -> SpeedTestResult:
        """Run latency, download, and upload measurements."""
        timestamp = datetime.now(UTC)
        try:
            latency, jitter, server = await self._measure_latency()
            download_rate, downloaded = await self._measure_download()
            upload_rate, uploaded = await self._measure_upload()
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001 - expose endpoint failures as entity state
            return SpeedTestResult(timestamp, 0, 0, 0, 0, 0, 0, "", f"{type(err).__name__}: {err}")

        return SpeedTestResult(
            timestamp,
            download_rate,
            upload_rate,
            latency,
            jitter,
            downloaded,
            uploaded,
            server,
        )

    async def _measure_latency(self) -> tuple[float, float, str]:
        samples: list[float] = []
        server = ""
        for sample in range(6):
            start = time.perf_counter()
            async with self._session.get(f"{TEST_HOST}/__down?bytes=0") as response:
                response.raise_for_status()
                await response.read()
                elapsed = (time.perf_counter() - start) * 1000
                if sample:
                    samples.append(elapsed)
                server = server or response.headers.get("colo", "")
        jitter = sum(abs(a - b) for a, b in itertools.pairwise(samples)) / (len(samples) - 1)
        return min(samples), jitter, server

    async def _measure_download(self) -> tuple[float, int]:
        per_stream = DOWNLOAD_BYTES // STREAMS

        async def download() -> int:
            received = 0
            async with self._session.get(f"{TEST_HOST}/__down?bytes={per_stream}") as response:
                response.raise_for_status()
                async for chunk in response.content.iter_chunked(64 * 1024):
                    received += len(chunk)
            return received

        start = time.perf_counter()
        counts = await asyncio.gather(*(download() for _ in range(STREAMS)))
        elapsed = time.perf_counter() - start
        total = sum(counts)
        return total * 8 / elapsed / 1_000_000, total

    async def _measure_upload(self) -> tuple[float, int]:
        per_stream = UPLOAD_BYTES // STREAMS
        payload = bytes(per_stream)

        async def upload() -> int:
            async with self._session.post(f"{TEST_HOST}/__up", data=payload) as response:
                response.raise_for_status()
                await response.read()
            return len(payload)

        start = time.perf_counter()
        counts = await asyncio.gather(*(upload() for _ in range(STREAMS)))
        elapsed = time.perf_counter() - start
        total = sum(counts)
        return total * 8 / elapsed / 1_000_000, total
