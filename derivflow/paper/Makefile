# Build the paper.  Written against tectonic (self-contained, downloads its own
# TeX packages on first run); any TeX distribution with amsmath/graphicx/
# hyperref/booktabs will do, e.g. `latexmk -pdf paper.tex`.
#
# Built and verified with: tectonic 0.15.0
# Result at the time of writing: 11 pages, no errors, no overfull boxes,
# no undefined references, all four figures embedded.

paper.pdf: paper.tex $(wildcard figs/*.pdf)
	tectonic -X compile paper.tex

check:
	python3 verify_paper_numbers.py

clean:
	rm -f paper.pdf paper.aux paper.log paper.out

.PHONY: check clean
