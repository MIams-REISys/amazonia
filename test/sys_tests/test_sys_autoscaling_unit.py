#!/usr/bin/python3

from troposphere import ec2, Ref, Template, Join, Tags

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.autoscaling_unit import AutoscalingUnit
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.elb_config import ElbConfig


def main():
    userdata = """
#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
    """
    template = Template()

    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))

    internet_gateway = template.add_resource(
        ec2.InternetGateway('igname', Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', 'igname']))))
    internet_gateway.DependsOn = vpc.title

    gateway_attachment = template.add_resource(
        ec2.VPCGatewayAttachment(internet_gateway.title + 'Atch',
                                 VpcId=Ref(vpc),
                                 InternetGatewayId=Ref(internet_gateway)))
    gateway_attachment.DependsOn = internet_gateway.title

    private_subnets = [template.add_resource(ec2.Subnet('MySubnet',
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.1.0/24'))]
    public_subnets = [template.add_resource(ec2.Subnet('MySubnet2',
                                                       AvailabilityZone='ap-southeast-2a',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.2.0/24'))]
    nat = SingleInstance(title='nat',
                         keypair='pipeline',
                         si_image_id='ami-53371f30',
                         si_instance_type='t2.nano',
                         vpc=vpc,
                         subnet=public_subnets[0],
                         template=template,
                         instance_dependencies=internet_gateway.title)

    jump = SingleInstance(title='jump',
                          keypair='pipeline',
                          si_image_id='ami-dc361ebf',
                          si_instance_type='t2.nano',
                          vpc=vpc,
                          subnet=public_subnets[0],
                          template=template,
                          instance_dependencies=internet_gateway.title)

    service_role_arn = 'arn:aws:iam::1234567890124 :role/CodeDeployServiceRole'

    network_config = NetworkConfig(
        vpc=vpc,
        jump=jump,
        nat=nat,
        private_subnets=private_subnets,
        public_subnets=public_subnets,
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        unit_hosted_zone_name=None
    )
    elb_config = ElbConfig(
        protocols=['HTTP'],
        instanceports=['80'],
        loadbalancerports=['80'],
        path2ping='/index.html',
        elb_log_bucket=None,
        public_unit=True
    )
    asg_conifg = AsgConfig(
        minsize=1,
        maxsize=1,
        health_check_grace_period=300,
        health_check_type='ELB',
        keypair='pipeline',
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        userdata=userdata,
        cd_service_role_arn=service_role_arn,

        iam_instance_profile_arn=None,
        sns_topic_arn=None,
        sns_notification_types=None,
        hdd_size=None
    )


    unit1 = AutoscalingUnit(
        unit_title='app1',
        template=template,
        dependencies='app2',
        network_config=network_config,
        elb_config=elb_config,
        asg_config=asg_conifg
    )

    unit2 = AutoscalingUnit(
        unit_title='app2',
        network_config=network_config,
        template=template,
        elb_config=elb_config,
        asg_config=asg_conifg,
        dependencies='app1'
    )

    unit1.add_unit_flow(unit2)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
