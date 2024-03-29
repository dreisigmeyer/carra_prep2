from preprocessing.carra_files.make_carra_files import make_carra_files
from preprocessing.gbd_metadata.make_gbd_metadata import make_gbd_metadata
from preprocessing.patent_metadata.make_patent_metadata import make_patent_metadata
import sys

xml_files = sys.argv[1]
NUMBER_OF_PROCESSES = int(sys.argv[2])
path_to_json = sys.argv[3]
make_gbd_metadata(xml_files)
make_patent_metadata(xml_files, NUMBER_OF_PROCESSES)
make_carra_files(xml_files, NUMBER_OF_PROCESSES, path_to_json)
