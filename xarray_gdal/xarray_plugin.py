import typing as T

import pyproj
import rasterio
import xarray as xr


class GdalRawBackend(xr.backends.common.BackendEntrypoint):
    def open_dataset(  # type: ignore
        self,
        filename_or_obj: str,
        drop_variables: T.Optional[T.Tuple[str]] = None,
        decode_coords: T.Union[bool, None, str] = None,
        mask_and_scale: T.Optional[bool] = None,
    ) -> xr.Dataset:
        with rasterio.open(filename_or_obj) as rds:
            data_vars = {}
            for i in rds.indexes:
                data_var_attrs = {
                    "grid_mapping": "spatial_ref",
                    "scale_factor": rds.scales[i - 1],
                    "add_offset": rds.offsets[i - 1],
                    "_FillValue": rds.nodatavals[i - 1],
                }
                data_vars[f"band{i}"] = (("y", "x"), rds.read(i), data_var_attrs)

            spatial_ref_attrs = pyproj.CRS.from_user_input(rds.crs).to_cf()
            data_vars["spatial_ref"] = ((), 0, spatial_ref_attrs)

            coords = {
                "y": ("y", [rds.xy(j, 0)[1] for j in range(rds.height)]),
                "x": ("x", [rds.xy(0, i)[0] for i in range(rds.width)]),
            }

            ds = xr.Dataset(data_vars=data_vars, coords=coords)

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
