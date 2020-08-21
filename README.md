# Openshift Flask Api

This is a simple backend service that combines two api services into one easy to use api.

## Model Api
The first api is a model service in which you can make predictions off of a model. This backend is customized to use a solar prediction model. A source to image builder named [nachlass](https://github.com/Gkrumbach07/nachlass) is used to convert the model into a REST api. More information on the model iteself can be can be found at its [GitHub reop.](https://github.com/Gkrumbach07/solar_forecaster)

You can deploy the model with these commands.
```
oc new-app quay.io/gkrumbach07/nachless:latest-6~https://github.com/Gkrumbach07/solar_forecaster \
	--build-env S2I_SOURCE_NOTEBOOK_LIST=03-model-training.ipynb \
	--name=model

oc expose svc/model
```
Next take note of the model url that you just exposed. You can get this address by using the `oc get` command. To save the address for later commands, use the coomand bellow.
`MODEL_URL=http://$(oc get route/model -o jsonpath='{.spec.host}')`

## Weather API
This is a third party api service named ClimaCell. You can sign up for free at https://www.climacell.co/pricing/. You will need to find your api key to be able to use this backend service.

## Deployment
To run this on Openshift you can run this command in the CLI terminal. Notice we used `$MODEL_URL` variable name from the command we ran before.
```
oc new-app centos/python-36-centos7~https://github.com/Gkrumbach07/openshift-flask-api.git \
	-e API_KEY=D0nTsT3Almyk3y \
	-e REACT_APP_MODEL_URL=$MODEL_URL \
	--name=backend

oc expose svc/backend
```
