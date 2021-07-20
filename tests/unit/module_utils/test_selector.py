# Copyright [2021] [Red Hat, Inc.]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.kubernetes.core.plugins.module_utils.selector import LabelSelectorFilter

prod_definition = {
    'apiVersion': 'v1',
    'kind': 'Pod',
    'metadata': {
        'name': 'test',
        'labels': {
            'environment': 'production',
            'app': 'nginx',
        }
    },
    'spec': {
        'containers': [
            {'name': 'nginx', 'image': 'nginx:1.14.2', 'command': ['/bin/sh', '-c', 'sleep 10']}
        ]
    }
}

no_label_definition = {
    'apiVersion': 'v1',
    'kind': 'Pod',
    'metadata': {
        'name': 'test',
        'labels': {}
    },
    'spec': {
        'containers': [
            {'name': 'nginx', 'image': 'nginx:1.14.2', 'command': ['/bin/sh', '-c', 'sleep 10']}
        ]
    }
}

test_definition = {
    'apiVersion': 'v1',
    'kind': 'Pod',
    'metadata': {
        'name': 'test',
        'labels': {
            'environment': 'test',
            'app': 'nginx',
        }
    },
    'spec': {
        'containers': [
            {'name': 'nginx', 'image': 'nginx:1.15.2', 'command': ['/bin/sh', '-c', 'sleep 10']}
        ]
    }
}


def test_label_selector_without_operator():
    label_selector = ['environment', 'app']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert LabelSelectorFilter(label_selector).isMatching(test_definition)


def test_label_selector_equal_operator():
    label_selector = ['environment==test']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment=production']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment=production', 'app==mongodb']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment=production', 'app==nginx']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment', 'app==nginx']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert LabelSelectorFilter(label_selector).isMatching(test_definition)


def test_label_selector_notequal_operator():
    label_selector = ['environment!=test']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment!=production']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment=production', 'app!=mongodb']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment=production', 'app!=nginx']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment', 'app!=nginx']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)


def test_label_selector_conflicting_definition():
    label_selector = ['environment==test', 'environment!=test']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment==test', 'environment==production']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)


def test_set_based_requirement():
    label_selector = ['environment in (production)']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment in (production, test)']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment notin (production)']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment notin (production, test)']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['environment']
    assert LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert LabelSelectorFilter(label_selector).isMatching(test_definition)
    label_selector = ['!environment']
    assert not LabelSelectorFilter(label_selector).isMatching(prod_definition)
    assert LabelSelectorFilter(label_selector).isMatching(no_label_definition)
    assert not LabelSelectorFilter(label_selector).isMatching(test_definition)
