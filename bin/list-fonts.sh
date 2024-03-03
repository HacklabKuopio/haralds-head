#!/usr/bin/env bash
for FONTS in `pyfiglet -l`; do echo $FONTS; pyfiglet $FONTS -f $FONTS; done;
