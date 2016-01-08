# Polo

## What It Is

Polo is basically a wrapper around MALLET's topic model utility to
make working with its output files easier. With Polo, you specify your
topic model parameters in a configuration file and then generate
results with a simple command - one much simpler than the one that
comes with MALLET. The resulting files are converted into a single
SQLite database file that implements an simple and intuitive data
model of the topic model. This file can be copied anywhere and used
for a variety of purposes, such as a resource for an R or Python
analytics session, or at the bottom of a stack for an interactive web
or desktop application for end users to explore.

Polo is so named because in the game of polo, players use
mallets. That's it. 

## Synopsis

To get started using Polo, the first thing to do is grab the source
code from git hub and clone it into a local directory. You can call it
anything but `polo_root` is a good choice. Change directories into the
cloned code base and edit the file `config-play.ini`.  ``` git clone
git@github.com:ontoligent/polo.git polo_root cd polo_root vi
config-play.ini ``` In the config file, add the values for your mallet
installation and the place where your Polo projects will live. The
meaning and strucutre of this directory will be explained below. Note
that you need to have Mallet already installed on your system. (You
can find out how do that here -- http://mallet.cs.umass.edu. However,
its path does not need to be in the environment; you can just put it
in the config file directly, for example like so: ``` [DEFAULT]
mallet_path: /usr/local/bin/mallet projects_path: projects ``` In the


