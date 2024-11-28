from setuptools import setup, find_packages

setup(
    name="hermes",
    version="0.1.0",
    description="A high-performance ORM for Python with support for migrations, relations, and caching.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/hermes",  # Replace with your GitHub repo URL
    packages=find_packages(),
    install_requires=[
        "click>=8.0",       # CLI support
        "aiosqlite>=0.17",  # Async SQLite database access
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",   # For testing
            "black>=23.0",   # Code formatter
            "flake8>=6.0",   # Linter
        ]
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "hermes=src.cli:cli",  # Define the `hermes` command
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
        "Bug Tracker": "https://github.com/yourusername/hermes/issues",  # Replace with your issue tracker
        "Documentation": "https://github.com/yourusername/hermes/wiki",  # Replace with your documentation URL
        "Source Code": "https://github.com/yourusername/hermes",         # Replace with your repository URL
    },
)
