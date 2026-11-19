SHELL := bash

.PHONY: all \
		fps fps-no-tamper-detection fps-animation fps-frame fps-process fps-summary \
		quality \
		performance \
		clean \
		dashboard

all: fps quality

fps: fps-no-tamper-detection fps-animation fps-frame fps-process fps-summary

fps-no-tamper-detection:
	py -m fps.plot_frames no_tamper_detection

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

performance:
	py -m performance.plot

clean:
	rm -f fps/outputs/*.png quality/outputs/*.png

dashboard:
	streamlit run dashboard.py