from django.db import models

DEFAULT_MAX_LENGTH = 255


class Crop(models.Model):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)

    def __str__(self):
        return self.name


class Phase(models.Model):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)

    def __str__(self):
        return self.name


class Device(models.Model):
    device_range = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    resolution = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    sampling = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)

    def __str__(self):
        return self.name


class Set(models.Model):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)

    def __str__(self):
        return self.name


class LightSource(models.Model):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    source_type = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    wavelength = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    temperature = models.CharField(max_length=DEFAULT_MAX_LENGTH)

    def __str__(self):
        return self.name


class SpectralData(models.Model):

    crop = models.ForeignKey(Crop, on_delete=models.PROTECT)
    set = models.ForeignKey(Set, on_delete=models.PROTECT, blank=True, null=True)
    phase = models.ForeignKey(Phase, on_delete=models.PROTECT, blank=True, null=True)
    light_source = models.ForeignKey(
        LightSource, on_delete=models.PROTECT, blank=True, null=True
    )
    device = models.ForeignKey(Device, on_delete=models.PROTECT, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True, null=True)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    intensity = models.FloatField()
    wavelength = models.FloatField()

    registered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.crop.name}: {self.intensity}, {self.wavelength}"

    class Meta:
        verbose_name = "Spectral data"
        verbose_name_plural = "Spectral data"
