#!/usr/bin/python3

from troposphere import Tags, Ref, Output, Join, GetAtt, cloudfront

class CFDistribution(object):
    def __init__(self, title, template, cforigins_config, cfcache_behaviors_config, cfdistribution_config):
        """
        Class to abstract a Cloudfront Distribution object
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distributionconfig.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param title: The title of this Cloudfront distribution
        :param template: Troposphere stack to append resources to
        :param cforigins_config: A list of CFOriginsConfig objects
        :param cfcache_behaviors_config: A list of CFCacheBehaviors objects
        :param cfdistribution_config: A CFDistributionConfig object
        """
        self.title = title + 'CFDist'
        self.origins = []
        self.cache_behaviors = []
        self.default_cache_behavior = cloudfront.DefaultCacheBehavior()

        self.default_cache_behavior = self.add_default_cache_behavior(title, cfdistribution_config)

        # Populate origins
        self.add_origins(title, cforigins_config)
        # Populate cache_behaviors
        self.add_cache_behaviors(title, cfcache_behaviors_config)

        # Set distribution-wide parameters
        cfdist_params = {
            'Aliases' : cfdistribution_config.aliases,
            'Comment' : self.title,
            'DefaultCacheBehavior' : self.default_cache_behavior,
            'CacheBehaviors' : self.cache_behaviors,
            'DefaultRootObject' : cfdistribution_config.default_root_object,
            'Enabled' : True,
            'Origins' : self.origins,
            'PriceClass' : cfdistribution_config.price_class,
        }

        self.cf_dist = template.add_resource(cloudfront.DistributionConfig(
                self.title,
                # TODO: unpack cfdist_params
                **cfdist_params
            )
        )

    def add_origins(self, title, cforigins_config):
        """
        Create Cloudfront Origin objects and append to list of origins
        :param title: Title of this Cloudfront Distribution
        """
        for number, origin in enumerate(cforigins_config):

            if (origin.origin_policy['is_s3']):
                # Create S3Origin
                created_origin = cloudfront.Origin(
                    '{0}Origin{1}'.format(title, number),
                    DomainName=origin.domain_name,
                    Id=origin.origin_id,
                    S3OriginConfig=cloudfront.S3Origin(
                        OriginAccessIdentity=origin.origin_access_identity
                    )
                )
            else:
                # Create CustomOrigin
                created_origin = cloudfront.Origin(
                    '{0}Origin{1}'.format(title, number),
                    DomainName=origin.domain_name,
                    Id=origin.origin_id,
                    CustomOriginConfig=cloudfront.CustomOrigin(
                        HTTPPort=origin.http_port,
                        HTTPSPort=origin.https_port,
                        # Add input checking to ensure protocol_policy is one of (allow-all, http-only, https-only)
                        OriginProtocolPolicy=origin.origin_protocol_policy,
                        OriginSSLProtocols=origin.origin_ssl_protocols,
                    )
                )

            self.origins.append(created_origin)

    def add_cache_behaviors(self, title, cfcache_behaviors_config):
        """
        Create Cloudfront CacheBehavior objects and append to list of cache_behaviors
        :param title: Title of this Cloudfront Distribution
        :param cfcache_behaviors_config: list of CFCacheBehaviors
        """

        for number, cache_behavior in enumerate(cfcache_behaviors_config):

            created_cache_behavior = cloudfront.CacheBehavior(
                '{0}CacheBehavior{1}'.format(title, number),
                AllowedMethods=cache_behavior.allowed_methods,
                CachedMethods=cache_behavior.cached_methods,
                Compress=False,
                TargetOriginId=cache_behavior.target_origin_id,
                ForwardedValues=cloudfront.ForwardedValues(
                    Cookies=cloudfront.Cookies(
                        Forward=cache_behavior.forward_cookies
                    ),
                    QueryString=False
                ),
                TrustedSigners=cache_behavior.trusted_signers,
                ViewerProtocolPolicy=cache_behavior.viewer_protocol_policy,
                MinTTL=cache_behavior.min_ttl,
                DefaultTTL=cache_behavior.default_ttl,
                MaxTTL=cache_behavior.max_ttl,
                PathPattern=cache_behavior.path_pattern,
                SmoothStreaming=False
            )

            self.cache_behaviors.append(created_cache_behavior)

    def add_default_cache_behavior(self, title, cfdistribution_config):
        """
        Create Cloudfront DefaultCacheBehavior object
        :return: Returns the created DefaultCacheBehavior object
        """
        return cloudfront.DefaultCacheBehavior(
            TargetOriginId=cfdistribution_config.target_origin_id,
            CachedMethods=cfdistribution_config.cached_methods,
            Compress=False,
            ForwardedValues=cloudfront.ForwardedValues(
                QueryString=False
            ),
            TrustedSigners=cfdistribution_config.trusted_signers,
            ViewerProtocolPolicy=cfdistribution_config.viewer_protocol_policy,
            MinTTL=cfdistribution_config.min_ttl,
            DefaultTTL=cfdistribution_config.default_ttl,
            MaxTTL=cfdistribution_config.max_ttl
        )