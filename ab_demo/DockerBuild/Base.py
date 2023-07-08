from aws_cdk import (
    aws_s3 as s3,
    aws_ecr,
    aws_codebuild,
    aws_ssm,
    App, Aws, CfnOutput, Duration, RemovalPolicy, Stack, Aspects
)

import cdk_nag

class Base(Stack):
    def __init__(self, app: App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # pipeline requires versioned bucket
        bucket = s3.Bucket(
            self, "SourceBucket",
            bucket_name=f"{props['namespace'].lower()}-{Aws.ACCOUNT_ID}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.KMS_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=False,
            enforce_ssl=True,)
        # ssm parameter to get bucket name later
        bucket_param = aws_ssm.StringParameter(
            self, "ParameterB",
            parameter_name=f"{props['namespace']}-bucket",
            string_value=bucket.bucket_name,
            description='cdk pipeline bucket'
        )
        # ecr repo to push docker container into
        ecr = aws_ecr.Repository(
            self, "ECR",
            repository_name=f"{props['namespace']}",
            removal_policy=RemovalPolicy.DESTROY,
            image_scan_on_push=True,
        )
        # codebuild project meant to run in pipeline
        cb_docker_build = aws_codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"{props['namespace']}-Docker-Build",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='DockerBuild/pipeline_delivery/docker_build_buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,
            ),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'ecr': aws_codebuild.BuildEnvironmentVariable(
                    value=ecr.repository_uri),
                'tag': aws_codebuild.BuildEnvironmentVariable(
                    value='cdk')
            },
            description='Pipeline for CodeBuild',
            timeout=Duration.minutes(60),
        )
        # codebuild iam permissions to read write s3
        bucket.grant_read_write(cb_docker_build)

        # codebuild permissions to interact with ecr
        ecr.grant_pull_push(cb_docker_build)

        CfnOutput(
            self, "ECRURI",
            description="ECR URI",
            value=ecr.repository_uri,
        )
        CfnOutput(
            self, "S3Bucket",
            description="S3 Bucket",
            value=bucket.bucket_name
        )
         # Security Scan
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
        
        cdk_nag.NagSuppressions.add_stack_suppressions(self, [
            {"id":"AwsSolutions-IAM5", "reason": "ERROR: The IAM user, role, or group uses AWS managed policies. An AWS managed policy is a standalone policy that is created and admini stered by AWS. Currently, many AWS managed policies do not restrict resource scope. Repla ce AWS managed policies with system specific (customer) managed policies. This is a granu lar rule that returns individual findings that can be suppressed with appliesTo. The find ings are in the format Policy::<policy> for AWS managed policies. Example: appliesTo: ['P olicy::arn:<AWS::Partition>:iam::aws:policy/foo']"},
            {"id":"AwsSolutions-S1", "reason":"S3 is not meant to have trafic other than a LZ for ecr images"},
            {"id":"AwsSolutions-CB4", "reason":"Encription is manage by S3"},
            {"id":"AwsSolutions-CB3", "reason":"Docker images are been build in this pipeline"},
            ])

        self.output_props = props.copy()
        self.output_props['bucket']= bucket
        self.output_props['cb_docker_build'] = cb_docker_build

    # pass objects to another stack
    @property
    def outputs(self):
        return self.output_props
