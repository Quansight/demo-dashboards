import gcsfs
import intake
import pandas as pd
from google.cloud import storage
from intake.catalog import Catalog

from mlops_framework import CATALOG_DIR

project = "qhub-279316"
bucket = "quansight-qhub-data"
json_path = "/home/jovyan/shared/quansight/quansight-qhub-object-storage.json"
catalog_path = CATALOG_DIR.joinpath("catalog.yml")

"""
NOTES:
------
Run the below code to clear gcsfs cache
    - fs.invalidate_cache()
"""


def catalog_init():
    """
    Initialising the airline catalog
    Args:
        No parameters
    Returns:
        Intake catalog object
    """
    fs = gcsfs.GCSFileSystem(token=json_path)
    catalog = intake.open_catalog(catalog_path)
    return catalog


def list_catalog(catalog_instance: Catalog):
    """
    Get a list of all the catalog entries
     Args:
        catalog_instance: Intake catalog of the data (generated from catalog_init)
    Returns:
        A list of catalog entries
    """
    catalog_list = list(catalog_instance)
    return catalog_list


def view_catalog(catalog_instance: Catalog):
    """Viewable GUI form of the catalog. View in Jupyter or in Panel app
    Args:
        catalog_instance: Intake catalog of the data (generated from catalog_init)
    Returns:
        Panel app with interactive catalog visualization.
    """
    catalog = catalog_instance
    intake_app = intake.gui
    intake_app.add(catalog)
    return intake_app
