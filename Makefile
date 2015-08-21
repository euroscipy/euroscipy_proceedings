NAME=klemm_witherden

all: output/$(NAME)/paper.pdf

output/$(NAME)/paper.pdf: papers/$(NAME)/$(NAME).rst papers/$(NAME)/*.png
	./make_paper.sh papers/$(NAME)

clean:
	rm -rf output/$(NAME)
