# Test Plan


## API

    See [issue #35.](https://github.com/rask004/youtube-channel-graphing/issues/35)

- User Name extraction
    Given a URL to a youtube channel, extract the channel name or user name.

    * Legacy User URLs
    * Modern Channel URLs

    * Exceptions
        - Malformed API request
        - non existent channel URL

- Featured Channel Extraction
    Given the URL of a youtube channel, extract all public featured channels of this channel as
    (Channel Name , URL) tuples.

    * No featured channels
    * 1 Featured channel
    * Several featured channels
    * Legacy User URLs
    * Modern Channel URLs

    * Exceptions
        - Malformed API request
        - non existent channel URL


## Arguments

- initial URL

    Test the URL is valid.

    * Valid URL to a channel
    * Invalid (non-existent) URL
    * Valid URL but is not a channel
    * null

- degree

    Test the degree is a positive integer.

    * 1
    * 0
    * -1
    * float
    * string / non-integer

- filename

    Test the requested filename is a valid filename.

    * Valid
    * Invalid
    * null

- verbosity

    Test the verbosity level is a valid choice.
    Test the verbosity output is the correct format.
    Test there is no verbosity if not requested.

    * In range 1-4
    * outside range
    * 1: Error messages only
    * 2: Current Degree
    * 3: Current Degree, current user being processed, number of users processed.
    * 4: Suitable for Debugging (Date Time statements).
         Current Degree, current user being processed, number of users processed, associations found, URLs and Channel Names, initial URL and channel name.
    * Default case of 0 / null: No verbose statements

- formatted data output

    See [issue #34.](https://github.com/rask004/youtube-channel-graphing/issues/34)

    Test if an output format is specified, the output is actually in that format.
    Test if no output format is specified, the default test output is used.

    * gexf: GEXF format
    * gml: GML format
    * json: JSON format
    * yaml: YAML format
    * text: edge list format
    * none / null: edge list format

- show graph visually

    Test that a graph is shown visually, in a diagram, without errors.

    * No Exceptions
    ?


