.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide_addons.html
   This text does not appear on pypi or github. It is a comment.

buildout_helpers
=============================

Do you work with many buildouts? Are you suffering from keeping them all up to date to best practices? Is the output of buildout annotate not enough for you? Are you having trouble to keep your buildouts repoducible?
This package provide helpers that help you for each of these problems and maybe more!

Features
--------

- normalize_buildout:

    The tool sorts sections and the keys in each section alphabetically, also some special multi line values, like eggs.
    sources sections for mister developer get aligned by attributes, so muliple source checkouts with similar branches get identified more easily, because the branch value for each source checkout gets printed in the same column.
    Some special sections are alwyays at the end or the beginning.

- freeze:

  This tool downloads all buildout configurations and stores them locally. The buildout files get modified to link to the downloaded resources.
  Every downloaded resource has a header with information that allow freeze to update the resources!

- version_info:

  This tool is similar to the annotate command of buildout. But this tool only gives information about versions. For each package it shows the version buildout will use and what version other buildout files pin. If your buildout file masks newer versions from buildout files it extends, the versions are printed in red. So if you have some version pins and update to a newer Patch version of Plone, you can look for red printouts, these can give you hints to outdated version pins in your own config files.

Detailed features of normalize_buildout
---------------------------------------
normalize_buildout by default will replace the given config files in place.
It buildout files cannot be parsed no file will be modified.
It has a command line option for not changing the file and only reporting via exit code if the file is not normalized. This can easily be integrated in check tools or ci tools.

The script understands the special meaning of some sections and keys:

  - buildout section is always the first
  - versions, and sources section are always the last
  - recipe key is always first
  - eggs, and zcml values get sorted.
  - keys of sources entries get sorted, values get indented so that branch settings are all on the same column.
  - mr.developer options are grouped and separated from the other buildout options

Every sorting happens case insensitive.
Comments above sections and above keys get shuffled together with key or section.
You can document why you need to pin a specific version of a package and after normalization, the comment is still above the right version specifier.

Detailed features of freeze
---------------------------
Freeze downloads all external files to a directory external_buildouts.
All buildout files that reference these get their extends values updated to point to the local resources.

Every downloaded resource gets a special header. It warns you to modify the file and it contains the URL from which the resource was downloaded and the ETAG value.
Upon repeated invocation, we check, if the resource has actually been changed. So if servers responds with a 304, the resource will not be downloaded again.
This is important for heavy CI users, like the quaive project. They sometimes got throttled from github.

Detailed features of version_info
---------------------------------

Everything has been said in the general feature section already.

Installation
------------

You can install the package with pip or zc.buildout.

PIP::

    $ pip install buildout_helpers

Buildout::

   [buildout]

    ...
    [extras]
    recipe = zc.recipe.egg
    eggs =
        buildout_helpers


and then running "bin/buildout"

For use with CI we suggest to use a requirements.txt file with pip to install both buildout_helpers, a defined version of setuptools and zc.buildout.

Usage
-----

normalize_buildout
``````````````````

You can do three common action swith this command.

1. Check if config files are normalized (for CI)::

   $ normalize_buildout --check *.cfg etc/*.cfg versions/*.cfg

   This will either return nothing, or a warning that the buildout is not normalized. It will have a falsy return code for CI.

2. Normalize a config file in place::

   $ normalize_buildout buildout.cfg

   This will normalize the buildout file.

3. Read a config file from stdin and print it on stdout, useful in vim::

   :%!normalize_buildout -

   On failure, this command will print out the config file unmodified.

freeze
``````

Use freeze initially to download external resources.

    $ freeze buildout.cfg

This command makes new ways to work with buildout more easy to handle.
You can now easily put company wide default buildout files on a central server.
Without a helper like the freeze command, you must choose between two bad choices:

  - reference the config files directly.

    If you update your buildout files in such a way that each referencing project needs to be updated, you immediately broke them all. Without a CI system that triggers builds periodically, you might not even notice before you break a new buildout run on production

  - copy the config file into the project

    You know what happens, you never update the file and suddenly you have N best practices.

With freeze and a proper CI system you can get the advantages of both options without the disadvantes. Use freeze to have a local copy. On your CI system, have two tests. One normal one, and one that will run freeze before running buildout. This way you test if your current configuration works and if your current configuration would work with the latest up to date buildout files!

version_info
````````````

This command is helpful during project updates. If you want to update your Plone Site to the newest Plone Patch version, you reference the newest url from Plone, like `http://dist.plone.org/release/4.3.7/versions.cfg` and then you run the version_info command and look for version information printed in red. In these cases you might have to update or remove your own version pins.

Contribute
----------

- Issue Tracker: https://github.com/collective/buildout_helpers/issues
- Source Code: https://github.com/collective/buildout_helpers
