#!/usr/bin/python3

from troposphere import cloudfront, Ref, Tags, Template

from amazonia.classes.cfdistribution import CFDistribution
from amazonia.classes.cfdistribution_config import CFDistributionConfig
from amazonia.classes.cforigins_config import CFOriginsConfig
from amazonia.classes.cfcache_behaviors_config import CFCacheBehaviors


def main():
    template = Template()

    origins = [ CFOriginsConfig (
            template=template,
            domain_name='amazonia-elb-bucket.s3.amazonaws.com',
            origin_id='S3-bucket-id',
            origin_policy={
                'type' : 's3origin',
                'origin_access_identity': 'originaccessid1'
            }
        ),
        CFOriginsConfig(
            template=template,
            domain_name='amazonia-myStackap-DFODUO453-39457345.ap-southeast-2.elb.amazonaws.com',
            origin_id='www-origin',
            origin_policy={
                'type' : 'customorigin',
                'origin_protocol_policy' : 'https-only'
            }
        )
    ]

    cache_behaviors = [
        CFCacheBehaviors(
            path_pattern='/index.html',
            allowed_methods=['GET', 'POST'],
            cached_methods=['GET', 'POST'],
            target_origin_id='S3-bucket-id',
            forward_cookies='all',
            viewer_protocol_policy='allow-all',
            min_ttl=0,
            default_ttl=0,
            max_ttl=0,
            trusted_signers=['self']
        ),
        CFCacheBehaviors(
            path_pattern='/login.js',
            allowed_methods=['GET', 'POST', 'HEAD', 'DELETE', 'OPTIONS', 'PATCH', 'PUT'],
            cached_methods=['GET', 'POST'],
            target_origin_id='www-origin',
            forward_cookies='all',
            viewer_protocol_policy='https-only',
            min_ttl=0,
            default_ttl=0,
            max_ttl=0,
            trusted_signers=['self']
        ),
    ]

    distribution_config = CFDistributionConfig(
        aliases=['amazonia-myStackap-LXYP1MFWT9UC-145363293.ap-southeast-2.elb.amazonaws.com'],
        comment='SysTestCFDistribution',
        default_root_object='index.html',
        enabled=True,
        price_class='PriceClass_All',
        target_origin_id='originId',
        allowed_methods=['GET','HEAD'],
        cached_methods=['GET','HEAD'],
        trusted_signers=['self'],
        viewer_protocol_policy='https-only',
        min_ttl=0,
        default_ttl=0,
        max_ttl=0,
        error_page_path='index.html',
    )

    CFDistribution(title='cfdist',
                   template=template,
                   cforigins_config=origins,
                   cfcache_behaviors_config=cache_behaviors,
                   cfdistribution_config=distribution_config)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
