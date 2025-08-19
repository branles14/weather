from __future__ import annotations

from pathlib import Path
import pytest

from weather.config import load_config


def test_load_config_valid(tmp_path: Path) -> None:
    cfg_path = tmp_path / "weather.conf"
    cfg_path.write_text(
        """
LAT=39.1
LONGITUDE=-105.2
UNITS=metric
CACHE_MAX_RANGE=1500
CACHE_MAX_AGE=600
        """.strip(),
        encoding="utf-8",
    )
    cfg = load_config(cfg_path)
    assert cfg.lat == 39.1
    assert cfg.lon == -105.2
    assert cfg.units == "metric"
    assert cfg.cache_max_range == 1500
    assert cfg.cache_max_age == 600


@pytest.mark.parametrize(
    "content",
    [
        "LAT=abc",  # invalid latitude
        "LONGITUDE=def",  # invalid longitude
        "UNITS=unknown",  # invalid units
        "CACHE_MAX_RANGE=bad",  # invalid int
        "CACHE_MAX_AGE=bad",  # invalid int
    ],
)
def test_load_config_invalid_values(tmp_path: Path, content: str) -> None:
    cfg_path = tmp_path / "weather.conf"
    cfg_path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(cfg_path)

