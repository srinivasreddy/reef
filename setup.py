from setuptools import find_packages, setup

with open("requirements.txt") as fd:
    install_requires = fd.read().splitlines()

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
    install_requires=install_requires,
)
