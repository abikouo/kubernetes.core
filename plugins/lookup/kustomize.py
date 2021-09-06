#
#  Copyright 2021 Red Hat | Ansible
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
    lookup: kustomize

    short_description: Build a set of kubernetes resources using a 'kustomization.yaml' file.

    author:
      - Aubin Bikouo <@abikouo>
    notes:
      - If both kustomize and kubectl are part of the PATH, kustomize will be used by the plugin.
    description:
      - Uses the kustomize or the kubectl tool.
      - Return the result of kustomize build or kubectl kustomize
    options:
      dir:
        description:
        - The dir argument must be a path to a directory containing 'kustomization.yaml',
          or a git repository URL with a path suffix specifying same with respect to the repository root.
        - If dir is omitted, '.' is assumed.
        default: "."
      binary_path:
        description:
        - The path of a kustomize or kubectl binary to use.
      opt_dirs:
        description:
        - optional list of directories to search for executable in addition to PATH.

    requirements:
      - "python >= 3.6"
'''

EXAMPLES = """
- name: Run lookup using kustomize
  set_fact:
    resources: "{{ lookup('kustomize', binary_path='/path/to/kustomize') }}"

- name: Run lookup using kubectl kustomize
  set_fact:
    resources: "{{ lookup('kustomize', binary_path='/path/to/kubectl') }}"

- name: Create kubernetes resources for lookup output
  k8s:
    definition: "{{ item }}"
  with_items:
    "{{ lookup('kustomize', dir='/path/to/kustomization') }}"
"""

RETURN = """
  _list:
    description:
      - One ore more object definitions returned from the tool execution.
    type: complex
    contains:
      api_version:
        description: The versioned schema of this representation of an object.
        returned: success
        type: str
      kind:
        description: Represents the REST resource this object represents.
        returned: success
        type: str
      metadata:
        description: Standard object metadata. Includes name, namespace, annotations, labels, etc.
        returned: success
        type: complex
      spec:
        description: Specific attributes of the object. Will vary based on the I(api_version) and I(kind).
        returned: success
        type: complex
      status:
        description: Current status details for the object.
        returned: success
        type: complex
"""

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils._text import to_native


import os
import subprocess


def get_binary_from_path(name, opt_dirs=None):
    try:
        opt_arg = {}
        if opt_dirs is not None:
            if not isinstance(opt_dirs, list):
                opt_dirs = [opt_dirs]
            opt_arg['opt_dirs'] = opt_dirs
        bin_path = get_bin_path(name, **opt_arg)
        return bin_path
    except ValueError:
        return None


def run_command(command):
    cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cmd.communicate()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, dir=".", binary_path=None, opt_dirs=None, **kwargs):
        try:
            executable_path = binary_path
            if executable_path is None:
                executable_path = get_binary_from_path(name="kustomize", opt_dirs=opt_dirs)
                if executable_path is None:
                    executable_path = get_binary_from_path(name="kubectl", opt_dirs=opt_dirs)

                # validate that at least one tool was found
                if executable_path is None:
                    raise AnsibleLookupError("Failed to find required executable 'kubectl' and 'kustomize' in paths")

            # check input directory
            kustomization_dir = dir
            if not os.path.isdir(kustomization_dir):
                raise AnsibleLookupError("dir parameter {0} is not a valid directory.".format(kustomization_dir))
            kustomization_file = os.path.join(kustomization_dir, "kustomization.yaml")
            if not os.path.isfile(kustomization_file):
                raise AnsibleLookupError("missing 'kustomization.yaml' file from input directory '{0}'".format(kustomization_dir))

            command = [executable_path]
            if executable_path.endswith('kustomize'):
                command += ['build', kustomization_dir]
            elif executable_path.endswith('kubectl'):
                command += ['kustomize', kustomization_dir]
            else:
                raise AnsibleLookupError("unexpected tool provided as parameter {0}, expected one of kustomize, kubectl.".format(executable_path))

            (out, err) = run_command(command)
            if err:
                raise AnsibleLookupError("kustomize command failed with: {0}".format(err.decode("utf-8")))
            return [out.decode('utf-8')]

        except Exception as e:
            raise AnsibleLookupError("The following error occurred: {0}".format(to_native(e)))
