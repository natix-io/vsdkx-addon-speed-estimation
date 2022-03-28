from setuptools import setup, find_namespace_packages

setup(
    name='vsdkx-addon-speed-estimation',
    url='https://github.com/natix-io/vsdkx-addon-speed-estimation.git',
    author='Nicole',
    author_email='nicole@natix.io',
    namespace_packages=['vsdkx', 'vsdkx.addon'],
    packages=find_namespace_packages(include=['vsdkx*']),
    dependency_links=[
        'git+https://gitlab+deploy-token-485942:VJtus51fGR59sMGhxHUF@gitlab.com/natix/cvison/vsdkx/vsdkx-core.git#egg=vsdkx-core'
    ],
    install_requires=[
        'vsdkx-core',
        'numpy>=1.18.5',
    ],
    version='1.0',
)
