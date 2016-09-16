#!/usr/bin/python3

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.sns import SNS
from nose.tools import *
from troposphere import Template, ec2, Ref, Join


def test_not_nat_single_instance():
    """
    Tests for instances where 'nat' is NOT the first 3 letters  of the title and expect natting (SourceDestCheck)
    to be disabled and the PrivateIp to be displayed in the output.
    :return: Pass
    """
    jump_titles = ['jump', 'Jump', '2Jump', 'other', 'natjump', 'testStackJump']

    for title in jump_titles:
        si = create_si(title)
        si_sdc = si.single.SourceDestCheck
        assert_equals(si_sdc, 'true')
        sio = si.template.outputs[title].Description
        assert_in('PublicIp', sio)
        assert_equals(si.single.IamInstanceProfile, 'instance-profile')


def test_jump_with_hostedzone_creates_r53_record():
    """
    Tests that creating a jump host and supplying a hostedzone creates an elastic IP, r53 recordset and output for
    the jump host
    :return: Pass
    """
    jump_titles = ['jump1', 'jump2']

    for title in jump_titles:
        si = create_si(title)

        assert_equals(si.eip_address.Domain, 'vpc')
        assert_equals(si.si_r53.HostedZoneName, 'my.hostedzone.')

        sio = si.template.outputs[title + 'URL'].Value
        assert_equals(sio, si.si_r53.Name)


def test_nat_single_instance():
    """
    Tests that creating a NAT and supplying a True value to 'alert' and at least one email in a list to alert_emails
    will create an SNS topic
    """

    title = 'SnsTopic'
    si = create_si('nat', is_nat=True)
    si_sdc = si.single.SourceDestCheck
    assert_equals(si_sdc, 'false')
    sio = si.template.outputs['nat'].Description
    assert_in('PrivateIp', sio)
    assert_equals(si.single.IamInstanceProfile, 'instance-profile')
    assert_equals(si.sns_topic.trop_topic.title, title)
    assert_is(type(si.sns_topic.trop_topic.DisplayName), Join)
    assert_equals(si.template.outputs[title].Description, 'SNS Topic')
    assert_equals(si.sns_topic.trop_topic.Subscription[0].title, title + 'Subscription0')
    assert_equals(si.sns_topic.trop_topic.Subscription[0].Endpoint, 'some@email.com')
    assert_equals(si.sns_topic.trop_topic.Subscription[0].Protocol, 'email')
    assert_equals(si.sns_topic.alarms[0].title, title + 'Alarm0')
    assert_equals(si.sns_topic.alarms[0].AlarmDescription, 'Alarms when nat metric CPUUtilization reaches 60')
    assert_equals(type(si.sns_topic.alarms[0].AlarmActions[0]), type(Ref('abc')))
    assert_equals(type(si.sns_topic.alarms[0].OKActions[0]), type(Ref('abc')))
    assert_equals(si.sns_topic.alarms[0].MetricName, 'CPUUtilization')
    assert_equals(si.sns_topic.alarms[0].Namespace, 'AWS/EC2')
    assert_equals(si.sns_topic.alarms[0].Threshold, '60')
    assert_equals(si.sns_topic.alarms[0].ComparisonOperator, 'GreaterThanOrEqualToThreshold')
    assert_equals(si.sns_topic.alarms[0].EvaluationPeriods, '1')
    assert_equals(si.sns_topic.alarms[0].Period, '300')
    assert_equals(si.sns_topic.alarms[0].Statistic, 'Sum')
    assert_equals(si.sns_topic.alarms[0].Dimensions[0].Name, 'InstanceId')


def create_si(title, is_nat=False):
    """
    Helper function to create Single instance Troposhpere object to interate through.
    :param title: name of instance
    :param is_nat: is the instance a nat
    :return: Troposphere object for single instance, security group and output
    """
    vpc = 'vpc-12345'
    dependencies = 'igw-12345'
    public_hosted_zone_name = None if is_nat else 'my.hostedzone.'
    template = Template()
    subnet = template.add_resource(ec2.Subnet('subnet12345',
                                              AvailabilityZone='ap-southeast-2a',
                                              VpcId=vpc,
                                              CidrBlock='10.0.1.0/24'))
    sns_topic = SNS(template)
    sns_topic.add_subscription('some@email.com', 'email')
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=subnet,
        public_hosted_zone_name=public_hosted_zone_name,
        instance_dependencies=dependencies,
        is_nat=is_nat,
        iam_instance_profile_arn='my/instance-profile',
        sns_topic=sns_topic
    )
    si = SingleInstance(title=title,
                        template=template,
                        single_instance_config=single_instance_config
                        )

    return si
