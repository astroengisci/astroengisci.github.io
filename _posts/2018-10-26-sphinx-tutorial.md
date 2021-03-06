---
layout: post
title: Sphinx Tutorial for OBU CS Club
---
# Setup Tasks

  1. Download `astroengisci/csclub-sphinx-demo` from GitHub
  2. Install the Sphinx package in Python according to the [installation
     tutorial](http://www.sphinx-doc.org/en/master/usage/installation.html).
  3. You're going to be using the terminal/command prompt in this 
     presentation. ***STAY CALM, EVERYTHING WILL BE ALRIGHT***
     
# Creating your Sphinx Documentation Build

  1. Create a `/docs` folder in the cloned repository
  2. Run `sphinx-quickstart` in the `docs` folder. You can use the
     default values for all except:
     - `autodoc` should be included (select `y`)
     - `viewcode` should be included (select `y`)
  3. Run `make html` or, on Windows, `./make.bat html`
  4. Edit `conf.py` to change the source path to the folder containing
     your project's actual code (`..` in this case)
  5. Make a new folder `ref` in `docs`
  6. In the `docs` folder, run `sphinx-apidoc .. -o ref`. This will
     automatically generate reference files for every Python module
     in `..` (the directory above the current one) and stuff them in
     `docs`.
  7. Add `ref/modules` to the table of contents in `index.rst`
  8. Rebuild the documentation.
  9. You're done!
  
# Other Fun Stuff

## Changing the theme
In `conf.py` change `html_theme` at (likely around line 79) to the
Sphinx theme of your choice.

## Autosummary tables

  1. Edit `conf.py` to include the `sphinx.ext.autosummary` extension.
  2. Edit `ref/modules.rst` to use the `.. autosummary::` directive
     rather than the `.. toctree::` directive. 
     - Add the `:toctree:` option to this directive. 
     - Remove the  `:maxdepth:` option.
