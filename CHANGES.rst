Changelog
=========


1.0.0 (2016-03-01)
------------------

- This package is working well in production. No more betas.
  [do3cc]

- Change cmd line parameter for normalizer from -c to -C.
  --check is unchanged and should be prefered in CI configs.
  [do3cc]


1.0.0b5 (2015-12-16)
--------------------

- Slightly better error handling for normalize_buildout.
  [do3cc]

- Fixed an error in version info, not handling remote urls properly.
  [do3cc]

- Fixed an error in version info, extends order was backwards.
  [do3cc]

- Normalize now sorts case insensitive.
  [do3cc]

1.0.0b4 (2015-12-14)
--------------------

- Last release broke, I don't trust what is as 1.0.0b3 on pypi.
  [do3cc]


1.0.0b3 (2015-12-14)
--------------------

- Now normalize_buildouts accepts many config files in one run.
  [do3cc]


1.0.0b2 (2015-12-14)
--------------------

- Mostly refactor freeze command. Still hard to read and needs more love.
  [do3cc]


1.0.0b1 (2015-12-14)
--------------------

- Add freeze command, downloads all external buildout files, with
  headers that allow the same freeze command to update it.
  [do3cc]

- Add version info command that show which buildout file pins which
  version. Inspired from @jensens script
  [do3cc]

- Rename package to buildout_helpers. Namespace packages cause trobule
  with pip and buildout
  [do3cc]

0.3.0 (2015-09-22)
------------------

- Mr.developer variables in buildout sections are now separated
  and at the end of the buildout section
  [do3cc]

- Sources sections are at the end now
  [do3cc]

- Multiline options do not need an indent of 4 spaces, one is enough.
  Now this script correctly identifies them
  [do3cc]


0.2.0 (2015-09-11)
------------------

- Support piping.
  [do3cc]

- Remove unneeded dependency.
  [do3cc]

- Fix 3 bugs resulting in bad buildout.cfgs.
  [do3cc]


0.1 (2015-09-10)
----------------

- Initial release.
  [do3cc]
