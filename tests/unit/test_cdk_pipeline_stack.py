import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_pipeline.cdk_pipeline_stack import CdkPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_pipeline/cdk_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkPipelineStack(
        app,
        'cdk-pipeline',
        branch='_test'
    )
    template = assertions.Template.from_stack(stack)
#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })


def test_new_fake_test():
    assert True
