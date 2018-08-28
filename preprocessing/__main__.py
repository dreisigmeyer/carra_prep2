from preprocessing.gbd_metadata.make_gbd_metadata import make_gbd_metadata
import sys

xml_files = sys.argv[1]
make_gbd_metadata(xml_files)
