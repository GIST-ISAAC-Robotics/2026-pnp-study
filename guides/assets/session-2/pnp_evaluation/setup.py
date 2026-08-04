from setuptools import find_packages, setup

package_name = 'pnp_evaluation'

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
    description='Minimal dummy server and action client for Session 2.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'dummy_pick_place_server = pnp_evaluation.dummy_pick_place_server:main',
            'scenario_runner = pnp_evaluation.scenario_runner:main',
        ],
    },
)
