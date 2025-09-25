"""Installation script for the custom environments extension."""

from setuptools import find_packages, setup

# Installation operation
setup(
    name="my-environments",
    version="1.0.0",
    author="IsaacLab User",
    maintainer="IsaacLab User",
    url="https://github.com/isaac-sim/IsaacLab",
    description="Custom robot environments for IsaacLab",
    keywords=["robotics", "reinforcement learning"],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "isaaclab",
    ],
    extras_require={
        "rl": ["rsl_rl", "rl_games", "sb3_contrib"],
    },
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    zip_safe=False,
)