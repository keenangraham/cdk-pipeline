from cdk_pipeline.config import config


def prepend_project_name(name):
    return f'{config["project_name"]}-{name}'


def prepend_branch_context(scope, name):
    return f'{scope.node.try_get_context("branch")}-{name}'
