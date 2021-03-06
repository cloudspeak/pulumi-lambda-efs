from .development_environment import DevelopmentEnvironment

# These are the default environment variable values used on Lambda.  We have to know
# these because we can only overwrite them, not append them.
LdLibraryPathDefaults = "/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib"
PathDefaults = "/var/lang/bin:/usr/local/bin:/usr/bin/:/bin:/opt/bin"
PythonpathDefaults = "/var/runtime"

mount_location = "/mnt/efs"
brew_prefix = "lambda_packages/linuxbrew"
pip_prefix = "lambda_packages/pip"


def get_environment_function_args(development_environment: DevelopmentEnvironment):
    """
    Helper function for creating Lambda functions which can read libraries
    which were installed to EFS using the scripts in this package.  Specifically,
    it returns the arguments which should be passed to a Pulumi `Function`
    constructor so that the function can access the libraries installed in an
    environment created by a `DevelopmentEnvironment` resource.

    It can be used in conjunction with the * operator like so:

    example_function = lambda_.Function("exampleFunction",
        code="lambda.zip",
        handler="handler.my_handler",
        role=example_role.arn,
        runtime="python3.8",
        opts=ResourceOptions(depends_on=[environment]),
        **get_environment_function_args(environment)
    )

    Note using the function in this way will overwite the `vpc_config`,
    `file_system_config` and `environment` parameters if they were present.
    """
    return {
        "vpc_config": {
            "security_group_ids": [development_environment.security_group_id],
            "subnet_ids": development_environment.public_subnet_ids,
        },
        "file_system_config": {
            "arn": development_environment.efs_access_point_arn,
            "local_mount_path": mount_location,
        },
        "environment": {
            "variables": {
                "LAMBDA_PACKAGES_PATH": mount_location,
                "LD_LIBRARY_PATH": f"{LdLibraryPathDefaults}:{mount_location}/{brew_prefix}/lib",
                "PATH": f"{PathDefaults}:{mount_location}/{brew_prefix}/bin",
                "PYTHONPATH": f"{PythonpathDefaults}:{mount_location}/{pip_prefix}",
            }
        },
    }
