#!/bin/sh
thispath=$(realpath .)

# generate figure for 7.4
latexmk $thispath/7.4.tex
# generate figure for 7.5
latexmk $thispath/7.5.tex
# generate figure for 7.6
latexmk $thispath/7.6.tex
# generate figures for 7.7 (figures not in paper)
# latexmk $thispath/7.7.tex
# generate table for 7.8
latexmk $thispath/7.8.tex
# generate table for 7.9
latexmk $thispath/7.9.tex