from aws_cdk import Stack

from constructs import Construct


class CdkPipelineStack(Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
