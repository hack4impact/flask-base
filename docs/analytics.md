# Adding Analytics

## Google Analytics

Including Google analytics to your flask-base app is incredibly easy. Simply add an environment variable named `GOOGLE_ANALYTICS_ID` to a local file called `config.env`.

A Google analytics ID can be obtained by signing up [here](https://analytics.google.com/analytics/web). The ID should be of the form `UA-XXXXXX-X`.

For more information about using Google analytics, check out their [help center](https://support.google.com/analytics#topic=3544906).

## Segment
Including Segment to your flask-base app requires you to add an environment variable named `SEGMENT_API_KEY` to a local file called `config.env`.

To obtain a Segment API key, you will first need to [sign up](https://app.segment.com). Then, add a Javascript source and navigate to "Settings" to get a write key.

For more information about using Segment, check out their [help center](https://segment.com/help).
