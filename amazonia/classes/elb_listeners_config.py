#!/usr/bin/python3


class ElbListenersConfig(object):
    def __init__(self, instance_protocol, loadbalancer_protocol, instance_port, loadbalancer_port):
        """
        Simple ELB listener config class to contain elb listener related parameters
        :param instance_protocol: instance_protocol for ELB to communicate with webserver
        :param loadbalancer_protocol: loadbalancer_protocol for world to communicate with ELB
        :param instance_port: ports for ELB and webserver to communicate via
        :param loadbalancer_port: ports for public and ELB to communicate via
        """
        self.instance_protocol = instance_protocol
        self.loadbalancer_protocol = loadbalancer_protocol
        self.instance_port = instance_port
        self.loadbalancer_port = loadbalancer_port
