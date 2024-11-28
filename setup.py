from setuptools import setup, find_packages

setup(
    name="hermes-orm",
    version="0.1.0",
    description="A high-performance ORM for Python with support for migrations, relations, and caching.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Altxria Inc.",
    author_email="company@altxria.com",
    url="https://github.com/altxriainc/hermes",  # URL to your repository
    packages=find_packages(where="src"),  # Look for packages in the src directory
    package_dir={"": "src"},  # Map the root package directory to src
    install_requires=[
        "click>=8.0",
        "aiosqlite>=0.17",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
        ]
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "hermes=hermes.cli:cli",  # Entry point for the CLI
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    license="MIT",
    keywords="ORM Python SQL migrations relations caching",
    project_urls={
        "Bug Tracker": "https://github.com/altxriainc/hermes/issues",
        "Documentation": "https://github.com/altxriainc/hermes/wiki",
        "Source Code": "https://github.com/altxriainc/hermes",
    },
)
