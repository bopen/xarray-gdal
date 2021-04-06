import os.path

import pytest
import xarray as xr

HERE = os.path.dirname(__file__)


@pytest.mark.parametrize("engine", ["gdal-beta", "gdal-raw"])
def test_xarray_open_dataset(engine):
    cog_file = os.path.join(HERE, "sample.tif")

    ds = xr.open_dataset(cog_file, engine=engine)

    assert isinstance(ds, xr.Dataset)
    assert "band1" in ds.data_vars
    assert ds.data_vars["band1"].shape == (500, 500)

    assert "grid_mapping" in ds.data_vars["band1"].attrs
    assert "spatial_ref" in ds.data_vars
    assert "spatial_ref" not in ds.coords

    ds.to_netcdf(f"test-{engine}-coordinates.nc")

    ds = xr.open_dataset(cog_file, engine=engine, decode_coords="all")

    assert "grid_mapping" in ds.data_vars["band1"].encoding
    assert "spatial_ref" not in ds.data_vars
    assert "spatial_ref" in ds.coords

    ds.to_netcdf(f"test-{engine}-all.nc")
