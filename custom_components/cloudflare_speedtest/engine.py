"""Asynchronous speed test using Cloudflare public endpoints."""

from __future__ import annotations

import asyncio
import itertools
import time
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

from aiohttp import ClientSession

from .const import (
    CONF_DOWNLOAD_BYTES,
    CONF_DOWNLOAD_SECONDS,
    CONF_LATENCY_SAMPLES,
    CONF_MAX_TEST_SECONDS,
    CONF_READ_CHUNK_BYTES,
    CONF_STREAMS,
    CONF_UPLOAD_BYTES,
    CONF_UPLOAD_SECONDS,
    CONF_WRITE_CHUNK_BYTES,
    REQUEST_BYTES_MAX,
    TEST_HOST,
)


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


class _TransferMeter:
    """Track bytes and active transfer duration across concurrent streams."""

    def __init__(self) -> None:
        self.bytes = 0
        self.started: float | None = None
        self.finished: float | None = None

    def add(self, count: int) -> None:
        """Record transferred bytes."""
        now = time.perf_counter()
        self.started = now if self.started is None else self.started
        self.finished = now
        self.bytes += count

    def finish(self) -> None:
        """Mark server acknowledgement of latest transferred bytes."""
        if self.started is not None:
            self.finished = time.perf_counter()

    def reached_duration(self, seconds: float) -> bool:
        """Return whether active transfer window reached configured target."""
        return self.started is not None and time.perf_counter() - self.started >= seconds

    @property
    def mbps(self) -> float:
        """Return rate over active transfer window."""
        if self.started is None or self.finished is None or self.finished <= self.started:
            return 0.0
        return self.bytes * 8 / (self.finished - self.started) / 1_000_000


def _stream_allocations(total_bytes: int, streams: int) -> tuple[int, ...]:
    """Split byte ceiling exactly across streams."""
    quotient, remainder = divmod(total_bytes, streams)
    return tuple(quotient + (index < remainder) for index in range(streams))


class CloudflareSpeedTest:
    """Measure connection using Cloudflare speed-test endpoints."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_run(self, options: Mapping[str, int | float]) -> SpeedTestResult:
        """Run latency, download, and upload measurements."""
        timestamp = datetime.now(UTC)
        try:
            latency, jitter, server = await self._measure_latency(
                int(options[CONF_LATENCY_SAMPLES])
            )
            download_rate, downloaded = await self._measure_download(options)
            upload_rate, uploaded = await self._measure_upload(options)
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

    async def _measure_latency(self, sample_count: int) -> tuple[float, float, str]:
        samples: list[float] = []
        server = ""
        for sample in range(sample_count + 1):
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

    async def _measure_download(self, options: Mapping[str, int | float]) -> tuple[float, int]:
        meter = _TransferMeter()
        target_seconds = float(options[CONF_DOWNLOAD_SECONDS])
        allocations = _stream_allocations(
            int(options[CONF_DOWNLOAD_BYTES]), int(options[CONF_STREAMS])
        )
        read_size = int(options[CONF_READ_CHUNK_BYTES])

        async def download(allocation: int) -> None:
            remaining = allocation
            while remaining and not meter.reached_duration(target_seconds):
                requested = min(remaining, REQUEST_BYTES_MAX)
                received = 0
                async with self._session.get(f"{TEST_HOST}/__down?bytes={requested}") as response:
                    response.raise_for_status()
                    async for chunk in response.content.iter_chunked(read_size):
                        received += len(chunk)
                        meter.add(len(chunk))
                        if meter.reached_duration(target_seconds):
                            break
                if received == 0:
                    raise RuntimeError("download returned no data")
                remaining -= received

        try:
            async with asyncio.timeout(float(options[CONF_MAX_TEST_SECONDS])):
                await asyncio.gather(*(download(allocation) for allocation in allocations))
        except TimeoutError:
            if meter.bytes == 0:
                raise
        return meter.mbps, meter.bytes

    async def _measure_upload(self, options: Mapping[str, int | float]) -> tuple[float, int]:
        meter = _TransferMeter()
        target_seconds = float(options[CONF_UPLOAD_SECONDS])
        allocations = _stream_allocations(
            int(options[CONF_UPLOAD_BYTES]), int(options[CONF_STREAMS])
        )
        write_size = int(options[CONF_WRITE_CHUNK_BYTES])
        payload = bytes(write_size)

        async def upload(allocation: int) -> None:
            remaining = allocation
            while remaining and not meter.reached_duration(target_seconds):
                requested = min(remaining, REQUEST_BYTES_MAX)
                sent = 0

                async def body(request_size: int = requested) -> AsyncIterator[bytes]:
                    nonlocal sent
                    while sent < request_size and not meter.reached_duration(target_seconds):
                        size = min(write_size, request_size - sent)
                        sent += size
                        meter.add(size)
                        yield payload[:size]

                async with self._session.post(f"{TEST_HOST}/__up", data=body()) as response:
                    response.raise_for_status()
                    await response.read()
                meter.finish()
                if sent == 0:
                    raise RuntimeError("upload accepted no data")
                remaining -= sent

        try:
            async with asyncio.timeout(float(options[CONF_MAX_TEST_SECONDS])):
                await asyncio.gather(*(upload(allocation) for allocation in allocations))
        except TimeoutError:
            if meter.bytes == 0:
                raise
        return meter.mbps, meter.bytes
