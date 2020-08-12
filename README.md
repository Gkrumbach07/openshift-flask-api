# Openshift Flask Api

This is a simple backend service that combines two api services into one easy to use api.

## Model Api
The first api is a model service in which you can make predictions off of a model. This backend is customized to use a solar prediction model. A source to image builder named [nachlass](https://github.com/Gkrumbach07/nachlass) is used to convert the model into a REST api. More information on the model iteself can be can be found at its [GitHub reop.](https://github.com/Gkrumbach07/solar_forecaster)

## Weather API
This is a third party api serice named ClimaCell. You can sign up fro free at https://www.climacell.co/pricing/. You will need to find your api key to be able to use this backend service.
