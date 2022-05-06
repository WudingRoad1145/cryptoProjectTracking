
   
import requests
import os
import json

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = "AAAAAAAAAAAAAAAAAAAAALPMcAEAAAAAOIg1pxrBcVshtZX7XV2yq6WTC08%3DioqoXMQbulkr5ePUuNsB7J9v7zwsEYylUFYsgt5Ghtx4TE9Oxf"


def create_url():
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    usernames = "usernames=yanffyy"
    user_fields = "user.fields=description,created_at"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    #url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    url = "https://api.twitter.com/2/users/by?usernames=yanffyy&user.fields=public_metrics"
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    #print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main():
    url = create_url()
    json_response = connect_to_endpoint(url)
    print(json_response)
    print(json_response["data"][0]["public_metrics"]["followers_count"])
    result = json.dumps(json_response, indent=4, sort_keys=True) # json.dumps turn dict into string
    print(result[0])


if __name__ == "__main__":
    main()