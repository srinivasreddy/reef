from setuptools import find_packages, setup

setup(
    name="reef",
    version="0.0.2",
    url="https://srinivasreddy.dev",
    license="BSD",
    maintainer="Srinivas Reddy Thatiparthy",
    maintainer_email="thatiparthysreenivas@gmail.com",
    description=" A miniproject to test python and remote development skills.",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["Flask==1.1.1", "pandas==0.25.2", "requests==2.22.0"],
)
