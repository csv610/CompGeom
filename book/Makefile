LATEX   = pdflatex
BIBTEX  = bibtex
MAKEIDX = makeindex
MAIN    = main

.PHONY: all clean

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex chapters/*.tex preamble.sty app_references.bib
	$(LATEX) $(MAIN)
	$(BIBTEX) $(MAIN)
	$(MAKEIDX) $(MAIN).idx
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)

clean:
	rm -f *.aux *.bbl *.blg *.idx *.ilg *.ind *.log *.out *.toc *.lof *.lot *.fdb_latexmk *.fls *.synctex.gz
