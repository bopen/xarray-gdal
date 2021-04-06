import os.path
import typing as T

import rioxarray
import xarray as xr

CAN_OPEN_EXTS = {"geotif", "geotiff", "j2k", "jp2", "tif", "tiff", "vrt"}


class GdalBetaBackend(xr.backends.common.BackendEntrypoint):
    def open_dataset(  # type: ignore
        self,
        filename_or_obj: str,
        drop_variables: T.Optional[T.Tuple[str]] = None,
        decode_coords: T.Union[bool, None, str] = None,
    ) -> xr.Dataset:
        ds_or_da = rioxarray.open_rasterio(filename_or_obj, default_name="__bands__")
        if isinstance(ds_or_da, xr.DataArray):
            ds = ds_or_da.to_dataset("band")
            ds = ds.rename({i: f"band{i}" for i in ds.data_vars})
            if decode_coords in {None, True, "coordinates"}:
                ds = ds.reset_coords("spatial_ref")
        else:
            ds = ds_or_da
        return ds

    def guess_can_open(self, filename_or_obj: T.Any) -> bool:
        try:
            _, ext = os.path.splitext(filename_or_obj)
        except TypeError:
            return False
        return ext[1:].lower() in CAN_OPEN_EXTS
