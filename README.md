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

The resulting files are converted into a single SQLite database file
that implements a simple and intuitive data model of the topic
model. This file may then be copied anywhere and used for a variety of
purposes, such as a resource for an R or Python analytics session, or
at the bottom of a stack for an interactive web or desktop application
for end users to explore.

Polo is so named because in the game of polo, players use
mallets. That's it.

## Synopsis

To get started using Polo, the first thing to do is grab the source
code from git hub and clone it into a local directory. You can call it
anything but `polo_root` is a good choice. Change directories into the
cloned code base and edit the file `config-play.ini`.

```
git clone
git@github.com:ontoligent/polo.git polo_root cd polo_root
vi config-play.ini
```

In the config file, add the values for your mallet installation and
the place where your Polo projects will live. The meaning and
strucutre of this directory will be explained below. Note that you
need to have Mallet already installed on your system. (You can find
out how do that here -- http://mallet.cs.umass.edu. However, its path
does not need to be in the environment; you can just put it in the
config file directly, for example like so:

```
[DEFAULT]
mallet_path: /usr/local/bin/mallet
projects_path: projects
```

In the


