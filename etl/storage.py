from datetime import datetime, timezone
import os
from pathlib import Path

from loguru import logger
from polars import DataFrame    

def _create_folder_structure(time: datetime) -> Path:
    dir_path = Path("data") / f"year={time.year}" / f"month={time.month:02d}" / f"day={time.day:02d}"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def write_parquet_file(raw_data: list[dict]) -> None:
    if not raw_data:
        logger.warning("No data to write to Parquet file.")
        return
    timestamp = datetime.now(timezone.utc)
    dir_path = _create_folder_structure(timestamp)
    file_path = dir_path / f"coins_{timestamp.strftime('%H%M%S')}.parquet"
    try:
        df = DataFrame([coin for coin in raw_data])
        df.write_parquet(file_path, compression="snappy")
        logger.info(f"Data written to {file_path}")
        return
    except Exception as e:
        logger.error(f"Error writing data to Parquet file: {e}")
        raise