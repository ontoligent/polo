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

## Synopsis

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
This directory structure reflects the following assumptions:

* There is a **project directory** where all of your source data and
  generated output will live. By default, this directory lives in your
  Polo application root and is called `projects`. It is automatically
  created for you when you install Polo. The project directory
  contains **three resources**:

* A **corpus directory**, which contains your corpus files and extra
stopwords list. By convention, your corpus file is called `corpus.csv`
and it a comma delimmited file with three columns -- a document ID, a
label of some kind (which must be there, even if it is filler), and
the 'document' itself, which for a topic model is just the unit of
text you are analyzing, which may be a paragraph or any other segment
of text, and not necessarily a stand-alone document. The extra
stopwords file is called `extra-stopwords.txt` and contains stopwords
beyond those used by MALLET itself. (A future version of Polo will
allow users to adjust this default setting.)

* A **trials durectory**, which contains subdirectories for each of
your topic model trials. Each time you want to run a trial, you create
a subdirectory -- say `trial` -- and then put an entry for that trial
in the project's `config.ini` file.

* A **config.ini** file to define some things about your project and
specific parameters for each
