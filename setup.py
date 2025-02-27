# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2021, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
import os
import sys

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext

# Use the env var ATOM_DISABLE_FH4 to disable linking against VCRUNTIME140_1.dll

ext_modules = [
    Extension(
        "atom.catom",
        [
            "atom/src/atomlist.cpp",
            "atom/src/atomdict.cpp",
            "atom/src/atomset.cpp",
            "atom/src/atomref.cpp",
            "atom/src/catom.cpp",
            "atom/src/catommodule.cpp",
            "atom/src/defaultvaluebehavior.cpp",
            "atom/src/delattrbehavior.cpp",
            "atom/src/enumtypes.cpp",
            "atom/src/eventbinder.cpp",
            "atom/src/getattrbehavior.cpp",
            "atom/src/member.cpp",
            "atom/src/memberchange.cpp",
            "atom/src/methodwrapper.cpp",
            "atom/src/observerpool.cpp",
            "atom/src/postgetattrbehavior.cpp",
            "atom/src/postsetattrbehavior.cpp",
            "atom/src/postvalidatebehavior.cpp",
            "atom/src/propertyhelper.cpp",
            "atom/src/setattrbehavior.cpp",
            "atom/src/signalconnector.cpp",
            "atom/src/validatebehavior.cpp",
        ],
        include_dirs=["src"],
        language="c++",
    ),
    Extension(
        "atom.datastructures.sortedmap",
        ["atom/src/sortedmap.cpp"],
        include_dirs=["src"],
        language="c++",
    ),
]


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    c_opts = {
        "msvc": ["/EHsc"],
    }

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.debug = False

    def build_extensions(self):

        # Delayed import of cppy to let setup_requires install it if necessary
        import cppy

        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        for ext in self.extensions:
            ext.include_dirs.insert(0, cppy.get_include())
            ext.extra_compile_args = opts
            if sys.platform == "darwin":
                ext.extra_compile_args += ["-stdlib=libc++"]
                ext.extra_link_args += ["-stdlib=libc++"]
            if ct == "msvc" and os.environ.get("ATOM_DISABLE_FH4"):
                # Disable FH4 Exception Handling implementation so that we don't
                # require VCRUNTIME140_1.dll. For more details, see:
                # https://devblogs.microsoft.com/cppblog/making-cpp-exception-handling-smaller-x64/
                # https://github.com/joerick/cibuildwheel/issues/423#issuecomment-677763904
                ext.extra_compile_args.append("/d2FH4-")
        build_ext.build_extensions(self)


setup(
    packages=find_packages(exclude=["tests", "tests.*"]),
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
    package_data={"atom": ["py.typed", "*.pyi"]},
)
