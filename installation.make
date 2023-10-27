.DEFAULT_GOAL = help
build-spot:
	@tar -xvf spot.tar.gz && cd dependencies && sudo dpkg -i libbddx-dev_2.11.6.0-1_amd64.deb libspot-dev_2.11.6.0-1_amd64.deb libbddx0_2.11.6.0-1_amd64.deb spot_2.11.6.0-1_amd64.deb libspot0_2.11.6.0-1_amd64.deb libspotltsmin0_2.11.6.0-1_amd64.deb libjs-mathjax_2.7.9+dfsg-1_all.deb libspotgen0_2.11.6.0-1_amd64.deb spot-doc_2.11.6.0-1_all.deb fonts-mathjax_2.7.9+dfsg-1_all.deb libjs-requirejs_2.3.6+ds-1_all.deb

build-meson:
	

help: # Show all commands
	@egrep -h '\s#\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'