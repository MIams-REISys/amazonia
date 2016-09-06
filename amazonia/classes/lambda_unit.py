#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Ref
from troposphere.awslambda import Code, VPCConfig, Function


class LambdaUnit(SecurityEnabledObject):
    def __init__(self, unit_title, template, dependencies, network_config, lambda_config):
        """
        Amazonia lambda unit definition
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/awslambda.py
        :param unit_title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param template: Troposphere stack to append resources to
        :param network_config: object containing network related variables
        :param lambda_config: object containing lambda related variablea
        """
        self.title = unit_title + 'Lambda'
        self.public_cidr = network_config.public_cidr
        self.dependencies = dependencies if dependencies else []

        super(LambdaUnit, self).__init__(vpc=network_config.vpc, title=self.title, template=template)

        self.trop_lambda_function = template.add_resource(
            Function(self.title,
                     Code=Code(S3Bucket=lambda_config.lambda_s3_bucket, S3Key=lambda_config.lambda_s3_key),
                     Description=lambda_config.lambda_description,
                     FunctionName=lambda_config.lambda_function_name,
                     Handler=lambda_config.lambda_handler,
                     MemorySize=lambda_config.lambda_memory_size,
                     Role=lambda_config.lambda_role_arn,
                     Runtime=lambda_config.lambda_runtime,
                     Timeout=lambda_config.lambda_timeout,
                     VpcConfig=VPCConfig(SubnetIds=[Ref(x) for x in network_config.private_subnets],
                                         SecurityGroupIds=[Ref(self.security_group)])))

        if network_config.nat_highly_available:
            self.add_egress(receiver=self.public_cidr, port='-1')  # All Traffic to Nat gateways
        else:
            self.add_flow(receiver=network_config.nat, port='-1')  # All Traffic to Nat

    def get_dependencies(self):
        """
        :return: returns a list of units lambda needs to access
        """
        return self.dependencies

    def get_destinations(self):
        """
        Raises invalid flow error
        """
        raise InvalidFlowError('Error: lambda_unit {0} may only be the originator of flow, not the destination.'
                               .format(self.title))

    def get_inbound_ports(self):
        """
        Raises invalid flow error
        """
        raise InvalidFlowError('Error: lambda_unit {0} may only be the originator of flow, not the destination.'
                               .format(self.title))

    def add_unit_flow(self, receiver):
        """
        Create security group flow from this lambda function to another unit
        :param receiver: Other Amazonia Unit
        """
        for port in receiver.get_inbound_ports():
            for destination in receiver.get_destinations():
                self.add_flow(receiver=destination, port=port)


class InvalidFlowError(Exception):
    def __init__(self, value):
        self.value = value
