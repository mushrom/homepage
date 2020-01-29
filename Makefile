TEMPLATES  = src/index.html src/projects.html src/blog.html
TEMPLATES += src/misc.html
POSTS      = $(wildcard posts/post*.html)
OUTPUT     = $(patsubst src/%,   out/%, $(TEMPLATES))
OUTPUT    += $(patsubst posts/%, out/%, $(POSTS))

PREFIX = /var/www

.PHONY: all
all: directories $(OUTPUT)

out/%.html: src/%.html
	@echo "[ ] Generating $< -> $@"
	@./preproc.py "$<" "$@"

out/%.html: posts/%.html
	@echo "[ ] Generating $< -> $@"
	@./preproc.py "$<" "$@"

clean:
	@rm -r out

directories:
	@echo "[ ] Making needed directories"
	@mkdir -p out
	@cp -r src/css out
	@cp -rn src/data out

install:
	@echo "[ ] Installing to $(PREFIX)"
	@cp -r out/* $(PREFIX)

