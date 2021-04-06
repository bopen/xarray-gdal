import os.path

import xarray as xr

HERE = os.path.dirname(__file__)


def test_xarray_open_dataset():
    cog_file = os.path.join(HERE, "sample.tif")

    ds = xr.open_dataset(cog_file, engine="gdal-beta")

    assert isinstance(ds, xr.Dataset)
    assert "band1" in ds.data_vars
    assert ds.data_vars["band1"].shape == (500, 500)
    assert "spatial_ref" in ds.data_vars
    assert "spatial_ref" not in ds.coords

    ds = xr.open_dataset(cog_file, engine="gdal-beta", decode_coords="all")

    assert "spatial_ref" not in ds.data_vars
    assert "spatial_ref" in ds.coords

    ds = xr.open_dataset(cog_file)

    assert isinstance(ds, xr.Dataset)

    ds.to_netcdf("test.nc")
