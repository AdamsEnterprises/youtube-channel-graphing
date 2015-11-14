# Test Plan

## ----------------------------


## Purpose:

To test correctness of important Features within the Youtube Graph script.

Such procedures include:
    Extracting critical information through the Youtube API.
    parsing and validating command line arguments.


## Environment:

Testing is to be conducted using a test script. 

## Features to Test:


## API

See [issue #35.](https://github.com/rask004/youtube-channel-graphing/issues/35)
    
- User Name extraction
    Given a URL to a youtube channel, extract the channel name or user name.

    * Modern Channel URLs

    * Exceptions
        - Malformed API request / object
        - non existent channel URL

- Featured Channel Extraction
    Given the URL of a youtube channel, extract all public featured channels of this channel as
    URLs.

    * No featured channels
    * 1 Featured channel
    * Several featured channels
    * Modern Channel URLs

    * Exceptions
        - Malformed API request / object
        - non existent channel URL


## Arguments

- parsing

    Test the parsed argument results are valid

    * combinations of valid arguments
    * combinations with invalid arguments.
    * combinations with missing optional arguments (defaults)

- initial id

    Validation of the initial channel id.

    * Valid id for a channel
    * Invalid (non-existent) id
    * null
    
- api key

    Validation of the supplied api key
    
    * Valid key
    * Invalid (non-existent) key
    * null

- degree

    Validation of the degree, as a positive integer.

    * > 1
    * 1
    * 0
    * -1

- filename

    Validation of the filename, appropriate to the system.

    * Valid
    * Invalid
    * null - default

- formatted data output

    See [issue #34.](https://github.com/rask004/youtube-channel-graphing/issues/34)

    Validation that if output is formatted a particular way, it is correct.

    * gexf: GEXF format
    * gml: GML format
    * yaml: YAML format
    * text: edge list format
    * none / null: edge list format


## Features to not test:

- Verbose message formats. May not be in the release version.

- scripting related to the CI Server.

- showing the graph in a diagram.

- incorrect number of required CLI arguments, and arguments in a form not accepted by parser.

- bad choices for verbosity or output formats - the arg parser will do this itself.

- creation and validation of google api objects - outside of scope.

- json data output - requires multidirectional graphs, not yet implemented.