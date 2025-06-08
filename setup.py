from setuptools import find_packages, setup

setup(
    name="pysql",
    version="0.1.0",
    description="Librería para pruebas SQL",
    author="Cano2908",
    author_email="c.cano2908@outlook.com",
    url="https://github.com/Cano2908/pysql",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["python-dotenv==1.0.1", "psycopg2-binary==2.9.10", "sqlmodel"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
