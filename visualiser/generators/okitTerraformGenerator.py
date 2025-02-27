
# Copyright (c) 2020, 2021, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.

"""Provide Module Description
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
__author__ = ["Andrew Hopkinson (Oracle Cloud Solutions A-Team)"]
__version__ = "1.0.0"
__module__ = "ociTerraformGenerator"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


import os
import json

from common.okitCommon import jsonToFormattedString
from common.okitCommon import writeTerraformFile
from common.okitLogging import getLogger
from generators.okitGenerator import OCIGenerator

# Configure logging
logger = getLogger()

class OCITerraformGenerator(OCIGenerator):
    DIRECTORY_SUFFIX = 'terraform'
    PROVIDER_FILE_NAME = 'provider.tf'
    METADATA_FILE_NAME = 'metadata.tf'
    MAIN_FILE_NAME = 'main.tf'
    USER_DEFINED_FILE_NAME = 'user_defined.tf'
    VARIABLES_FILE_NAME = 'variables.tf'
    TERRAFORM_FILE_NAME = 'terraform.tfvars'
    OUTPUTS_FILE_NAME = 'output.tf'
    JINJA2_VARIABLE_FORMAT = 'var.{0:s}'

    def __init__(self, template_root, output_root, visualiser_json, use_vars=True, add_provider=True, add_suffix=True):
        template_dir = os.path.join(template_root, self.DIRECTORY_SUFFIX)
        if add_suffix:
            output_dir = os.path.join(output_root, self.DIRECTORY_SUFFIX)
        else:
            output_dir = output_root
        super(OCITerraformGenerator, self).__init__(template_dir, output_dir, visualiser_json, use_vars, add_provider)

    def writeFiles(self):
        # Write Provider tf file
        writeTerraformFile(os.path.join(self.output_dir, self.PROVIDER_FILE_NAME), self.getProvider())
        # Write Metadata tf file
        writeTerraformFile(os.path.join(self.output_dir, self.METADATA_FILE_NAME), self.getMetadata())
        # Write Main tf processing file
        main_rendered = self.getRenderedMain()
        writeTerraformFile(os.path.join(self.output_dir, self.MAIN_FILE_NAME), self.getRenderedMain())
        # Write Variable files
        variable_definitions = []
        variable_values = []
        for key, value in self.getVariables().items():
            if type(value) is dict:
                variable_values.append('{0!s:s} = {1!s:s}'.format(key, json.dumps(value)))
            elif type(value) is bool:
                variable_values.append('{0!s:s} = "{1}"'.format(key, str(value).lower()))
            else:
                variable_values.append('{0!s:s} = "{1}"'.format(key, value))
            variable_definitions.append('variable "{0:s}" {{}}'.format(key))
            #variable_definitions.append('variable "{0:s}" {{\ndefault = "{1}"\n}}'.format(key, value))
        writeTerraformFile(os.path.join(self.output_dir, self.VARIABLES_FILE_NAME), variable_definitions)
        writeTerraformFile(os.path.join(self.output_dir, self.TERRAFORM_FILE_NAME), variable_values)
        # User Defined - Unchecked Terraform
        user_defined_terraform = self.visualiser_json.get('user_defined', {}).get('terraform', '')
        if user_defined_terraform.rstrip() != '':
            writeTerraformFile(os.path.join(self.output_dir, self.USER_DEFINED_FILE_NAME), [user_defined_terraform])

        return
    
    def getVariableDefinitions(self):
        variable_definitions = []
        variable_values = []
        for key, value in self.getVariables().items():
            if type(value) is dict:
                variable_values.append('{0!s:s} = {1!s:s}'.format(key, json.dumps(value)))
            elif type(value) is bool:
                variable_values.append('{0!s:s} = "{1}"'.format(key, str(value).lower()))
            else:
                variable_values.append('{0!s:s} = "{1}"'.format(key, value))
            variable_definitions.append('variable "{0:s}" {{}}'.format(key))
        return variable_definitions
    
    def getVariableValues(self):
        variable_definitions = []
        variable_values = []
        for key, value in self.getVariables().items():
            if type(value) is dict:
                variable_values.append('{0!s:s} = {1!s:s}'.format(key, json.dumps(value)))
            elif type(value) is bool:
                variable_values.append('{0!s:s} = "{1}"'.format(key, str(value).lower()))
            else:
                variable_values.append('{0!s:s} = "{1}"'.format(key, value))
            variable_definitions.append('variable "{0:s}" {{}}'.format(key))
        return variable_values
    
    def toJson(self):
        generated_tf = {
            "provider.tf": '\n'.join(self.getProvider()),
            "metadata.tf": '\n'.join(self.getMetadata()),
            "main.tf": '\n'.join(self.getRenderedMain()),
            "variables.tf": '\n'.join(self.getVariableDefinitions()),
            "terraform.tfvar": '\n'.join(self.getVariableValues()),
            # "output.tf": '\n'.join(self.getRenderedOutput()),
            "user_defined.tf": self.visualiser_json.get('user_defined', {}).get('terraform', '')
        }
        return generated_tf

    def formatJinja2Variable(self, variable_name):
        return 'var.{0:s}'.format(variable_name)

    def formatJinja2IdReference(self, resource_name, element='id'):
        return 'local.{0!s:s}_{1!s:s}'.format(resource_name, element)

    def formatJinja2DhcpReference(self, resource_name):
        return 'local.{0:s}_dhcp_options_id'.format(resource_name)

    def formatJinja2Value(self, value):
        if isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return '"{0!s:s}"'.format(value)

    def renderDefinedTags(self, artifact):
        # tags = {**artifact.get("defined_tags", {}), **self.visualiser_json.get("defined_tags", {})}
        tags = {**artifact.get("defined_tags", {}), **self.visualiser_json.get("defined_tags", {}), **self.getOkitDefinedTags(artifact)}
        if len(tags.keys()) > 0:
            definedtags = {}
            for namespace, tags in tags.items():
                for key, value in tags.items():
                    definedtags["{0!s:s}.{1!s:s}".format(namespace, key)] = str(value)
            if self.use_vars:
                standardisedName = self.standardiseResourceName(artifact.get('display_name', artifact.get('name', '')))
                # -- Defined Tags
                variableName = '{0:s}_defined_tags'.format(standardisedName)
                self.run_variables[variableName] = definedtags
                self.jinja2_variables["defined_tags"] = self.formatJinja2Variable(variableName)
            else:
                self.jinja2_variables["defined_tags"] = self.formatJinja2Value(definedtags)
        else:
            self.jinja2_variables.pop("defined_tags", None)
        return


