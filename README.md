# Polo

## What It Is

Polo is basically a wrapper around MALLET's topic model utility to
make working with its output files easier. With Polo, you specify your
topic model parameters in a configuration file and then generate
results with a simple command - one much simpler than the one that
comes with MALLET. For example, instead of doing this each time you
want to train a model against a corpus:

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

Or, if you want to change the number of topics:

```
./play demo default 100
```

If you want to mess with the number of iterations, just add the
new value after the number of topics:

```
./play demo default 100 1000
```

At the end of the process, you will see something like this:

```
--------------------------------------------------------------------------------
Enter the following to see your new database right away:
	sqlite3 projects/demo/trials/default/demo-default-z60-i1000.db
--------------------------------------------------------------------------------
```

If you want to see how it works right now, issue the above `play` command in
your Polo application root, assuming that (1) you have MALLET
installed and have entered its path into the `config-play.ini` file,
and (2) you have Python 3 installed. See **Requirements** for more
info.

In addition to making it easier to generate topic models, the
resulting files are converted into **a single SQLite database** file that
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
code from github and clone it into a local directory. You can call the directory
anything; `polo_root` is a good choice. Change directories into the
cloned code base and edit the file `config-play.ini` in your favorite editor:

```
git clone git@github.com:ontoligent/polo.git polo_root
cd polo_root
emacs config-play.ini
```

In the config file, add the values for your mallet installation and
the place where your Polo projects will live. The meaning and
strucutre of this directory will be explained below. Note that you
need to have MALLET already installed on your system. (You can find
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
to train the model.

Next, take some time to become familiar with how Polo organizes
things. Polo organizes your corpus data and output files in the
following way:

```
projects\
	demo\
		config.ini
		corpus\
			corpus.csv
			extra-stopwords.txt
		trials\
			default\
```

This is the directory structure of the demo corpus that comes with
Polo. To create your own project, just replicate this structure, add your
own contents, and then edit the config file to match your needs. The config
file that ships with Polo looks like this:

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

Polo's directory structure reflects the following assumptions:

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
paragraph or any other text segment, and not necessarily a stand-alone
document. The extra stopwords file is called `extra-stopwords.txt` and
contains stopwords beyond those used by MALLET itself. Note that the
stopwords file must exist, even if it is empty, and it must be named
as listed here. Ditto for the corpus file (although it better have
some content, right?)
* A **trials durectory**, which contains subdirectories for each of
your topic model trials. Each time you want to run a trial, you create
a subdirectory -- say `trial1` -- and then put an entry for that trial
in the project's `config.ini` file (see next item), The trials
directory is where Polo will put your resulting SQLite database.
* A **config.ini** file to define some things about your project and
specific parameters for each. Users of MALLET will recognize that the
keys in the trials section are just the command line keys for MALLET's
`train topics` function. Given this, you can add more keys if you'd
like. Note, however, that Polo takes care of defining the output
files, so you don't need to add these.

So, once you have create a project directory with a corpus and trials
directory, and added a corpus file and stopwords file to the former
and a trial directory to the latter, and you have created a
`config.ini` file for the project, you can start doing this:

`./play myproject mytrial`

Remember you can add arguments for number of topics and number of
iterations to this command if you want to override what's in the
config file.

After running this, the resulting SQLite file will be found in the trial directory, and
will be named as follows:

`myproject-mytrial-zX-iY.db`

Where 'myproject' is the name of your project, 'mytrial' is the name
of your trial, 'X' is the number of topics, and 'Y' is the number of
iterations.

Copy this file to wherever it can be useful. Think of it as a
portable, durable record of a specific topic model trial.

# Requirements

Polo requires the following;
* **MALLET**. I am using the latest version (as of 8 JAN
  2016) and I have no idea how much it has changed from the earlier
versions.
* **Python 3**. I am using 3.5 and import the following modules: `os, re,
configparser, sqlite3, codecs, collections, lxml, math`. I use the
Anaconda distribution and I believe that I had to install `lxml`
separately.

Also:
* Properly prepared corpus data.
* A machine that can run MALLET, especially if your corpus is really
big and you want to train lots of topics.

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
