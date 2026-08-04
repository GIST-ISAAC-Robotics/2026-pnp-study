from setuptools import find_packages, setup

package_name = 'pnp_orchestrator'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='PNP Study',
    maintainer_email='student@example.com',
    description='Outer task orchestration skeleton for the pick-and-place study.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'orchestrator = pnp_orchestrator.orchestrator:main',
            'target_pose_monitor = pnp_orchestrator.target_pose_monitor:main',
        ],
    },
)
