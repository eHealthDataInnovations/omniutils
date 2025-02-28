import os

from setuptools import setup  # type: ignore


def read(file_path):
    with open(
        os.path.join(os.path.dirname(__file__), file_path),
        "r",
        encoding="utf-8",
    ) as rfile:
        return rfile.read()


setup(
    name="omniutils",
    version="0.1.0",
    description="Uma coleção de módulos utilitários para projetos diversos",
    long_description=read("README.md"),  # Lê diretamente do arquivo README.md
    long_description_content_type="text/markdown",
    author="Jailton Paiva",
    author_email="jailtoncarlos@gmail.com",
    keywords=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=read("requirements/requirements-packaging.txt"),
    # packages=find_packages(exclude=["tests*"]),
    url="https://github.com/eHealthDataInnovations/medication_framework",
    include_package_data=True,
    python_requires=">=3.10",
)
