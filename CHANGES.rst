Changelog
=========


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
