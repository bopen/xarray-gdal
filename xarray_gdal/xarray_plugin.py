import os.path
import typing as T

import rasterio
import rioxarray
import xarray as xr

CAN_OPEN_EXTS = {"geotif", "geotiff", "j2k", "jp2", "tif", "tiff", "vrt"}


class GdalBetaBackend(xr.backends.common.BackendEntrypoint):
    def open_dataset(  # type: ignore
        self,
        filename_or_obj: str,
        drop_variables: T.Optional[T.Tuple[str]] = None,
        decode_coords: T.Union[bool, None, str] = None,
        mask_and_scale: T.Optional[bool] = None,
    ) -> xr.Dataset:
        ds_or_da = rioxarray.open_rasterio(filename_or_obj, default_name="__bands__")
        if isinstance(ds_or_da, xr.DataArray):
            ds = ds_or_da.to_dataset("band")
            # FIXME: fixup attributes
            for dv in ds.data_vars.values():
                dv.attrs.update(ds.attrs)
            ds.attrs.clear()
            ds = ds.rename({i: f"band{i}" for i in ds.data_vars})
            ds = ds.reset_coords("spatial_ref")
        else:
            ds = ds_or_da

        decoded_ds = xr.decode_cf(
            ds,
            concat_characters=False,
            mask_and_scale=mask_and_scale,
            decode_times=False,
            decode_coords=decode_coords,
            drop_variables=drop_variables,
            use_cftime=False,
            decode_timedelta=False,
        )
        return decoded_ds

    def guess_can_open(self, filename_or_obj: T.Any) -> bool:
        try:
            _, ext = os.path.splitext(filename_or_obj)
        except TypeError:
            return False
        return ext[1:].lower() in CAN_OPEN_EXTS


class GdalRawBackend(xr.backends.common.BackendEntrypoint):
    def open_dataset(  # type: ignore
        self,
        filename_or_obj: str,
        drop_variables: T.Optional[T.Tuple[str]] = None,
        decode_coords: T.Union[bool, None, str] = None,
        mask_and_scale: T.Optional[bool] = None,
    ) -> xr.Dataset:
        with rasterio.open(filename_or_obj) as rds:
            data_vars = {
                f"band{i}": (("y", "x"), rds.read(i), {"grid_mapping": "spatial_ref"})
                for i in rds.indexes
            }
            data_vars["spatial_ref"] = ((), 0, {"grid_mapping_name": "dummy"})
            ds = xr.Dataset(data_vars=data_vars,)

            decoded_ds = xr.decode_cf(
                ds,
                concat_characters=False,
                mask_and_scale=mask_and_scale,
                decode_times=False,
                decode_coords=decode_coords,
                drop_variables=drop_variables,
                use_cftime=False,
                decode_timedelta=False,
            )
            return decoded_ds
