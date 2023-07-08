from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    CfnOutput as cout,
    Aspects
)
import cdk_nag
class DockerDeploy(Stack):
    def __init__(self, scope: Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        deployment = s3_deployment.BucketDeployment(
            self, "DockerZip", 
            sources=[s3_deployment.Source.asset("DockerBuild")],
            destination_bucket=props['bucket'],
            prune= True
        )

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        cdk_nag.NagSuppressions.add_stack_suppressions(self, [
            {"id":"AwsSolutions-IAM4", "reason": "Stack policy is created by the stack"},
            {"id":"AwsSolutions-IAM5", "reason": "ERROR: The IAM user, role, or group uses AWS managed policies. An AWS managed policy is a standalone policy that is created and admini stered by AWS. Currently, many AWS managed policies do not restrict resource scope. Repla ce AWS managed policies with system specific (customer) managed policies. This is a granu lar rule that returns individual findings that can be suppressed with appliesTo. The find ings are in the format Policy::<policy> for AWS managed policies. Example: appliesTo: ['P olicy::arn:<AWS::Partition>:iam::aws:policy/foo']"},
        ])
        





