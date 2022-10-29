from setuptools import setup, Extension
from os import environ

compiler = environ['cc'].split('\\')[-1]
print(compiler)

args = []
if compiler == 'gcc.exe':
    args = ['-ofast']
else:
    args = ["/O2", "/GS-", "/fp:fast", "/std:c++latest", "/Zc:strictStrings-"]


def main():
    setup(name="nostalgiaeraycasting",
          version="1.0.0",
          description="Python raycasting engine for pygame",
          author="Yvant2000",
          author_email="yvant2000@gmail.com",
          ext_modules=[
              Extension(
                  "nostalgiaeraycasting",
                  ["casting.cpp"],
                  extra_compile_args=args
              )
          ]
          )


if __name__ == "__main__":
    main()
