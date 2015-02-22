# Instagram Incoming Webhook

## Hosts
* mongodb	127.0.0.1

## Environment Variables
* SENTRY_API_KEY

## Run
   
   docker run -p 8888:8888 --link mongodb/mongodb --rm --name instagram-incoming-webhook instagram-incoming-webhook