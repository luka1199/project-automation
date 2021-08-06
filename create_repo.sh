#!/bin/bash
if [[ $# -eq 0 ]] ; then
    echo 'No arguments'
    exit 1
fi
cd $2
git init
git add README.md
git add .gitignore
git commit -m "First commit"
git remote add origin https://github.com/$3/$1.git
git push -u origin master
code .