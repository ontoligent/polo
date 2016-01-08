# Polo

## What It Is

Polo is basically a wrapper around MALLET's topic model utility to
make working with its output files easier. With Polo, you specify your
topic model parameters in a configuration file and then generate
results with a simple command - one much simpler than the one that
comes with MALLET. For example, instead of doing this:

```
usr/local/bin/mallet import-file --keep-sequence \
--output projects/demo/trials/default/corpus.mallet \
--input projects/demo/corpus/corpus.csv --remove-stopwords \
--extra-stopwords projects/demo/corpus/extra-stopwords.txt

/usr/local/bin/mallet train-topics --num-iterations 100 \
--optimize-interval 10 --num-topics 10 --word-topic-counts-file \ 
projects/demo/trials/default/model-word-topic-counts.txt \
--xml-topic-phrase-report
projects/demo/trials/default/model-topic-phrase-report.xml \
--num-top-words 10 \
--xml-topic-report projects/demo/trials/default/model-topic-report.xml \
--output-doc-topics projects/demo/trials/default/model-doc-topics.txt \
--input projects/demo/trials/default/corpus.mallet \
--output-topic-keys \
projects/demo/trials/default/model-topic-keys.txt --num-threads 1
```

You can just do this:

```
./play demo default
```

Or, if you wanted to change the number of topics:

```
./play demo default 100
```

And, you you want to mess with the number of iterations, just add the
new value after the number of topics:

```
./play demo default 100 1000
```

In fact, if you want to see how it works right now, issue the above
command in your Polo application root, assuming that (1) you have
MALLET installed, and two you have Python 3 installed with the usual
data science stack (including pandas). See **Requirements** for more
info.

In addition to making it easier to generate topic models, the
resulting files are converted into a single SQLite database file that
implements a simple and intuitive data model of the topic model. This
data model adds some extra data to the source data as well, such as
the topic entropy for each document. The database file may then be
copied anywhere and used for a variety of purposes, such as a resource
for an R or Python analytics session, or at the bottom of a stack for
an interactive web or desktop application for end users to explore.

Polo is so named because in the game of polo, players use
mallets. That's it.

## Getting Started

To get started using Polo, the first thing to do is grab the source
code from git hub and clone it into a local directory. You can call it
anything but `polo_root` is a good choice. Change directories into the
cloned code base and edit the file `config-play.ini`.

```
git clone
git@github.com:ontoligent/polo.git polo_root
cd polo_root
vi config-play.ini
```

In the config file, add the values for your mallet installation and
the place where your Polo projects will live. The meaning and
strucutre of this directory will be explained below. Note that you
need to have Mallet already installed on your system. (You can find
out how do that here -- http://mallet.cs.umass.edu.) However, its path
does not need to be in the environment; you can just put it in the
config file directly, for example like so:

```
[DEFAULT]
mallet_path: /usr/local/bin/mallet
projects_path: projects
```

This lets Polo know where MALLET is and where your source files
live. Of course, to use Polo, you need some source data -- a corpus
file against which to train a topic model along with an extra
stopwords file, plus some configuration information to tell MALLET how
to train the model. Polo organizes this information in the following
way:

```
projects\
	my_project\
		config.ini
		corpus\
			corpus.csv
			extra-stopwords.txt
		trials\
			trial1\
			trial2\
```

# Requirements

# More Explanation

This directory structure reflects the following assumptions:

* There is a **project directory** where all of your source data and
  generated output will live. By default, this directory lives in your
  Polo application root and is called `projects`. It is automatically
  created for you when you install Polo. The project directory
  contains **three resources**:

* A **corpus directory**, which contains your corpus files and extra
stopwords list. By convention, your corpus file is called `corpus.csv`
and is a comma delimmited file with three columns -- a unique document
ID, a label of some kind (which must be there, even if it is something
you have to make up), and the 'document' itself, which for a topic
model is just the unit of text you are analyzing, which may be a
paragraph or any other text segment, and not necessarily a
stand-alone document. The extra stopwords file is called
`extra-stopwords.txt` and contains stopwords beyond those used by
MALLET itself.

* A **trials durectory**, which contains subdirectories for each of
your topic model trials. Each time you want to run a trial, you create
a subdirectory -- say `trial1` -- and then put an entry for that trial
in the project's `config.ini` file (see next item), The trials
directory is where Polo will put your resulting SQLite database. You
will find it there 

* A **config.ini** file to define some things about your project and
specific parameters for each. The sample config file that Polo ships
with looks like this:

```
[DEFAULT]
title: Polo Demo
owner: foo@virignia.edu

[default]
num-topics: 60
num-top-words: 10
num-iterations: 1000
optimize-interval: 10
num-threads: 1
```

This file describes a project and a single trail called 'default'.

Once you have created a 

# Limitations

Some qualifications to the preceeding assumptions are:

* Polo only works with a CSV file for its corpus -- and not a
directory of files, as MALLET is capable of doing.

* You are responsible for creating the corpus file itself and putting
it into the `corpus` subdirectory. Right now, Polo provides no
utilities for creating this file, but since this is such an important
part of the process, I am probably going to add something to help in
this area.

* Polo uses MALLET's built in stopwords file and this can't be
  changed.  A future version of Polo will allow users to adjust this
  default setting.
