.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide_addons.html
   This text does not appear on pypi or github. It is a comment.

collective.normalize_buildout
=============================

Do you have multiple buildouts and you want an easy way to apply new best practices to each buildout in a simple way, but you cannot, because every buildout file is configured slightly different?

Then this package is for you. The normalize_buildout is a script that will normalize your buildout file.

The tool sorts sections and the keys in each section alphabetically, also some special multi line values, like eggs.

Features
--------

normalize_buildout by default will replace the given config file in place.
It has a command line option for not changing the file and only reporting via exit code if the file is not normalized. This can easily be integrated in check tools or ci tools.

The script understands the special meaning of some sections and keys:

  - buildout section is always the first
  - versions, and sources section are always the last
  - recipe key is always first
  - eggs, and zcml values get sorted.
  - keys of sources entries get sorted, values get indented so that branch settings are all on the same column.
  - mr.developer options are grouped and separated from the other buildout options

Comments above sections and above keys get shuffled together with key or section.
You can document why you need to pin a specific version of a package and after normalization, the comment is still above the right version specifier.
- Can be bullet points


Installation
------------

You can install the package with pip or zc.buildout.

PIP::

    $ pip install collective.normalize_buildout

Buildout::

   [buildout]

    ...
    [extras]
    recipe = zc.recipe.egg
    eggs =
        collective.normalize_buildout


and then running "bin/buildout"

Usage
-----

You can do three things with this command.

1. Check if a config file is normalized (for CI)::

   $ normalize_buildout -c buildout.cfg

   This will either return nothing, or a warning that the buildout is not normalized. It will have a falsy return code for CI.

2. Normalize a config file in place::

   $ normalize_buildout buildout.cfg

   This will normalize the buildout file.

3. Read a config file from stdin and print it on stdout, useful in vim::

   :%!normalize_buildout -

   On failure, this command will print out the config file unmodified.

Contribute
----------

- Issue Tracker: https://github.com/collective/collective.normalize_buildout/issues
- Source Code: https://github.com/collective/collective.normalize_buildout
