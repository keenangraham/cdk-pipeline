import aws_cdk as cdk

from cdk_pipeline.cdk_pipeline_stack import CdkPipelineStack
from cdk_pipeline.notification_stack import NotificationStack
from cdk_pipeline.config import config


ENVIRONMENT = cdk.Environment(
    account=config['account'],
    region=config['region'],
)

app = cdk.App()


pipeline = CdkPipelineStack(
    app,
    'CdkPipelineStack',
    env=ENVIRONMENT,
)

app.synth()
