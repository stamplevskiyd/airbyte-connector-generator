# Partitioning

Partitioning is required if the records of a stream are grouped into buckets based on an attribute or parent resources that need to be queried separately to extract the records.

Sometimes records belonging to a single stream are partitioned into subsets that need to be fetched separately. In most cases, these partitions are a parent resource type of the resource type targeted by the connector. The partitioning feature can be used to configure your connector to iterate through all partitions. In API documentation, this concept can show up as mandatory parameters that need to be set on the path, query parameters or request body of the request.

Common API structures look like this:

- The [SurveySparrow API](https://developers.surveysparrow.com/rest-apis/response#getV3Responses) allows to fetch a list of responses to surveys. For the `/responses` endpoint, the id of the survey to fetch responses for needs to be specified via the query parameter `survey_id`. The API does not allow to fetch responses for all available surveys in a single request, there needs to be a separate request per survey. The surveys represent the partitions of the responses stream.
- The [Woocommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/#order-notes) includes an endpoint to fetch notes of webshop orders via the `/orders/<id>/notes` endpoint. The `<id>` placeholder needs to be set to the id of the order to fetch the notes for. The orders represent the partitions of the notes stream.

There are some cases that require multiple requests to fetch all records as well, but partitioning is not the right tool to configure these in the connector builder:

- If your records are spread out across multiple pages that need to be requested individually if there are too many records, use the Pagination feature.
- If your records are spread out over time and multiple requests are necessary to fetch all data (for example one request per day), use the Incremental sync feature.

## Dynamic and static partitioning

There are three possible sources for the partitions that need to be queried - the connector itself, supplied by the end user when configuring a Source based on the connector, or the API provides the list of partitions via another endpoint (for example the Woocommerce API also includes an `/orders` endpoint that returns all orders).

The first two options are a "static" form of partition routing (because the partitions won't change as long as the Airbyte configuration isn't changed). This can be achieved by configuring the Parameterized Requests component in the Connector Builder.

The API providing the partitions via one or multiple separate requests is a "dynamic" form of partitioning because the partitions can change any time. This can be achieved by configuring the Parent Stream partition component in the Connector Builder.

### Parameterized Requests

To configure static partitioning, enable the `Parameterized Requests` component. The following fields have to be configured:

- The "Parameter Values" can either be set to a list of strings, making the partitions part of the connector itself, or delegated to a user input so the end user configuring a Source based on the connector can control which partitions to fetch. When using "user input" mode for the parameter values, create a user input of type array and reference it as the value using the [placeholder](/platform/connector-development/config-based/understanding-the-yaml-file/reference#variables) value using `{{ config['<your chosen user input name>'] }}`
- The "Current Parameter Value Identifier" can be freely choosen and is the identifier of the variable holding the current parameter value. It can for example be used in the path of the stream using the `{{ stream_partition.<identifier> }}` syntax.
- The "Inject Parameter Value into outgoing HTTP Request" option allows you to configure how to add the current parameter value to the requests

#### Example

To enable static partitioning defined as part of the connector for the [SurveySparrow API](https://developers.surveysparrow.com/rest-apis/response#getV3Responses) responses, the Parameterized Requests component needs to be configured as following:

- "Parameter Values" are set to the list of survey ids to fetch
- "Current Parameter Value Identifier" is set to `survey` (this is not used for this example)
- "Inject Parameter Value into outgoing HTTP Request" is set to `request_parameter` for the field name `survey_id`

When parameter values were set to `123`, `456` and `789`, the following requests will be executed:

```
curl -X GET https://api.surveysparrow.com/v3/responses?survey_id=123
curl -X GET https://api.surveysparrow.com/v3/responses?survey_id=456
curl -X GET https://api.surveysparrow.com/v3/responses?survey_id=789
```

To enable user-configurable static partitions for the [Woocommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/#order-notes) order notes, the configuration would look like this:

- Set "Parameter Values" to "User input"
- In the "Value" input, click the user icon and create a new user input
- Name it `Order IDs`, set type to `array` and click create
- Set "Current Parameter Value Identifier" to `order`
- "Inject Parameter Value into outgoing HTTP Request" is disabled, because the order id needs to be injected into the path
- In the general section of the stream configuration, the "URL Path" is set to `/orders/{{ stream_partition.order }}/notes`

<iframe width="640" height="612" src="https://www.loom.com/embed/5a0b36e3269b4e548230013099a56983?sid=6a21bb0a-f351-4f13-ac7e-b29c91e17248" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

When Order IDs were set to `123`, `456` and `789` in the testing values, the following requests will be executed:

```
curl -X GET https://example.com/wp-json/wc/v3/orders/123/notes
curl -X GET https://example.com/wp-json/wc/v3/orders/456/notes
curl -X GET https://example.com/wp-json/wc/v3/orders/789/notes
```

### Parent Stream

To fetch the list of partitions (in this example surveys or orders) from the API itself, the "Parent Stream" component has to be used. It allows you to select another stream of the same connector to serve as the source for partitions to fetch. Each record of the parent stream is used as a partition for the current stream.

The following fields have to be configured to use the Parent Stream component:

- The "Parent Stream" defines the records of which stream should be used as partitions
- The "Parent Key" is the property on the parent stream record that should become the partition value (in most cases this is some form of id)
- The "Current Parent Key Value Identifier" can be freely choosen and is the identifier of the variable holding the current partition value. It can for example be used in the path of the stream using the `{{ stream_partition.<identifier> }}` [interpolation placeholder](/platform/connector-development/config-based/understanding-the-yaml-file/reference#variables).

#### Example

To enable dynamic partitioning for the [Woocommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/#order-notes) order notes, first an orders stream needs to be configured for the `/orders` endpoint to fetch a list of orders. Once this is done, the Parent Stream component for the responses stream has be configured like this:

- "Parent Key" is set to `id`
- "Current Parent Key Value Identifier" is set to `order`
- In the general section of the stream configuration, the "URL Path" is set to `/orders/{{ stream_partition.order }}/notes`

<iframe width="640" height="612" src="https://www.loom.com/embed/e10a9128d2d9461b999d3d278669cc20?sid=abc9a9a4-5608-4887-adcc-de83ccb73137" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

When triggering a sync, the connector will first fetch all records of the orders stream. The records will look like this:

```
{ "id": 123, "currency": "EUR", "shipping_total": "12.23", ... }
{ "id": 456, "currency": "EUR", "shipping_total": "45.56", ... }
{ "id": 789, "currency": "EUR", "shipping_total": "78.89", ... }
```

To turn a record into a partition value, the "parent key" is extracted, resulting in the partition values `123`, `456` and `789`. In turn, this results in the following requests to fetch the records of the notes stream:

```
curl -X GET https://example.com/wp-json/wc/v3/orders/123/notes
curl -X GET https://example.com/wp-json/wc/v3/orders/456/notes
curl -X GET https://example.com/wp-json/wc/v3/orders/789/notes
```

## Multiple partition routers

It is possible to configure multiple partitioning mechanisms on a single stream - if this is the case, all possible combinations of partition values are requested separately.

For example, the [Google Pagespeed API](https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed) allows to specify the URL and the "strategy" to run an analysis for. To allow a user to trigger an analysis for multiple URLs and strategies at the same time, two Parameterized Request lists can be used (one injecting the parameter value into the `url` parameter, one injecting it into the `strategy` parameter).

If a user configures the URLs `example.com` and `example.org` and the strategies `desktop` and `mobile`, then the following requests will be triggered

```
curl -X GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.com&strategy=desktop
curl -X GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.com&strategy=mobile
curl -X GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.org&strategy=desktop
curl -X GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.org&strategy=mobile
```

## Adding the partition value to the record

Sometimes it's helpful to attach the partition a record belongs to to the record itself so it can be used during analysis in the destination. This can be done using a transformation to add a field and the `{{ stream_partition.<identifier> }}` interpolation placeholder.

For example when fetching the order notes via the [Woocommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/#order-notes), the order id itself is not included in the note record, which means it won't be possible to associate which note belongs to which order:

```
{ "id": 999, "author": "Jon Doe", "note": "Great product!" }
```

However the order id can be added by taking the following steps:

- Making sure the "Current Parameter Value Identifier" is set to `order`
- Add an "Add field" transformation with "Path" `order_id` and "Value" `{{ stream_partition.order }}`

Using this configuration, the notes record looks like this:

```
{ "id": 999, "author": "Jon Doe", "note": "Great product!", "order_id": 123 }
```

## Custom parameter injection

Using the "Inject Parameter / Parent Key Value into outgoing HTTP Request" option in the Parameterized Requests and Parent Stream components works for most cases, but sometimes the API has special requirements that can't be handled this way:

- The API requires to add a prefix or a suffix to the actual value
- Multiple values need to be put together in a single parameter
- The value needs to be injected into the URL path
- Some conditional logic needs to be applied

To handle these cases, disable injection in the component and use the generic parameter section at the bottom of the stream configuration form to freely configure query parameters, headers and properties of the JSON body, by using jinja expressions and [available variables](/platform/connector-development/config-based/understanding-the-yaml-file/reference/#/variables). You can also use these variables (like `stream_partition`) as part of the URL path as shown in the Woocommerce example above.
