import argparse
import sys
from pathlib import Path

parser = argparse.ArgumentParser(prog='main', description='Convert a high-level yaml workflow file to CWL.')
parser.add_argument('--yaml', type=str, required=('--generate_schemas_only' not in sys.argv),
                    help='Yaml workflow file')

parser.add_argument('--generate_schemas_only', default=False, action="store_true",
                    help='Generate schemas for the files in ~/wic/cwl_dirs.txt and ~/wic/yml_dirs.txt')
parser.add_argument('--homedir', type=str, required=False, default=str(Path().home()),
                    help='The users home directory. This is necessary because CWL clears environment variables (e.g. HOME)')
# Change default to True for now. See comment in compiler.py
parser.add_argument('--cwl_output_intermediate_files', type=bool, required=False, default=True,
                    help='Enable output files which are used between steps (for debugging).')
parser.add_argument('--insert_steps_automatically', default=False, action="store_true",
                    help='''Attempt to fix inference failures by speculatively
                    inserting workflow steps from a curated whitelist.''')
parser.add_argument('--write_summary',
                    help='Path to write the final output JSON object to. Default is stdout.')

parser.add_argument('--parallel', default=False, action="store_true",
                    help='''When running locally, execute independent steps in parallel.
                    \nThis is required for real-time analysis, but it may cause issues with
                    \nhanging (particularly when scattering). See user guide for details.''')
parser.add_argument('--quiet', default=False, action="store_true",
                    help='''Disable verbose output. This will not print out the commands used for each step.''')
parser.add_argument('--cwl_runner', type=str, required=False, default='cwltool', choices=['cwltool', 'toil-cwl-runner'],
                    help='The CWL runner to use for running workflows locally.')
parser.add_argument('--ignore_docker_install', default=False, action="store_true",
                    help='Do not check whether docker is installed before running workflows.')
parser.add_argument('--ignore_docker_processes', default=False, action="store_true",
                    help='Do not check whether there are too many running docker processes before running workflows.')
parser.add_argument('--user_space_docker_cmd', default='docker',
                    help='Specify which command to use to run OCI containers.')

group_run = parser.add_mutually_exclusive_group()
group_run.add_argument('--run_local', default=False, action="store_true",
                       help='After generating the cwl file(s), run it on your local machine.')
group_run.add_argument('--run_compute', default=False, action="store_true",
                       help='After generating the cwl file(s), run it on the remote labshare Compute platform.')
parser.add_argument('--compute_driver', type=str, required=False, default='slurm', choices=['slurm', 'argo'],
                    help='The driver to use for running workflows on labshare Compute.')
# Use required=('--run_compute' in sys.argv) make other args conditionally required.
# See https://stackoverflow.com/questions/19414060/argparse-required-argument-y-if-x-is-present
# For example, if run_compute is enabled, you MUST enable cwl_inline_subworkflows!
# Plugins with 'class: Workflow' (i.e. subworkflows) are not currently supported.

# --cwl_inline_subworkflows inlines subworkflows in YAML formats and --cwl_inline_scatter inlines
# the compiled cwl files. This separation is necessary since inlining scatter requires resolving
# edge inferences first.
parser.add_argument('--cwl_inline_subworkflows', default=('--run_compute' in sys.argv), action="store_true",
                    help='Before generating the cwl file, inline all subworkflows. Required for --run_compute')
parser.add_argument('--cwl_inline_scatter', default=('--run_compute' in sys.argv), action="store_true",
                    help='After compilation, inline scatter feature into subworkflows. ' +
                         'This ignores "inlineable: False" in wic metadata tag. Required for --run_compute.')
parser.add_argument('--inference_disable', default=False, action="store_true",
                    help='Disables use of the inference algorithm when compiling.')
parser.add_argument('--inference_use_naming_conventions', default=False, action="store_true",
                    help='Enables the use of naming conventions in the inference algorithm')
parser.add_argument('--validate_plugins', default=False, action="store_true",
                    help='Validate all CWL CommandLineTools')
parser.add_argument('--no_skip_dollar_schemas', default=False, action="store_true",
                    help='''Does not skip processing $schemas tags in CWL files for performance.
                    Skipping significantly improves initial validation performance, but is not always desired.
                    See https://github.com/common-workflow-language/cwltool/issues/623''')
parser.add_argument('--cachedir', type=str, required=False, default='cachedir',
                    help='The directory to save intermediate results; useful with RealtimePlots.py')

AWS_URL = 'http://compute.ci.aws.labshare.org'
NCATS_URL = 'https://compute.scb-ncats.io/'

parser.add_argument('--compute_url', type=str, default=NCATS_URL,
                    help='The URL associated with the labshare Compute API. Required for --run_compute')
parser.add_argument('--compute_access_token', type=str, required=('--run_compute' in sys.argv),
                    help="""The access_token used for authentication. Required for --run_compute
                    For now, get this manually from https://a-qa.labshare.org/""")

parser.add_argument('--graph_label_edges', default=False, action="store_true",
                    help='Label the graph edges with the name of the intermediate input/output.')
parser.add_argument('--graph_label_stepname', default=False, action="store_true",
                    help='Prepend the step name to each step node.')
parser.add_argument('--graph_show_inputs', default=False, action="store_true",
                    help='Add nodes to the graph representing the workflow inputs.')
parser.add_argument('--graph_show_outputs', default=False, action="store_true",
                    help='Add nodes to the graph representing the workflow outputs.')
parser.add_argument('--graph_inline_depth', type=int, required=False, default=sys.maxsize,
                    help='Controls the depth of subgraphs which are displayed.')
parser.add_argument('--graph_dark_theme', default=False, action="store_true",
                    help='Changees the color of the fonts and edges from white to black.')
parser.add_argument('--custom_net', type=str, required=False,
                    help='Passes --custom-net flag to cwltool.')
