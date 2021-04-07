import os.path

import xarray as xr

HERE = os.path.dirname(__file__)


def test_xarray_open_dataset():
    cog_file = os.path.join(HERE, "sample.tif")

    ds = xr.open_dataset(cog_file, engine="gdal-raw")

    assert isinstance(ds, xr.Dataset)
    assert "band1" in ds.data_vars
    assert ds.data_vars["band1"].shape == (500, 500)

    assert "grid_mapping" in ds.data_vars["band1"].attrs
    assert "spatial_ref" in ds.data_vars
    assert "spatial_ref" not in ds.coords

    ds.to_netcdf("test-coordinates.nc")

    ds = xr.open_dataset(cog_file, engine="gdal-raw", decode_coords="all")

    assert "grid_mapping" in ds.data_vars["band1"].encoding
    assert "spatial_ref" not in ds.data_vars
    assert "spatial_ref" in ds.coords

    ds.to_netcdf("test-all.nc")
