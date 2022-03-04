import aws_cdk as cdk

from cdk_pipeline.cdk_pipeline_stack import CdkPipelineStack
from cdk_pipeline.notification_stack import NotificationStack

from cdk_pipeline.config import config
from cdk_pipeline.naming import prepend_project_name


ENVIRONMENT = cdk.Environment(
    account=config['account'],
    region=config['region'],
)

app = cdk.App()

notification = NotificationStack(
    app,
    prepend_project_name(
        'NotificationStack'
    ),
    env=ENVIRONMENT,
)

branch = app.node.try_get_context('branch') or config.get('default_branch')

pipeline = CdkPipelineStack(
    app,
    prepend_project_name(
        'CdkPipelineStack'
    ),
    chatbot=notification.chatbot,
    branch=branch,
    env=ENVIRONMENT,
)

app.synth()
