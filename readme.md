# Growth Shares Connected Content Lookup
<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Growth Shares Connected Content Lookup](#growth-shares-connected-content-lookup)
	- [Summary](#summary)
	- [Configuration settings](#configuration-settings)
		- [Local configuration Example](#local-configuration-example)
	- [Deploying Locally](#deploying-locally)
		- [Curl Example](#curl-example)
	- [Example Usage](#example-usage)
		- [Result](#result)
	- [Heroku](#heroku)
		- [Deploying to Heroku](#deploying-to-heroku)
		- [Heroku Deplooy](#heroku-deplooy)
			- [App name](#app-name)
			- [Environment Variables](#environment-variables)
			- [Endpoint](#endpoint)
			- [Postgres DB](#postgres-db)
	- [Importing data to Postgres](#importing-data-to-postgres)
	- [Sample CSV](#sample-csv)

<!-- /TOC -->

## Summary
This is a basic python3 script using the [Falcon framework](https://falconframework.org/) to host a webhook endpoint for use with [Braze connected content](https://www.braze.com/docs/user_guide/personalization_and_dynamic_content/connected_content/).  The webhook will take `lookup key` and return a json to be used. See [example usage](#example-usage) for more details.

## Configuration settings
Configuration can be set as part of the environment, or loaded from a `.env` file locally under the `lookup` section.
The following is a list of the configuration settings used:

| Field | Type | Description |
|----|----|----|
|AUTHENTICATION | String (required) | HTTP Authorization Header, should start with Bearer. Use alphanumeric only to avoid issues. **DON'T use equal(=) signs.** |
|DB_SCHEMA | String (optional)| Database Schema, default `public`. |
|DB_TABLE | String (optional)| Database Table, default `lookup`.|
|DB_KEY_FIELD| String[200] (optional)| Table Lookup field, default `id`.  Default max size is `200` characters.|
|DB_VALUE_FIELD| String (optional)| Table Lookup value from key, default `value`.|
|DATABASE_URL| String (required) | Postgres connection string. Only required if run outside Heroku, ie locally. Heroku will auto fill this value. Change this after you provision Heroku app if you want to use a different Postgres db besides the one Heroku provisions. |

### Local configuration Example
When running locally without an preset environment variables, an `.env` will be loaded automatically. See [env_example](env_example).

```
[lookup]
AUTHENTICATION=Bearer YWJjO#123jE_yMw
DATABASE_URL=postgres://[username]:[password]@[localhost]:[5432]/[database]
DB_SCHEMA=public
DB_TABLE=bz_lookup
DB_KEY_FIELD=id
DB_VALUE_FIELD=value
```

## Deploying Locally
To test the endpoint locally, add a `.env` file to the root directory. See [env_example](env_example). Use [PSQL](https://www.postgresql.org/download/) locally or via Heroku.
* Ensure python3 is installed and run `pip3 install requirements.txt`.
  * virtualenv should be used if possible.
* Create the necessary PQSL connection, user and database
* Update the `.env` with the connection string.
* Create the necessary [table](#postgres-db).
  * `python3 ./deploy/db_init.py` can also be used to create the base table.
* Load the necessary [data](#importing-data-to-postgres).
* run gunicorn `gunicorn -b 0.0.0.0:8000 braze-lookup:api`
* [Postman](https://www.postman.com/downloads/) or curl can be used to test the endpoint

### Curl Example
```
curl --location --request GET 'localhost:8000/lookup?id=value5' \
--header 'Authorization: Bearer YWJjO#123jE_yMw'
```


## Example Usage
To use the webhook with [Braze connected content](https://www.braze.com/docs/user_guide/personalization_and_dynamic_content/connected_content/), make a connected content get call with the following:

* URL of the deploy endpoint. If using heroku, it'll be on `herokuapp.com`
* Point to the `lookup` endpoint
* Include a `Authorization` header with the `[AUTHORIZATION]` value
* A query param with the `[DB_KEY_FIELD]` and `lookup value`

```
{% connected_content 	
  https://[APP NAME].herokuapp.com/lookup?[DB_KEY_FIELD]={value}
  :headers {"Authorization":"[AUTHORIZATION]"}
  :content_type application/json
  :method get
  :save response %}
```

Example:
```
{% connected_content 	
  https://braze-lookup-test-deploy.herokuapp.com/lookup?id=value5
  :headers {"Authorization":"Bearer YWJjO#123jE_yMw"}
  :content_type application/json
  :method get :save response %}
```

### Result
If the record is found, then a json object with the `[DB_KEY_FIELD]` and `[DB_VALUE_FIELD]` will be returned:

```
{
  "[DB_KEY_FIELD]": "{key}",
  "[DB_VALUE_FIELD]": "{value}"
}
```

Example:
```
{
  "id":"value5",
  "value":"11"
}
```

`{{ response.value }}` should output `11`.

**Return values will be a string.**

If the return value needs to be a json object, then `json_parse` can be used to convert it to json for further process.

Example:
```
{
  "id":"json5",
  "value":"{\"offer\":\"marketing\",\"location\":"nyc"}"
}
```

```
{% assign resp_json =  response.value | json_parse %}
{{ resp_json.location }}
```

Should output `nyc`

**To convert to a number, using liquid assign with the `plus` filter ie `{% assign resp_num = resp_json.num | plus: 0 %}`**

## Heroku
[Heroku](https://dashboard.heroku.com/) can be use to host the webhook.

**Please be aware of any cost and limitation associated with using [Heroku](https://www.heroku.com/pricing).**


### Deploying to Heroku
Deploying of this repo can be done manually by using cloning this repo and using the [Heroku cli](https://devcenter.heroku.com/articles/heroku-cli) or by using the Heroku Deploy button to easily deploy this to Heroku.

### Heroku Deplooy
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy/?template=https://github.com/zzhaobraze/lookup-test)

#### App name
Enter a globally unique app name:
![App Name](/images/heroku_app_name.png)

#### Environment Variables
The only environment variable that needs to be added is the `AUTHENTICATION` value. The rest are optional.  See [config settings](#configuration-settings) for additional info.

* `AUTHENTICATION` - this will match the  `Authorization` header in connected content. Recommended to be alphanumeric. **DO NOT USE equal(=) sign**
  * Example: `Bearer YWJjO#123jE_yMw`

![Env Variables](/images/heroku_env_config.png)

#### Endpoint
If deploying via Heroku, the url will be `https://[APP NAME].herokuapp.com/lookup`.
The url can be also be found in your Heroku app, under `Settings` -> `Domain`


#### Postgres DB
If using Heroku Deploy, a DB will automatically be created with the `DB_TABLE` name in the `DB_SCHEMA` with the `key` and `value` columns. Otherwise the [Heroku Postgres](https://devcenter.heroku.com/categories/heroku-postgres) will need to be manually provision to the app, and the table manually created. For usage outside Heroku, the database will need to be manually created.

**Please be aware of any cost and limitation associated with using [PostgresDB with Heroku](https://devcenter.heroku.com/articles/heroku-postgres-plans).**


See [Post Deploy Script](deploy/db_init.py).

Example:
```
CREATE TABLE [DB_SCHEMA].[DB_TABLE] (
		[DB_KEY_FIELD] VARCHAR(200) PRIMARY KEY,
		[DB_VALUE_FIELD] VARCHAR
)
```

## Lookup Admin Tool
Adding and editing data in the lookup table can be done using the simple admin tool that can be found here [Braze Data Lookup Admin](https://github.com/zzhaobraze/lookup-admin) or manually using Postgres CLI or PGAdmin.

## Importing data to Postgres
Data import can be done via the Postgres CLI Copy
```
copy public.lookup (id, value) FROM './example_data.csv' DELIMITER ',' CSV HEADER QUOTE '\"' ESCAPE '\"';""
```

Or using [pgadmin](https://www.pgadmin.org/)

![pgadmin import tool](/images/pgadmin_popup.png)

![pgadmin import](/images/pgadmin_import.png)

![pgadmin import settings](/images/pgadmin_import_settings.png)

**Enable headers, and if importing from excel csv, Delimiter `,` with escape `"` or data may not be loaded correctly.**

## Sample CSV
See [example data](example_data.csv) for a data example.

## Benchmarking
See [example data](benchmark/)

### Sample Results
Sample local run with 20 workers, 50 threads and a sample size of 1000 gave an average response time of `341.700998ms` without caching.

Sample local run with 1000 workers, 100 threads and a sample size of 10000 gave an average response time of `1589.971138ms` without caching.

```
status,total duration(s), total counts, average response(ms)
200,7376.066533,9999,737.680421
```

