#!/usr/bin/python3

from troposphere import ec2, Ref, Template, Join, Tags

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.zd_autoscaling_unit import ZdtdAutoscalingUnit
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.network_config import NetworkConfig


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

    cd_service_role_arn = 'arn:aws:iam::1234567890124 :role/CodeDeployServiceRole'

    network_config = NetworkConfig(public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'}, vpc=vpc,
                                   public_subnets=public_subnets, private_subnets=private_subnets, nat=nat,
                                   jump=jump, unit_hosted_zone_name=None)
    protocols = ['HTTP']
    instanceports = ['80']
    loadbalancerports = ['80']
    path2ping = '/index.html'
    minsize = 1
    maxsize = 1
    health_check_grace_period = 300
    health_check_type = 'ELB'
    keypair = 'pipeline'
    image_id = 'ami-dc361ebf'
    instance_type = 't2.nano'

    elb_config = ElbConfig(protocols=protocols, instanceports=instanceports, loadbalancerports=loadbalancerports,
                           elb_log_bucket=None, path2ping=path2ping, public_unit=True)
    common_asg_config = AsgConfig(sns_topic_arn=None, sns_notification_types=None,
                                  cd_service_role_arn=cd_service_role_arn,
                                  health_check_grace_period=health_check_grace_period,
                                  health_check_type=health_check_type, keypair=keypair, minsize=minsize,
                                  maxsize=maxsize, image_id=image_id,
                                  instance_type=instance_type, userdata=userdata,
                                  iam_instance_profile_arn=None, hdd_size=8)
    blue_asg_config = AsgConfig(sns_topic_arn=None, sns_notification_types=None,
                                cd_service_role_arn=None,
                                health_check_grace_period=None,
                                health_check_type=None, keypair=None, minsize=None,
                                maxsize=None, image_id=None,
                                instance_type=None, userdata=None,
                                iam_instance_profile_arn=None, hdd_size=None)
    green_asg_config = AsgConfig(sns_topic_arn=None, sns_notification_types=None,
                                 cd_service_role_arn=None,
                                 health_check_grace_period=None,
                                 health_check_type=None, keypair=None, minsize=None,
                                 maxsize=None, image_id=None,
                                 instance_type=None, userdata=None,
                                 iam_instance_profile_arn=None, hdd_size=None)

    unit1 = ZdtdAutoscalingUnit(
        unit_title='app1',
        template=template,
        zdtd_state='blue',
        dependencies=['app2'],
        network_config=network_config,
        elb_config=elb_config,
        common_asg_config=common_asg_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config
    )

    unit2 = ZdtdAutoscalingUnit(
        unit_title='app2',
        template=template,
        zdtd_state='green',
        dependencies=['app1'],
        network_config=network_config,
        elb_config=elb_config,
        common_asg_config=common_asg_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config
    )

    unit3 = ZdtdAutoscalingUnit(
        unit_title='app3',
        template=template,
        zdtd_state='both',
        dependencies=None,
        network_config=network_config,
        elb_config=elb_config,
        common_asg_config=common_asg_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config
    )

    unit1.add_unit_flow(unit2)
    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == '__main__':
    main()
