#!/usr/bin/python

# Copyright (c) 2020, 2021, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.

"""Provide Module Description
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
__author__ = ["Andrew Hopkinson (Oracle Cloud Solutions A-Team)"]
__version__ = "1.0.0"
__module__ = "ociQuery"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import datetime
import json
import oci
import re
import uuid

from discovery import OciResourceDiscoveryClient

from common.okitCommon import logJson
from common.okitCommon import standardiseIds
from common.okitCommon import jsonToFormattedString
from common.okitLogging import getLogger
from common.okitCommon import userDataDecode
from facades.ociConnection import OCIConnection

# Configure logging
logger = getLogger()

class OCIQuery(OCIConnection):

    SUPPORTED_RESOURCES = [
        "AnalyticsInstance",
        "AutonomousDatabase",
        "Backend",
        "BackendSet",
        "Bastion",
        "BootVolume",
        "BootVolumeAttachment",
        "Bucket",
        "Cluster",
        "Cpe",
        "Database",
        "DbHome",
        "DbNode",
        "DbSystem",
        "DHCPOptions",
        "Drg",
        "DrgAttachment",
        "DrgRouteDistribution",
        "DrgRouteDistributionStatement",
        "DrgRouteRule",
        "DrgRouteTable",
        "ExadataInfrastructure",
        "Export",
        "ExportSet",
        "FileSystem",
        "Group",
        "Image",
        "Instance",
        # "InstancePool",
        "InternetGateway",
        "IPSecConnection",
        "IpSecConnectionTunnel",
        "LoadBalancer",
        "LocalPeeringGateway",
        "MountTarget",
        "MySqlDbSystem",
        "NatGateway",
        "NetworkSecurityGroup",
        "NetworkSecurityGroupSecurityRule",
        "NodePool",
        "Policy",
        "PrivateIp",
        "PublicIp",
        "RemotePeeringConnection",
        "RouteTable",
        "SecurityList",
        "ServiceGateway",
        "Subnet",
        "User",
        "UserGroupMembership",
        "Vcn",
        "VmCluster",
        "VmClusterNetwork",
        "Volume",
        "VolumeAttachment",
        "VnicAttachment",
        "Vnic"
    ]
    DISCOVERY_OKIT_MAP = {
        "AnalyticsInstance": "analytics_instances",
        "AutonomousDatabase": "autonomous_databases",
        "Bastion": "bastions",
        #"BootVolume": "block_storage_volumes",
        "Bucket": "object_storage_buckets",
        "Cluster": "oke_clusters",
        "Cpe": "customer_premise_equipments",
        "Database": "databases",
        "DbHome": "db_homes",
        "DbNode": "db_nodes",
        "DbSystem": "database_systems",
        "DHCPOptions": "dhcp_options",
        # "Drg": "dynamic_routing_gateways",
        "Drg": "drgs",
        "DrgAttachment": "drg_attachments",
        "ExadataInfrastructure": "exadata_infrastructures",
        "FileSystem": "file_systems",
        "Group": "groups",
        "Instance": "instances",
        "InstancePool": "instance_pools",
        "InternetGateway": "internet_gateways",
        "IPSecConnection": "ipsec_connections",
        "LoadBalancer": "load_balancers",
        "LocalPeeringGateway": "local_peering_gateways",
        "MountTarget": "mount_targets",
        "MySqlDbSystem": "mysql_database_systems",
        "NatGateway": "nat_gateways",
        "NetworkSecurityGroup": "network_security_groups",
        "Policy": "policys", # Yes we know it's spelt incorrectly but the okitCodeSkeletonGenerator.py is simple
        "RemotePeeringConnection": "remote_peering_connections",
        "RouteTable": "route_tables",
        "SecurityList": "security_lists",
        "ServiceGateway": "service_gateways",
        "Subnet": "subnets",
        "User": "users",
        "Vcn": "virtual_cloud_networks",
        "VmCluster": "vm_clusters",
        "VmClusterNetwork": "vm_cluster_networks",
        "Volume": "block_storage_volumes"
    }
    VALID_LIFECYCLE_STATES = [
        "RUNNING",
        "STARTING",
        "STOPPING",
        "STOPPED",
        "AVAILABLE",
        "ACTIVE",
        "PROVISIONING",
        "UPDATING",
        "CREATING",
        "INACTIVE",
        "ATTACHED",
        "ALLOCATED"
    ]

    def __init__(self, config=None, configfile=None, profile=None):
        super(OCIQuery, self).__init__(config=config, configfile=configfile, profile=profile)

    def connect(self):
        pass

    def executeQuery(self, regions, compartments, include_sub_compartments=False, **kwargs):
        logger.info('Request : {0!s:s}'.format(str(regions)))
        logger.info('Request : {0!s:s}'.format(str(compartments)))
        logger.info('Request : {0!s:s}'.format(str(include_sub_compartments)))
        if self.instance_principal:
            self.config['tenancy'] = self.getTenancy()
        # if "cert-bundle" in self.config:
        #     cert_bundle = self.config["cert-bundle"]
        # else:
        #     cert_bundle = None
        logger.info(f'cert_bundle={self.cert_bundle}')

        discovery_client = OciResourceDiscoveryClient(self.config, signer=self.signer, cert_bundle=self.cert_bundle, regions=regions, include_resource_types=self.SUPPORTED_RESOURCES, compartments=compartments, include_sub_compartments=include_sub_compartments)
        # Get Supported Resources
        response = self.response_to_json(discovery_client.get_all_resources())
        logger.debug(f"Response : {response}")
        logger.debug('Response JSON : {0!s:s}'.format(json.dumps(response, indent=2)))
        # Get All Compartment
        all_compartments = self.response_to_json(discovery_client.all_compartments)
        # Filter Compartments to those specifically queried
        queried_compartments = [c for c in all_compartments if c["id"] in compartments]
        if include_sub_compartments:
            for id in compartments:
                queried_compartments.extend([c for c in all_compartments if c["id"] in discovery_client.get_subcompartment_ids(id)])
        response_json = self.convert(response, queried_compartments, compartments)

        return response_json

    def response_to_json(self, data):
        # # simple hack to convert to json
        # return str(results).replace("'",'"')
        # more robust hack to convert to json
        json_str = re.sub("'([0-9a-zA-Z-\.]*)':", '"\g<1>":', str(data))
        json_str = re.sub("'([0-9a-zA-Z-_\.]*)': '([0-9a-zA-Z-_\.]*)'", '"\g<1>": "\g<2>"', json_str)
        #return json.dumps(json.loads(json_str), indent=2)
        return json.loads(json_str)

    def convert(self, discovery_data, compartments, query_compartment_ids=[]):
        response_json = {
            "compartments": [self.addResourceName(c) for c in compartments]
        }
        compartment_ids = [c["id"] for c in response_json["compartments"]]
        # Set top level compartment parent to None
        for compartment in response_json["compartments"]:
            if compartment["id"] in query_compartment_ids:
                compartment["compartment_id"] = None
        map_keys = self.DISCOVERY_OKIT_MAP.keys()
        for region, resources in discovery_data.items():
            logger.info("Processing Region : {0!s:s} {1!s:s}".format(region, resources.keys()))
            for resource_type, resource_list in resources.items():
                logger.info("Processing Resource : {0!s:s}".format(resource_type))
                # logger.info(jsonToFormattedString(resource_list))
                if resource_type in map_keys:
                    if resource_type == "Drg":
                        resource_list = self.dynamic_routing_gateways(resource_list, resources)
                    elif resource_type == "MountTarget":
                        resource_list = self.mount_targets(resource_list, resources)
                    elif resource_type == "Instance":
                        resource_list = self.instances(resource_list, resources)
                    elif resource_type == "LoadBalancer":
                        resource_list = self.loadbalancers(resource_list, resources)
                    elif resource_type == "MySqlDbSystem":
                        resource_list = self.mysql_database_systems(resource_list, resources)
                    elif resource_type == "NetworkSecurityGroup":
                        resource_list = self.network_security_group(resource_list, resources)
                    elif resource_type == "Bucket":
                        resource_list = self.object_storage_buckets(resource_list, resources)
                    elif resource_type == "Cluster":
                        resource_list = self.oke_clusters(resource_list, resources)
                    elif resource_type == "RouteTable":
                        resource_list = self.route_tables(resource_list, resources)
                    elif resource_type == "ServiceGateway":
                        resource_list = self.service_gateways(resource_list, resources)
                    elif resource_type == "Group":
                        resource_list = self.groups(resource_list, resources)
                    # elif resource_type == "AnalyticsInstance":
                    #     resource_list = self.analytics_instances(resource_list, resources)
                    # Check Life Cycle State
                    # logger.info(f'Processing {resource_type} : {resource_list}')
                    response_json[self.DISCOVERY_OKIT_MAP[resource_type]] = [self.addResourceName(r) for r in resource_list if "lifecycle_state" not in r or r["lifecycle_state"] in self.VALID_LIFECYCLE_STATES]
        return response_json
    
    def addResourceName(self,resource):
        # resource['resource_name'] = f'Okit_{resource["id"].split(".")[-1]}'
        resource['resource_name'] = f'Okit_{uuid.uuid4().hex}'
        return resource

    def generateResourceName(self, resource_type):
        return f'Okit_{resource_type}_{str(datetime.datetime.now().timestamp())}'

    def analytics_instances(self, analytics_instances, resources):
        for ai in analytics_instances:
            logger.info(jsonToFormattedString(ai))
        return analytics_instances

    def dynamic_routing_gateways(self, drgs, resources):
        for drg in drgs:
            drg["route_tables"] = [r for r in resources.get("DrgRouteTable", []) if r["drg_id"] == drg["id"]]
            for rt in drg["route_tables"]:
                rt["rules"] = [r for r in resources.get("DrgRouteRule", []) if r["drg_route_table_id"] == rt["id"]]
            drg["route_distributions"] = [r for r in resources.get("DrgRouteDistribution", []) if r["drg_id"] == drg["id"]]
            for rd in drg["route_distributions"]:
                rd["statements"] = [r for r in resources.get("DrgRouteDistributionStatement", []) if r["drg_route_distribution_id"] == rd["id"]]
            # attachments = [a for a in resources.get("DrgAttachment", []) if a["drg_id"] == drg["id"]]
            # drg["vcn_id"] = attachments[0]["vcn_id"] if len(attachments) else ""
            # drg["route_table_id"] = attachments[0]["route_table_id"] if len(attachments) else ""
        return drgs

    def file_storage_systems(self, file_storage_systems, resources):
        for fs in file_storage_systems:
            fs["exports"] = [e for e in resources.get("Export", []) if e["file_system_id"] == fs["id"]]
            export_set_ids = [e["export_set_id"] for e in fs["exports"]]
            export_sets = [e for e in resources.get("ExportSet", []) if e["id"] in export_set_ids]
            fs["mount_targets"] = [m for m in resources.get("MountTarget", []) if m["export_set_id"] in export_set_ids]
            for mt in fs["mount_targets"]:
                ess = [e for e in export_sets if e["id"] == mt["export_set_id"]]
                mt["export_set"] = ess[0] if len(ess) else {}
        return file_storage_systems

    def groups(self, groups, resources):
        for group in groups:
            group["user_ids"] = [m["user_id"] for m in resources.get("UserGroupMembership", []) if m["group_id"] == group["id"]]
        return groups

    def instances(self, instances, resources):
        # Exclude OKE Instances
        instances = [i for i in instances if 'oke-cluster-id' not in i['metadata']]
        for instance in instances:
            instance["source_details"]["os"] = ''
            instance["source_details"]["version"] = ''
            if ("source_details" in instance and "image_id" in instance["source_details"]):
                logger.debug(f'Image Id : {instance["source_details"]["image_id"]}')
                images = [i for i in resources.get("Image", []) if i["id"] == instance["source_details"]["image_id"]]
                for i in resources.get("Image", []):
                    logger.debug(f'Image Id - {i["id"]} - {i["id"] == instance["source_details"]["image_id"]}')
                if len(images):
                    instance["source_details"]["os"] = images[0]["operating_system"]
                    instance["source_details"]["version"] = images[0]["operating_system_version"]
            if "metadata" in instance and "user_data" in instance["metadata"]:
                instance["metadata"]["user_data"] = userDataDecode(instance["metadata"]["user_data"])
            # Add Attached Block Storage Volumes
            instance['block_storage_volume_ids'] = [va['volume_id'] for va in resources.get("VolumeAttachment", []) if va['instance_id'] == instance['id']]
            # Add Vnic Attachments
            attachments_vnic_ids = [va["vnic_id"] for va in resources.get("VnicAttachment", []) if va['instance_id'] == instance['id']]
            instance['vnics'] = [vnic for vnic in resources.get("Vnic", []) if vnic["id"] in attachments_vnic_ids]
            # Get Volume Attachments as a single call and loop through them to see if they are associated with the instance.
            boot_volume_attachments = [va for va in resources.get("BootVolumeAttachment", []) if va['instance_id'] == instance['id']]
            boot_volumes = [va for va in resources.get("BootVolume", []) if va['id'] == boot_volume_attachments[0]['boot_volume_id']] if len(boot_volume_attachments) else []
            instance['boot_volume_size_in_gbs'] = boot_volumes[0]['size_in_gbs'] if len(boot_volumes) else 0
            instance['is_pv_encryption_in_transit_enabled'] = boot_volume_attachments[0]['is_pv_encryption_in_transit_enabled'] if len(boot_volume_attachments) else False
        return instances

    def loadbalancers(self, loadbalancers, resources):
        for lb in loadbalancers:
            lb["instance_ids"] = []
            for backend_set, backends in lb["backend_sets"].items():
                for backend in backends["backends"]:
                    ip_addresses = [ip for ip in resources.get("PrivateIp", []) if ip["ip_address"] == backend["ip_address"]]
                    lb["instance_ids"].extend([va["instance_id"] for va in resources.get("VnicAttachment", []) if va['vnic_id'] == ip_addresses[0]['vnic_id']] if len(ip_addresses) else [])
        return loadbalancers

    def mount_targets(self, mount_targets, resources):
        for mt in mount_targets:
            mt["exports"] = [e for e in resources.get("Export", []) if e["export_set_id"] == mt["export_set_id"]]
            export_sets = [e for e in resources.get("ExportSet", []) if e["id"] == mt["export_set_id"]]
            mt["export_set"] = export_sets[0]
        return mount_targets

    def mysql_database_systems(self, database_systems, resources):
        for db_system in database_systems:
            # Trim version to just the number
            db_system["mysql_version"] = db_system["mysql_version"].split('-')[0]
        return database_systems

    def network_security_group(self, nsgs, resources):
        for nsg in nsgs:
            nsg["security_rules"] = [r for r in resources.get("NetworkSecurityGroupSecurityRule", []) if r["network_security_group_id"] == nsg["id"]]
        return nsgs

    def object_storage_buckets(self, buckets, resources):
        for bucket in buckets:
            bucket["display_name"] = bucket["name"]
        return buckets

    def oke_clusters(self, clusters, resources):
        for cluster in clusters:
            cluster["pools"] = [p for p in resources.get("NodePool", []) if p["cluster_id"] == cluster["id"]]
        return clusters

    def route_tables(self, route_tables, resources):
        rule_type_map = {'internetgateway': 'internet_gateway',
                         'natgateway':'nat_gateway',
                         'localpeeringgateway': 'local_peering_gateway',
                         'dynamicroutinggateway': 'dynamic_routing_gateway',
                         'drg': 'drg_attachment',
                        #  'drg': 'dynamic_routing_gateway',
                         'privateip':'private_ip',
                         'servicegateway': 'service_gateway'}
        for route_table in route_tables:
            for rule in route_table.get('route_rules', []):
                if len(rule['network_entity_id']) > 0:
                    rule['target_type'] = rule_type_map[rule['network_entity_id'].split('.')[1]]
                else:
                    rule['target_type'] = ''

        return route_tables

    def service_gateways(self, gateways, resources):
        for gateway in gateways:
            if gateway["route_table_id"] is None:
                gateway["route_table_id"] = ""
                for service in gateway['services']:
                    service_elements = service['service_name'].split()
                    del service_elements[1]
                    gateway['service_name'] = " ".join(service_elements)
                    # At the moment we only have 2 optiona All or OCI Object Storage hence we just need the first 3 characters
                    gateway['service_name'] = service_elements[0]
        return gateways

    def ip_to_instance(self, ip, resources):
        return
