import aws_cdk as cdk

from aws_cdk.aws_codebuild import Artifacts
from aws_cdk.aws_codebuild import BuildEnvironmentVariable
from aws_cdk.aws_codebuild import BuildSpec
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.aws_codebuild import EventAction
from aws_cdk.aws_codebuild import FilterGroup
from aws_cdk.aws_codebuild import LinuxBuildImage
from aws_cdk.aws_codebuild import Project
from aws_cdk.aws_codebuild import ReportGroup
from aws_cdk.aws_codebuild import Source

from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.aws_iam import Role
from aws_cdk.aws_iam import ServicePrincipal

from aws_cdk.aws_s3 import Bucket

from cdk_pipeline.naming import prepend_project_name


class ContinuousIntegrationStack(cdk.Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        github = Source.git_hub(
            owner='keenangraham',
            repo='cdk-pipeline',
            webhook=True,
        )
        report_bucket = Bucket(
            self,
            'ReportBucket',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        report_artifacts = Artifacts.s3(
            bucket=report_bucket,
        )
        continuous_integration_project = Project(
            self,
            prepend_project_name(
                'ContinuousIntegrationProject'
            ),
            source=github,
            environment=BuildEnvironment(
                build_image=LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            build_spec=BuildSpec.from_object(
                {
                    'version': '0.2',
                    'phases': {
                        'install': {
                            'runtime-versions': {
                                'python': '3.9',
                            },
                            'commands': [
                                'echo $CODEBUILD_RESOLVED_SOURCE_VERSION',
                                'echo $CODEBUILD_SOURCE_REPO_URL',
                                'echo $CODEBUILD_WEBHOOK_EVENT',
                                'echo $CODEBUILD_WEBHOOK_TRIGGER',
                                'echo $(git log -1 --pretty="%s (%h) - %an")',
                                'pip3 install -r requirements.txt -r requirements-dev.txt',
                            ]
                        },
                        'build': {
                            'commands': [
                                'ls',
                                'echo CI',
                                'echo $TEST',
                                'python -m pytest --junitxml=pytest_report.xml --cov cdk_pipeline --cov-report html --cov-report term',
                            ]
                        }
                    },
                    'reports': {
                        'unit_tests': {
                            'files': 'pytest_report.xml',
                            'file_format': 'JUNITXML',
                        }
                    },
                    'artifacts': {
                        'files': 'htmlcov/**/*',
                    }
                }
            ),
            environment_variables={
                'TEST': BuildEnvironmentVariable(
                    value='SOMETHING!'
                )
            },
            badge=True,
            artifacts=report_artifacts,
        )
        resource_access_role = Role(
            self,
            'ResourceAccessRole',
            assumed_by=ServicePrincipal(
                'codebuild.amazonaws.com'
            )
        )
        project_name = continuous_integration_project.project_name
        log_group_arn = cdk.Stack.of(self).format_arn(
            service='logs',
            resource='log-group',
            arn_format=cdk.ArnFormat.COLON_RESOURCE_NAME,
            resource_name=f'/aws/codebuild/{project_name}',
        )
        log_group_star_arn = f'{log_group_arn}:*'
        public_read_policy = PolicyStatement(
            resources=[
                log_group_star_arn,
            ],
            actions=[
                'logs:GetLogEvents'
            ],
        )
        resource_access_role.add_to_principal_policy(
            public_read_policy
        )
        cfn_project = continuous_integration_project.node.default_child
        cfn_project.visibility = 'PUBLIC_READ'
        cfn_project.resource_access_role = resource_access_role.role_arn
