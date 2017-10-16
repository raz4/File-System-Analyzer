#!/bin/sh
.SILENT:

default:
	python3 script.py

dist:
	tar -cvf lab3b-704666892.tar.gz README script.py Makefile

clean:
	-rm -f lab3b_check.txt
