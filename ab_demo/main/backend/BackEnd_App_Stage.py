import aws_cdk as cdk
from constructs import Construct
from main.backend.ComponentsStack import ComponentsStack
from main.backend.ECS_Stack import ECSService
#from main.backend.DockerDeploy_Stack import DockerDeploy

class BackendApp(cdk.Stage):
     def __init__(self, scope: Construct, construct_id: str, arn_waf: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        components = ComponentsStack(self,"AppComponentsv2")
        ecs_app  = ECSService(self, "EcorpECSAppv2", wafacl= arn_waf)
