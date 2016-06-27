TEMPLATES = index.html projects.html blog.html misc.html
PREFIX = /var/www

.PHONY: all
all: directories $(TEMPLATES)

%.html: src/%.html
	@echo "[ ] Generating $< -> out/$@"
	@./preproc.py "$<" "out/$@"

clean:
	@rm -r out

directories:
	@echo "[ ] Making needed directories"
	@mkdir -p out
	@cp -r src/css out
	@cp -r src/data out

install:
	@echo "[ ] Installing to $(PREFIX)"
	@cp -r out/* $(PREFIX)

