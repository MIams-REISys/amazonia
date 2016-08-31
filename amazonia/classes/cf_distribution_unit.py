#!/usr/bin/python3

from troposphere import Tags, Ref, Output, Join, GetAtt, cloudfront

class CFDistributionUnit(object):
    def __init__(self, unit_title, template, cf_origins_config, cf_cache_behaviors_config, cf_distribution_config,
                 network_config):
        """
        Class to abstract a Cloudfront Distribution object
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distributionconfig.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param title: The title of this Cloudfront distribution
        :param template: Troposphere stack to append resources to
        :param cf_origins_config: A list of CFOriginsConfig objects
        :param cf_cache_behaviors_config: A list of CFCacheBehaviors objects
        :param cf_distribution_config: A CFDistributionConfig object
        """
        self.title = unit_title + 'CFDist'
        self.origins = []
        self.cache_behaviors = []
        self.default_cache_behavior = cloudfront.DefaultCacheBehavior()

        self.default_cache_behavior = self.add_default_cache_behavior(self.title, cf_distribution_config)

        # Populate origins
        self.add_origins(self.title, cf_origins_config)
        # Populate cache_behaviors
        self.add_cache_behaviors(self.title, cf_cache_behaviors_config)

        # Set distribution-wide parameters
        self.cf_dist = cloudfront.DistributionConfig(
            self.title,
            Aliases=cf_distribution_config.aliases,
            Comment=self.title,
            DefaultCacheBehavior=self.default_cache_behavior,
            CacheBehaviors=self.cache_behaviors,
            DefaultRootObject=cf_distribution_config.default_root_object,
            Enabled=cf_distribution_config.enabled,
            Origins=self.origins,
            PriceClass=cf_distribution_config.price_class
        )

        self.cf_dist = template.add_resource(cloudfront.Distribution(
            self.title,
            DistributionConfig=self.cf_dist
            )
        )

    def add_origins(self, title, cf_origins_config):
        """
        Create Cloudfront Origin objects and append to list of origins
        :param title: Title of this Cloudfront Distribution
        """
        for number, origin in enumerate(cf_origins_config):

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

    def add_cache_behaviors(self, title, cf_cache_behaviors_config):
        """
        Create Cloudfront CacheBehavior objects and append to list of cache_behaviors
        :param title: Title of this Cloudfront Distribution
        :param cf_cache_behaviors_config: list of CFCacheBehaviors
        """

        for number, cache_behavior in enumerate(cf_cache_behaviors_config):

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

    def add_default_cache_behavior(self, title, cf_distribution_config):
        """
        Create Cloudfront DefaultCacheBehavior object
        :return: Returns the created DefaultCacheBehavior object
        """
        return cloudfront.DefaultCacheBehavior(
            TargetOriginId=cf_distribution_config.target_origin_id,
            CachedMethods=cf_distribution_config.cached_methods,
            Compress=False,
            ForwardedValues=cloudfront.ForwardedValues(
                QueryString=False
            ),
            TrustedSigners=cf_distribution_config.trusted_signers,
            ViewerProtocolPolicy=cf_distribution_config.viewer_protocol_policy,
            MinTTL=cf_distribution_config.min_ttl,
            DefaultTTL=cf_distribution_config.default_ttl,
            MaxTTL=cf_distribution_config.max_ttl
        )