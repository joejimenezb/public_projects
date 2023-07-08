import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    pipelines as pipelines,
    aws_ssm as ssm,
    aws_codestarnotifications as notifications,
    Aspects
)
from constructs import Construct
from DockerBuild.DockerCD_Stage import DockerCD_Stage
from main.frontend.website_stage import WebsiteStage
from main.backend.BackEnd_App_Stage import BackendApp
from main.waf.waf_cf_stage import WAF_Satege
from main.synthetics.canary_stage import CanaryStage

import cdk_nag

class MainPipeline(Stack):

    def __init__(self, scope: Construct, construct_id: str, props,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # getting the properties from app 

        self.props = props.copy()  
        dev_f_endpoint  = ssm.StringParameter.from_string_parameter_attributes(self,'dev_f_endpoint', parameter_name= 'dev_f_endpoint').string_value
        dev_b_endpoint  = ssm.StringParameter.from_string_parameter_attributes(self,'dev_b_endpoint', parameter_name= 'dev_b_endpoint').string_value
        test_f_endpoint = ssm.StringParameter.from_string_parameter_attributes(self,'test_f_endpoint', parameter_name= 'test_f_endpoint').string_value
        test_b_endpoint = ssm.StringParameter.from_string_parameter_attributes(self,'test_b_endpoint', parameter_name= 'test_b_endpoint').string_value
        
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            cross_account_keys=True,
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    repo_string=self.props['github_repo'],
                    branch="main",
                    connection_arn=f"arn:aws:codestar-connections:{self.props['region']}:{self.props['tooling']}:connection/{self.props['github_arn']}"
                ),
                    #Create the connection in the console (https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-create-github.html#connections-create-github-cli)
                commands=[
                    "npm install -g aws-cdk",  # Installs the cdk cli on Codebuild
                    "pip install -r requirements.txt",  # Instructs Codebuild to install required packages
                    "zip -r source.zip DockerBuild", 
                    "mv source.zip DockerBuild",
                    "bandit -r app_code", # security scan for app code
                    "cdk synth",
                    "checkov -d cdk.out --framework cloudformation --baseline baseline/.checkov.baseline", # IaC security scan 2
                    "find cdk.out -iname \*.template.json -exec cfn-lint {} \;" # # IaC security scan 3
                ]
            ),
        )
        # Delpoyment waves represent the different environments (Dev, Test, Prod), each wave deploys the entire CDK project (all stacks)
        #---------------------------------------------------------------
        #------------------------------dev Wave Start-------------------
        #---------------------------------------------------------------
        
        #Docker Deploy
        dockercd = pipeline.add_wave(
            "Docker_wave",
             pre=[pipelines.ManualApprovalStep("DeployImageDev")]
        )
        #setting docker
        dockercd.add_stage (

            DockerCD_Stage( self, "DevDockerCD", 
                           env=cdk.Environment(account=self.props['dev'], region=self.props['region'])
            ),
            post=[
                pipelines.ShellStep(
                    "DockerBuild",
                    commands=[f"sleep 180"])]
        )
        
        # WAF Wave
        waf_wave = pipeline.add_wave(
            "WAF_wave",
            #pre=[pipelines.ManualApprovalStep("Deploy_WAF")]
        )
        
        waf_wave.add_stage(
            WAF_Satege(#WAF must be deploy in us-east-1 
                self,
                "EcorpWAF",
                env=cdk.Environment(account=self.props['dev'], region='us-east-1') 
            )
        )
        
        dev_wave = pipeline.add_wave(
            "Development_Deploy_Wave",
            #pre=[pipelines.ManualApprovalStep("DeployToDev")]
        )
        # Frontend
        dev_wave.add_stage(
            WebsiteStage(
            scope=self, 
            construct_id="DevFrontend",
            arn_waf=self.props['dev_WAFarn'],
            env=cdk.Environment(account=self.props['dev'], region=self.props['region'])
            ),
            post=[
                pipelines.ShellStep(
                    "validating front",
                    commands=[f"curl -Ssf {dev_f_endpoint}"])]
            )
        # Backend
        dev_wave.add_stage(
            BackendApp(
                scope= self,
                construct_id= "DevBackend",
                arn_waf=self.props['dev_WAFarn'],
                env=cdk.Environment(account=self.props['dev'], region=self.props['region'])
            ),
            post=[
                pipelines.ShellStep(
                    "validating back",
                    commands=[f"curl -Ssf {dev_b_endpoint}"
                    ]
                )
            ]
        )
        #Canary deployment
        dev_canary_w = pipeline.add_wave(
            "SyntheticsCanary",
            #pre=[pipelines.ManualApprovalStep("CanaryDeploy")]
        )
        dev_canary_w.add_stage(
            CanaryStage(
                self,
                "DevBackCanary",
                stage="dev",
                frb='back'
            )
        )
        dev_canary_w.add_stage(
            CanaryStage(
                self,
                "DevFronCanary",
                stage="dev",
                frb='front'
            )
        )
        #---------------------------------------------------------------
        #-------------------------dev Wave End--------------------------
        #---------------------------------------------------------------
        #-------------------------test Wave Start-----------------------
        #---------------------------------------------------------------
        
        #Docker Deploy
        # test_dockercd = pipeline.add_wave(
        #     "Test_Docker_wave",
        #      #pre=[pipelines.ManualApprovalStep("DeployImageDev")]
        # )
        #setting docker
        dockercd.add_stage (

            DockerCD_Stage( self, "DockerCD", 
                           env=cdk.Environment(account=self.props['test'], region=self.props['region'])
            ),
            post=[
                pipelines.ShellStep(
                    "DockerBuild",
                    commands=[f"sleep 180"])]
        )
        
        # Test WAF Wave
        # test_waf_wave = pipeline.add_wave(
        #     "TestWAF_wave",
        #     #pre=[pipelines.ManualApprovalStep("Deploy_WAF")]
        # )
        
        waf_wave.add_stage(
            WAF_Satege(#WAF must be deploy in us-east-1 
                self,
                "TestEcorpWAF",
                env=cdk.Environment(account=self.props['test'], region='us-east-1') 
            )
        )
        
        test_wave = pipeline.add_wave(
            "test_Deploy_Wave",
            #pre=[pipelines.ManualApprovalStep("DeployToDev")]
        )
        # Frontend
        test_wave.add_stage(
            WebsiteStage(
                scope=self, 
                construct_id="TestFrontend",
                arn_waf=props['test_WAFarn'],
                env=cdk.Environment(account=self.props['test'], region=self.props['region'])
            ),
            post=[
                pipelines.ShellStep(
                    "validating front",
                    commands=[f"curl -Ssf {test_f_endpoint}"])]
            )
        # Backend
        test_wave.add_stage(
            BackendApp(
                scope= self,
                construct_id= "TestBackend",
                arn_waf=props['test_WAFarn'],
                env=cdk.Environment(account=self.props['test'], region=self.props['region'])
            ),
            post=[
                pipelines.ShellStep(
                    "validating back",
                    commands=[f"curl -Ssf {test_b_endpoint}"])]
        )

          #Canary deployment
        dev_canary_w = pipeline.add_wave(
            "TestSyntheticsCanary",
            #pre=[pipelines.ManualApprovalStep("CanaryDeploy")]
        )
        dev_canary_w.add_stage(
            CanaryStage(
                self,
                "TestBackCanary",
                stage="test",
                frb='back'
            )
        )
        dev_canary_w.add_stage(
            CanaryStage(
                self,
                "TestFronCanary",
                stage="test",
                frb='front' 
            )
        )
        #---------------------------------------------------------------
        #------------------------------test Wave Start------------------
        #---------------------------------------------------------------

        # Security Scan
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        cdk_nag.NagSuppressions.add_stack_suppressions(self, [
      {"id":"AwsSolutions-KMS5",  "reason":"Symetric key is created and manage by the cdk stack"},
      {"id":"AwsSolutions-S1", "reason": "S3 is created and manage by the stack "},
      {"id":"AwsSolutions-IAM5",  "reason":"The IAM entity contains wildcard permissions and does not have a cdk-nag rule suppression with evidence for those permission."},
       ])
