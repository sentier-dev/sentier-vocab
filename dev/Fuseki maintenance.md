# Fuseki maintenance

## Drop a graph

Graphs exist within a dataset.

To drop a graph, go to https://fuseki.d-d-s.ch/, and make a query. Change the endpoint to `/skosmos/update`. Then run:

`DROP GRAPH <https://vocab.sentier.dev/units/>;`

## Adding a graph

Scp the data to the server, and then run:

`./s-put http://localhost:3030/skosmos/data https://vocab.sentier.dev/graph_name/ filename.ttl`

You might need to install `s-put` locally; it isn't installed globally.

./s-put http://localhost:3030/skosmos/data https://vocab.sentier.dev/simapro/ simapro.supplemented.ttl

## Test if SimaPro units are installed

Run this query:

```
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX qudt: <http://qudt.org/schema/qudt/>

SELECT ?simapro ?qudt
FROM <https://vocab.sentier.dev/simapro/>
FROM <https://vocab.sentier.dev/units/>
WHERE {
    ?simapro a skos:Concept .
    ?simapro skos:inScheme <https://vocab.sentier.dev/simapro/> .
    ?simapro skos:exactMatch ?qudt .
    ?qudt a skos:Concept .
    ?qudt skos:inScheme <https://vocab.sentier.dev/units/> .
    FILTER (?simapro = <https://vocab.sentier.dev/simapro/unit/MJ>)
}
```
