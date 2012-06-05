#!/bin/bash
for i in `find * | egrep "\.pyc$|\.py~$|\.pyc~$|\.bak$"` ; do rm -v ${i}; done

rm -vr debian/python-*
rm -vr debian/pycompat
rm -vr debian/compat
rm -vr debian/files
rm -vr debian/stamp-makefile-build
rm -vr python-build-stamp-*

rm -v test/zeobuilder
rm -vr test/output/*
rm -v test/*.so
rm -v test/zeobuilder_script.py
rm -v test/ZEOBUILDER-DIALOG-*

rm -v profile/zeobuilder

rm -v MANIFEST
rm -vr dist
rm -vr build

rm -vr doc/_build
