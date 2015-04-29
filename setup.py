from setuptools import setup, find_packages

__version__ = "0.0.1"


setup(
    version=__version__,
    name="Ferment",
    description="A tool to provide the current docker config in ferm format",
    author="Oliver Berger",
    author_email="diefans@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    keywords="ferm docker iptables",
    license="Apache Version 2",
    package_dir={'': 'src'},
    packages=find_packages(
        "src",
        exclude=[]
    ),
    namespace_packages=["ferment"],
    include_package_data=True,
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    ferment = ferment.scripts:run
    """,
    install_requires=[
        "docker-py",
        "click",
        "wheezy.template",
    ],
)
