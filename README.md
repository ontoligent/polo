# Polo

## Synopsis

The first thing to do is grab the source code from git hub and clone
it into a local directory. You can call it anything but `polo_root` is
a good choice. Change directories into the cloned code base and edit
the file `config-play.ini`. 
```
git clone git@github.com:ontoligent/polo.git polo_root
cd polo_root
vi config-play.ini
```
In the config file, add the values for your mallet installation and
the place where your Polo projects will level. The meaning and
strucutre of this directory will be explained below. Note that you
need to have mallet already installed on your system. However, its path
does not need to be in the environment; you can just put it in the
config file directly, for example like so:
```
[DEFAULT]
mallet_path: /usr/local/bin/mallet
projects_path: projects
```
In the 


