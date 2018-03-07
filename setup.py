from setuptools import setup

setup(
    name='jupyterhub-ltiauthenticator',
    version='0.1a',
    description='LTI',
    license='Apache 2.0',
    tests_require = [
    'unittest2',
    ],
    test_suite = 'unittest2.collector',
    packages=['ltiauthenticator'],
    install_requires=[
        'jupyterhub',
        'python-jose',
        'oauthlib'

    ]
)
