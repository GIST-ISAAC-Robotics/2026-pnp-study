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
    maintainer='pnp-study',
    maintainer_email='pnp-study@example.com',
    description='Session 1 target pose monitor',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'target_pose_monitor = pnp_orchestrator.target_pose_monitor:main',
        ],
    },
)
