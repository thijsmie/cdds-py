from distutils.core import setup


setup(
    name='testtopics',
    version='0.1',
    description='Cyclone DDS Python testtopics',
    author='Thijs Miedema',
    author_email='thijs.miedema@adlinktech.com',
    packages=['testtopics'],
    package_dir={'testtopics': 'testtopics/'},
)
