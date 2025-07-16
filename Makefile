#!/usr/bin/make 
#+ Author Umar Ba <jUmarB@protonmail.com>  


#+The Generated  shared object files are placed in $(PYH2D_pkg) directory   
PYH2D_pkg:=PyH2D  # Name of the package  

CYFLAGS= --inplace  --build-lib=$(PYH2D_pkg)  
SRC=$(wildcard  src/*.pyx) 
GEN_C_SRC=$(SRC:.pyx=.c) 

PYH2D_pkg_so_modules=$(wildcard PyH2D/*.so) 

all:  build  clean init  
	$(info [PyH2D]  Autobuild Done)
	$(shell sleep 1) 
	init 

build:  setup.py  $(SRC)
	$(info  Building sources ... )
	@python3 $< build_ext  $(CYFLAGS)  -j 3   


init: $(PYH2D_pkg) $(PYH2D_pkg_so_modules)   
	$(info   Generating  __$@__.py in package directory  $^  )
	$(file > $</__$@__.py) $(foreach  0,$^,$(file >> $</__$@__.py,from .$(word 2,$(subst /, ,$(word 1,$(subst ., ,$(0) ))))  import  * )) 


.PHONY: build  clean mproper 

clean: 
	$(info Remove generated Shared Object )
	@rm  *.so  

mproper:  setup.py
	$(info  Restoring )
	@python3  $^  clean  --all 
	@rm  $(GEN_C_SRC) 
	@rm  -r $(PYH2D_pkg) 
