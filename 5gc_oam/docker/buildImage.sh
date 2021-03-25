#! /bin/bash

FOLDER=""
NAME=""
VERSION="latest"

buildImage()
{
    if [ "$NAME" = "" ]
    then
        exit
    fi

    if [ "$FOLDER" != "" ] && [ -d $FOLDER ]
    then
        cd $FOLDER && \
            docker build -t="iii5gc/$NAME:$VERSION" .
    else
        echo "Folder is mandatory argument!!"
        usage
    fi
}

usage()
{
    echo "usage: ./buildImage.sh [-n name] [-v version] [-f folder] [-l list]"
}

while [ "$1" != "" ]; do
    case $1 in
        -n | --name )           shift
                                NAME=$1
                                ;;
        -v | --version )        shift
                                VERSION=$1
                                ;;
        -f | --folder )         shift
                                FOLDER=$1
                                FOLDER=`cd $FOLDER; pwd`
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        -l | --list )           docker images 
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

buildImage
