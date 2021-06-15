"""Tools to parse spectral data files."""
from datetime import datetime
from logging import getLogger

from main.models import *

logger = getLogger(__name__)


def parse_file(
    file_data: bytes,
    crop: Crop,
    region: Region,
    device: Device,
    phase: Phase,
    set: Set,
    light_source: LightSource,
    registered_at: datetime,
    latitude: float,
    longitude: float,
) -> None:
    parsed_values = parse_data(file_data)
    spectral_data_list = [
        SpectralData(
            wavelength=wavelength,
            intensity=intensity,
            crop=crop,
            region=region,
            device=device,
            phase=phase,
            set=set,
            light_source=light_source,
            registered_at=registered_at,
            latitude=latitude,
            longitude=longitude,
        )
        for wavelength, intensity in parsed_values
    ]
    SpectralData.objects.bulk_create(spectral_data_list)
    logger.debug(f"Spectral data: {spectral_data_list}")


def parse_data(file_data: bytes) -> list[tuple[float, float]]:
    result = []
    strings = file_data.decode("utf-8").split("\n")
    for string in strings:
        try:
            wavelength, intensity = string.split("\t")
            result.append(
                (
                    float(wavelength.strip().replace(",", ".")),
                    float(intensity.strip().replace(",", ".")),
                )
            )
        except ValueError:
            logger.info(f"Skipping string: {string}")
    return result
