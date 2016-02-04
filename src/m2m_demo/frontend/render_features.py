# =============================================================================
# render_features.py
#
# This file implements the `Features` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json
from collections import OrderedDict
from m2m_demo.frontend import RegisterPage, BaseResource


class Feature:
    """
    Utility class to represent the various attributes of each feature.
    """
    def __init__(self, name, enabled, immutable=False):
        self.name = name           # Display name
        self.enabled = enabled     # Is feature enabled by default?
        self.immutable = immutable # Can feature be enabled/disabled?
        self.add_blurb("")         # Explanation of feature (optional)

    def add_blurb(self, blurb):
        self.blurb = '<div class="feature-blurb">{}</div>'.format(blurb)


class FeaturesTab(BaseResource):
    """
    Features tab
    """
    def render_tab(self, request):
        return html


FEATURES = OrderedDict([
    ('connection',     Feature('Connection', True, immutable=True)),
    ('features',       Feature('Features', True, immutable=True)),
    ('simple_cli',     Feature('Simple CLI', True)),
    ('json_cli',       Feature('JSON CLI', True)),
    ('get',            Feature('Get', True)),
    ('schema',         Feature('Schema', True)),
    ('script',         Feature('Script', True)),
    ('explorer',       Feature('Explorer', True)),
    ('write_file',     Feature('Write File', True)),
    ('telemetry',      Feature('Telemetry Policy', False)),
    ('gpb',            Feature('Telemetry GPB', False)),
    ('history',        Feature('Commit history', False)),
    ('current_config', Feature('Current config', True)),
    ('manage_intf',    Feature('Manage interface', False)),
    ('protobuf',       Feature('Protocol Buffer', False)),
    ('about',          Feature('About', True, immutable=True))
])

FEATURES['connection'].add_blurb('Manage a connection to an IOS-XR device.')
FEATURES['features'].add_blurb('Enable/disable the component features of the app.')
FEATURES['simple_cli'].add_blurb('Execute CLI show commands (equivalent to CLI on the router).')
FEATURES['json_cli'].add_blurb('Execute CLI show commands, but get structured data in response.')
FEATURES['get'].add_blurb('Get manageability data for a given schema path.')
FEATURES['schema'].add_blurb('Get schema information for a given schema path.')
FEATURES['script'].add_blurb('Write and execute Python scripts using the M2M API.')
FEATURES['explorer'].add_blurb('Explore the schema.')
FEATURES['write_file'].add_blurb('Write a file to disk on the connected IOS-XR device.')
FEATURES['telemetry'].add_blurb('Generate policy files for use with Telemetry.<br>Note that this feature is relevant to Telemetry in IOX-XR 6.0.0 only, the process has changed in 6.1.0')
FEATURES['gpb'].add_blurb('Construct a Google Protocol Buffer from a candidate file.<br> Note that this feature is relevant to Telemetry in IOX-XR 6.0.0 only, the process has changed in 6.1.0')
FEATURES['history'].add_blurb('Examine the commit history.')
FEATURES['current_config'].add_blurb('Calculate the mapping between the current config and equivalent schema paths and values.')
FEATURES['manage_intf'].add_blurb('Manage an interface.')
FEATURES['protobuf'].add_blurb('Generate a candidate Google Protocol Buffer from a schema path or show command.')
FEATURES['about'].add_blurb('Information about M2M.')

html = '''\
<h1>Features</h1>
''' + '\n'.join([
    '<input type="checkbox" value="{0}"{1}{2}>{3}{4}'.format(
        name,
        ' checked' if feature.enabled else '',
        ' disabled' if feature.immutable else '',
        feature.name,
        feature.blurb)
    for name, feature in FEATURES.iteritems()
])


page = RegisterPage(FeaturesTab, path="/features", tab="features")
