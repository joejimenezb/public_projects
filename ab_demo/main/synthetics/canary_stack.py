from constructs import Construct
from aws_cdk import (
    Stack,
    aws_synthetics_alpha as synthetics,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_ssm as ssm,
    aws_kms as kms,
    Duration, Aspects, RemovalPolicy
)
import cdk_nag
class CanaryStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, stage: str, frb: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        url = {
            'dev':{
                    'front': ssm.StringParameter.from_string_parameter_attributes(self,'dev_f_endpoint', parameter_name= 'dev_f_endpoint').string_value,
                    'back':ssm.StringParameter.from_string_parameter_attributes(self,'dev_b_endpoint', parameter_name= 'dev_b_endpoint').string_value
            },
            'test':{
                    'front':ssm.StringParameter.from_string_parameter_attributes(self,'test_f_endpoint', parameter_name= 'test_f_endpoint').string_value,
                    'back':ssm.StringParameter.from_string_parameter_attributes(self,'test_b_endpoint', parameter_name= 'test_b_endpoint').string_value
            }
        }

        canary = synthetics.Canary(self, f"[{stage}Canary",
            schedule= synthetics.Schedule.rate(Duration.minutes(3)),
            test= synthetics.Test.custom(
                code=synthetics.Code.from_asset("canary"),
                handler="index.handler"
            ),
            runtime=synthetics.Runtime.SYNTHETICS_NODEJS_PUPPETEER_3_8,
            environment_variables={
                "url" : f"{url[stage][frb]}"
            }
        )

        canary_alarm = cloudwatch.Alarm(self, f"[{stage}CanaryAlarm",
            metric=canary.metric_success_percent(),
            evaluation_periods=5,
            threshold=90,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD       
        )
        encryption_key = kms.Key(self, 'encryption-key', enable_key_rotation=True)

        topic = sns.Topic(self, f"[{stage}Canary_SNS", master_key= encryption_key)

        canary_alarm.add_alarm_action(
            cw_actions.SnsAction(topic)
        )

        # Security Scan
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
        cdk_nag.NagSuppressions.add_stack_suppressions(self, [
        {"id":"AwsSolutions-S1", "reason":"This resource has no server access logs because is created by the stack"},
        {"id":"AwsSolutions-S2", "reason":"The S3 Bucket does not have an explicid policy restricting public access cause is created by the stack"},
        {"id":"AwsSolutions-IAM5",  "reason":"ERROR: The IAM user, role, or group uses AWS managed policies. An AWS managed policy is a standalone policy that is created and admini stered by AWS. Currently, many AWS managed policies do not restrict resource scope. Repla ce AWS managed policies with system specific (customer) managed policies. This is a granu lar rule that returns individual findings that can be suppressed with appliesTo. The find ings are in the format Policy::<policy> for AWS managed policies. Example: appliesTo: ['P olicy::arn:<AWS::Partition>:iam::aws:policy/foo']"},
        ])

