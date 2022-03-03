from cdk_pipeline.config import config


def prepend_org_and_project_name(name):
    return f'{config["org_name"]}-{config["project_name"]}-{name}'
