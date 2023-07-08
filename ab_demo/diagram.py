from diagrams import Cluster, Diagram
from diagrams.onprem.client import Users, User
from diagrams.aws.network import ElbApplicationLoadBalancer, Route53, CloudFront
from diagrams.aws.security import WAF
from diagrams.aws.storage import SimpleStorageServiceS3BucketWithObjects
from diagrams.aws.compute import ECS, ECR
from diagrams.aws.integration import Eventbridge
from diagrams.onprem.vcs import Github
from diagrams.aws.management import Cloudtrail, Cloudwatch, OrganizationsAccount
from diagrams.aws.integration import SNS
from diagrams.aws.devtools import Codepipeline, Codebuild, Codedeploy, CommandLineInterface


with Diagram("E-Corp Infr App", show=False, direction="LR"):

    with Cluster('App_Infra'):
        OrganizationsAccount('Target Account')
        user  = Users('Consumers')
        r53   = Route53('Route53')
        waf   = WAF('WAF')
        cf    = CloudFront('Cloudfront')
        front = SimpleStorageServiceS3BucketWithObjects('Static Website')
        with Cluster('VPC'):
            with Cluster('Public Subnet'):
                alb = ElbApplicationLoadBalancer ('ALB')
            
            with Cluster('Private Subnet'):
                 app_group = [
                    ECS('app1'),
                    ECS('app2'),
                    ECS('app3'),
                 ]
        user >> r53 >> waf >> cf >> front
        waf >> alb >> app_group

with Diagram("E-Corp CICD", show=False, direction="LR"):  
     
    with Cluster('CICD', "LR"):
        with Cluster('Organization', "LR"):
            accounts = [
                OrganizationsAccount('Dev'),
                OrganizationsAccount('Test'),
                OrganizationsAccount('Prod')
            ]
        gh       = Github('Github')
        with Cluster('Pipeline', 'LR'):
            approval = User('Approval')
            pipe     = Codepipeline('CodePipeline')
            deploy   = Codedeploy ('Deploy')
            build    = Codebuild ('Build')
            testing  = Codebuild('Integretion Testing')
            pipe >> approval >> build >> testing >> deploy >> approval

        with Cluster(label='Login and Monitoring', direction="LR"):
             cw  = Cloudwatch('CloudWatch')
             ct  = Cloudtrail('CloudTrail')
             sns = SNS('SNS')
             cw >> ct >> sns
        with Cluster ('Other AWS Services'):
             cw_synth = Cloudwatch('Synthetics')
             d_repo   = ECR('Docker Repo')
        
        gh >> pipe
        build >> d_repo
        deploy >> accounts
        testing >> cw_synth
        pipe >> cw


        



