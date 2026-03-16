from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ttl-archival-service",
    version="1.0.0",
    author="Stellar Team",
    author_email="team@stellar.com",
    description="TTL-Aware Automated Archival Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stellar/ttl-archival-service",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "postgres": ["psycopg2-binary>=2.9.0"],
        "mysql": ["PyMySQL>=1.0.0"],
        "redis": ["redis>=5.0.1"],
    },
    entry_points={
        "console_scripts": [
            "ttl-archival=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["*.py"],
    },
)
