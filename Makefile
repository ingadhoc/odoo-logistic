all: addons

design/logistic.xmi: design/logistic.zargo
	-echo "REBUILD logistic.xmi from logistic.zargo. I cant do it"

addons: logistic

logistic: design/logistic.uml
	xmi2oerp -r -i $< -t addons -v 2

clean:
	rm -rf addons/logistic/*
	sleep 1
	touch design/logistic.uml
