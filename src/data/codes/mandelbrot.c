// public domain and whatever
// compile: gcc -lm -Ofast -o mandelbrot mandelbrot.c

#include <math.h>
#include <complex.h>
#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdlib.h>
#include <termios.h>
#include <stdint.h>
#include <sys/ioctl.h>

enum {
	UI_MODE_256_COLOR,
	UI_MODE_ASCII,
};

typedef struct ui_state {
	bool running;
	unsigned mode;
	unsigned color_sensitivity;

	double scale;
	double x_offset;
	double y_offset;

	double width;
	double height;
} ui_state_t;

#define MAX_STEPS ((2<<12))

long double complex iter(long double complex z, complex c) {
	return z*z + c;
}

unsigned escapes(complex foo) {
	long double complex z = 0;

	for (unsigned i = 0; i < MAX_STEPS; i++) {
		z = iter(z, foo);

		if (creal(z) > 2) {
			return i;
		}
	}

	return 0;
}

void draw_ascii(unsigned steps) {
	if (steps == 0) {
		putchar(' ');

	} else {
		unsigned foo = log2(steps);
		char *things = ".,'\"-+onm$#Q0BNM";
		putchar(things[foo]);
	}
}

void draw_256_colors(ui_state_t *state, unsigned steps) {
	if (steps == 0) {
		putchar(' ');

	} else {
		unsigned foo = log2(steps) * state->color_sensitivity;
		printf("\e[48;5;%dm \e[0m", foo + 16);
	}
}

struct termios og_termios;

void disable_raw() {
	tcsetattr(STDIN_FILENO, TCSAFLUSH, &og_termios);
}

void enable_raw(void) {
	tcgetattr(STDIN_FILENO, &og_termios);
	atexit(disable_raw);

	struct termios raw = og_termios;
	raw.c_lflag &= ~(ECHO | ICANON);
	tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
}

void init_ui(ui_state_t *state) {
	state->running = true;
	state->mode = UI_MODE_256_COLOR;
	state->color_sensitivity = 16;

	state->scale = 2;
	state->width = 80; 
	state->height = 40;

	state->x_offset = 0;
	state->y_offset = 0;
}

void get_console_size(ui_state_t *ui) {
	struct winsize size;
	ioctl(STDOUT_FILENO, TIOCGWINSZ, &size);
	ui->width = size.ws_col;
	ui->height = size.ws_row - 2;
}

void redraw(ui_state_t ui) {
	printf("\e[1;1H");
	for (int y = 0; y < ui.height; y++) {
		for (int x = 0; x < ui.width; x++) {
			complex c = (x / (ui.width/ui.scale/2) - ui.scale + ui.x_offset)
			          + (y / (ui.height/ui.scale/2) - ui.scale + ui.y_offset)*I;

			if (ui.mode == UI_MODE_256_COLOR) {
				draw_256_colors(&ui, escapes(c));

			} else {
				draw_ascii(escapes(c));
			}
		}

		putchar('\n');
	}

	int k = printf("-s %g -x %g -y %g", ui.scale, ui.x_offset, ui.y_offset);

	for (int i = 0; i < ui.width - k; i++) {
		putchar(' ');
	}

	putchar('\n');
}

void handle_input(ui_state_t *ui) {
	char c;
	if (read(STDIN_FILENO, &c, 1) == 1) {
		switch (c) {
			// horizontal movements
			case 'h':
				ui->x_offset -= ui->scale / 2;
				break;
			case 'l':
				ui->x_offset += ui->scale / 2;
				break;

			// vertical movements
			case 'j':
				ui->y_offset += ui->scale / 2;
				break;
			case 'k':
				ui->y_offset -= ui->scale / 2;
				break;

			// zoom in
			case 'K':
			case '+':
				ui->scale -= ui->scale/4;
				break;

			// zoom out
			case 'J':
			case '-':
				ui->scale += ui->scale/3;
				break;

			// quit
			case 'q':
			case 'Q':
				ui->running = false;
				break;

			// toggle ascii/256color modes
			case 'm':
			case 'M':
				ui->mode = !ui->mode;
				break;

			// reduce/increase color sensitivity in 256 color mode, effectively
			// changing the pallette
			case '[':
				if (ui->color_sensitivity > 0) {
					ui->color_sensitivity--;
				}
				break;

			case ']':
				ui->color_sensitivity++;
				break;

			// otherwise nothing to do
			default:
				break;
		}
	}
}

void print_help(void) {
	printf(
		"Usage: ./mandlebrot [-ach] [-x offset] [-y offset] [-s scale]\n"
		"                    [-W width] [-H height]\n"
		"    -a : Enable plain ascii drawing mode\n"
		"    -c : Enable 256 color mode (default)\n"
		"    -x : Initial x offset\n"
		"    -y : Initial y offset\n"
		"    -s : Scale, smaller is higher zoom\n"
		"    -W : Width of drawing space\n"
		"    -H : Height of drawing space\n"
		"    -h : Print this help and exit\n"
	);
}

int main(int argc, char *argv[]) {
	ui_state_t ui;

	init_ui(&ui);
	get_console_size(&ui);
	enable_raw();

	for (int opt; (opt = getopt(argc, argv, "hacx:y:s:W:H:")) != -1;) {
		switch (opt) {
			case 'a':
				ui.mode = UI_MODE_ASCII;
				break;

			case 'c':
				ui.mode = UI_MODE_256_COLOR;
				break;

			case 'x':
				ui.x_offset = atof(optarg);
				break;

			case 'y':
				ui.y_offset = atof(optarg);
				break;

			case 's':
				ui.scale = atof(optarg);
				break;

			case 'W':
				ui.width = atoi(optarg);
				break;

			case 'H':
				ui.height = atoi(optarg);
				break;

			case 'h':
				print_help();
				exit(0);
				break;

			default:
				print_help();
				exit(EXIT_FAILURE);
				break;
		}
	}

	while (ui.running) {
		redraw(ui);
		handle_input(&ui);
	}

	return 0;
}
