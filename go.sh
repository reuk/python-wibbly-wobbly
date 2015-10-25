#!/bin/zsh

rm -rf build dist

if false; then
    #test
    python setup.py py2app -A
else
    #deploy
    python setup.py py2app
fi
