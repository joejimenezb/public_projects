
from constructs import Construct
from aws_cdk import (
    Stack, Aws,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cloudwatch as cloudwatch,
    Aspects, RemovalPolicy,
    aws_elasticloadbalancingv2 as elbv2
)
from properties import props
import cdk_nag


class ECSService(Stack):
    def __init__(self, scope: Construct, construct_id: str, wafacl, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.props = props()
        #Repo
        self.repo = ecr.Repository.from_repository_name(
            self,
            "ecr-repo",
            repository_name=self.props['namespace']
        )

        #creating the VPC
        self.vpc = ec2.Vpc(self, "MyVpc", max_azs=3)     # default is all AZs in region
        self.flowlog = ec2.FlowLog( self, 'MyVpcFlowlog',
                                   resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc))
        #creating the cluster
        self.cluster = ecs.Cluster(self, "MyCluster",
                                   vpc=self.vpc,
                                   container_insights=True)
        #alb and ecs fargate
        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "MyFargateService",
            cluster=self.cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=2,            # Default is 1
            task_image_options   = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(
                        repository = self.repo,
                        tag        = "cdk"
                        ),
                enable_logging=True,
                container_name="demo",
                container_port=80
                ),
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=True,  #  Default is True
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True))  #rollback if fail
        
        lb_s3 = s3.Bucket(
            self, 'AlbLogS3',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True

        )
        self.fargate_service.load_balancer.log_access_logs(
            bucket=lb_s3,
            prefix="ECorp/AlbLogs"
        )
       #ALB DNS
        self.alb_dns = self.fargate_service.load_balancer.load_balancer_dns_name

       
        #auto scaling
        scale_tgt = self.fargate_service.service.auto_scale_task_count(
            min_capacity = 2,
            max_capacity = 4)
        
        scale_tgt.scale_on_cpu_utilization(
            "CPUScaling",
            target_utilization_percent = 75
        )

        #alarm
        failure_alarm = cloudwatch.Alarm(
            self, "backend_alarm",
            metric=self.fargate_service.target_group.metric_unhealthy_host_count(),
            threshold=1,
            evaluation_periods=2
        )
        #cloudfron for alb 
        # waf_id = f'arn:aws:wafv2:us-east-1:{Aws.ACCOUNT_ID}:global/webacl/waf-cloudfront/{wafacl}'
        # lb_cloudfront = cloudfront.Distribution(
        #     self, 'DeployEcorpBackend',
        #     default_behavior=cloudfront.BehaviorOptions(
        #         origin=origins.LoadBalancerV2Origin(self.fargate_service.load_balancer, http_port=80)
        #     ),
        #     log_bucket=lb_s3,
        #     log_file_prefix="CF_Logs",
        #     web_acl_id=waf_id
        # )

        
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        cdk_nag.NagSuppressions.add_stack_suppressions(self, [
            {"id":"AwsSolutions-EC23", "reason":"ELB is disging to be public facing"},
            {"id":"AwsSolutions-S1", "reason":"S3 Bucket is login bucket"},
            {"id":"AwsSolutions-IAM5",  "reason":"The IAM entity contains wildcard permissions and does not have a cdk-nag rule suppression with evidence for those permission."}, 
            ]
        )








        


