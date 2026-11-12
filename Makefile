SHELL := bash

.PHONY: all \
		fps fps-animation fps-frame fps-process fps-summary \
		quality

all: fps quality

fps: fps-animation fps-frame fps-process fps-summary

fps-animation:
	py -m fps.plot_frames animation

fps-frame:
	py -m fps.plot_frames frame

fps-process:
	py -m fps.plot_frames process

fps-summary:
	py -m fps.plot_summary

quality:
	py -m quality.plot