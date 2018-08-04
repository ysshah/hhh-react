from setuptools import setup

setup(
  entry_points={'console_scripts': ['hhh=hhh.hhh:main']},
  install_requires=['praw'],
  packages=["hhh"]
)
